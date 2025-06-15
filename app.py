#!/usr/bin/env python3
"""
Flask Web API for ArXiv Paper Downloader
Provides Web API interface for paper search, download and management
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

from arxiv_downloader import ArxivDownloader
from models import Paper, DownloadStats
from logger import setup_logging, LoggerMixin
from config import Config
from utils import sanitize_filename, ensure_directory

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

class DownloadManager(LoggerMixin):
    """Download Manager"""
    
    def __init__(self):
        self.downloads = {}  # Store download tasks
        self.download_history = []  # Download history
        setup_logging()
    
    def add_download(self, paper_id: str, title: str, download_path: str) -> str:
        """Add download task"""
        download_id = f"download_{len(self.downloads) + 1}_{int(datetime.now().timestamp())}"
        
        download_info = {
            'id': download_id,
            'paper_id': paper_id,
            'title': title,
            'download_path': download_path,
            'status': 'pending',
            'progress': 0,
            'created_at': datetime.now().isoformat(),
            'file_size': 0
        }
        
        self.downloads[download_id] = download_info
        self.download_history.append(download_info.copy())
        
        return download_id
    
    def update_download_status(self, download_id: str, status: str, progress: int = None):
        """Update download status"""
        if download_id in self.downloads:
            self.downloads[download_id]['status'] = status
            if progress is not None:
                self.downloads[download_id]['progress'] = progress
            
            # Update history record
            for item in self.download_history:
                if item['id'] == download_id:
                    item['status'] = status
                    if progress is not None:
                        item['progress'] = progress
                    break
    
    def get_download_status(self, download_id: str) -> Dict[str, Any]:
        """Get download status"""
        return self.downloads.get(download_id, {})
    
    def get_download_history(self) -> List[Dict[str, Any]]:
        """Get download history"""
        return self.download_history

# Global instance
download_manager = DownloadManager()

def _validate_date_format(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD"""
    try:
        from datetime import datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Recommended keywords list
RECOMMENDED_KEYWORDS = [
    "machine learning",
    "deep learning",
    "neural networks",
    "computer vision",
    "natural language processing",
    "artificial intelligence",
    "reinforcement learning",
    "transformer",
    "attention mechanism",
    "generative adversarial networks",
    "convolutional neural networks",
    "recurrent neural networks",
    "transfer learning",
    "few-shot learning",
    "meta-learning",
    "graph neural networks",
    "self-supervised learning",
    "unsupervised learning",
    "supervised learning",
    "semi-supervised learning"
]

@app.route('/api/search', methods=['POST'])
@app.route('/api/papers/search', methods=['GET'])
def search_papers():
    """Search papers"""
    try:
        # Get search parameters from both GET args and POST JSON
        if request.method == 'POST':
            # Debug: log raw request data
            app.logger.info(f"POST request content type: {request.content_type}")
            app.logger.info(f"POST request data: {request.get_data()}")
            
            try:
                data = request.get_json(force=True) or {}
            except Exception as e:
                app.logger.error(f"JSON parsing error: {e}")
                # Try to get data from form if JSON fails
                data = request.form.to_dict() if request.form else {}
            
            query = data.get('query', '')
            max_results = int(data.get('max_results', 10))
            date_from = data.get('date_from')
            date_to = data.get('date_to')
        else:
            query = request.args.get('query', '')
            max_results = int(request.args.get('max_results', 10))
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
        
        # Validate date format
        if date_from and not _validate_date_format(date_from):
            return jsonify({'error': 'Invalid date format, please use YYYY-MM-DD format'}), 400
        if date_to and not _validate_date_format(date_to):
            return jsonify({'error': 'Invalid date format, please use YYYY-MM-DD format'}), 400
        
        if not query.strip():
            return jsonify({'error': 'Search query cannot be empty'}), 400
        
        # Create downloader instance (use temporary directory for search)
        downloader = ArxivDownloader()
        
        # Use enhanced search API with date range support
        from enhanced_arxiv_api import DateRange
        date_range = None
        if date_from or date_to:
            date_range = DateRange(
                start_date=date_from,
                end_date=date_to
            )
        
        # Search papers using enhanced API
        papers = downloader.search_papers_enhanced(
            query=query,
            date_range=date_range,
            max_results=max_results
        )
        
        # Convert to dictionary format
        papers_data = []
        for paper in papers:
            paper_dict = {
                'id': paper.id,
                'title': paper.title,
                'authors': paper.authors,
                'summary': paper.abstract,
                'abstract': paper.abstract,  # Frontend compatibility
                'published': paper.published if isinstance(paper.published, str) else paper.published,
                'updated': getattr(paper, 'updated', None),
                'categories': paper.categories,
                'pdf_url': paper.pdf_url,
                'arxiv_url': f"https://arxiv.org/abs/{paper.id}",
                'downloading': False
            }
            papers_data.append(paper_dict)
        
        return jsonify({
            'success': True,
            'papers': papers_data,
            'total': len(papers_data)
        })
        
    except Exception as e:
        app.logger.error(f"Paper search failed: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/papers/download', methods=['POST'])
def download_paper():
    """Download paper"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data cannot be empty'}), 400
        
        paper_id = data.get('paper_id')
        title = data.get('title', '')
        download_path = data.get('download_path')
        
        if not paper_id:
            return jsonify({'error': 'Paper ID cannot be empty'}), 400
        
        if not download_path:
            return jsonify({'error': 'Download path cannot be empty'}), 400
        
        # Ensure download directory exists
        ensure_directory(download_path)
        
        # Create downloader instance
        downloader = ArxivDownloader(download_path)
        
        # Add download task
        download_id = download_manager.add_download(paper_id, title, download_path)
        
        try:
            # Update status to downloading
            download_manager.update_download_status(download_id, 'downloading', 0)
            
            # Execute download
            success = downloader.download_paper_by_id(paper_id)
            
            if success:
                download_manager.update_download_status(download_id, 'completed', 100)
                return jsonify({
                    'success': True,
                    'download_id': download_id,
                    'message': 'Download successful'
                })
            else:
                download_manager.update_download_status(download_id, 'failed', 0)
                return jsonify({'error': 'Download failed'}), 500
                
        except Exception as e:
            download_manager.update_download_status(download_id, 'failed', 0)
            raise e
        
    except Exception as e:
        app.logger.error(f"Paper download failed: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/downloads', methods=['GET'])
def get_downloads():
    """Get download list"""
    try:
        downloads = download_manager.get_download_history()
        return jsonify({
            'success': True,
            'downloads': downloads
        })
    except Exception as e:
        app.logger.error(f"Failed to get download list: {str(e)}")
        return jsonify({'error': f'Failed to get download list: {str(e)}'}), 500

@app.route('/api/downloads/<download_id>/status', methods=['GET'])
def get_download_status(download_id):
    """Get download status"""
    try:
        status = download_manager.get_download_status(download_id)
        if not status:
            return jsonify({'error': 'Download task does not exist'}), 404
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        app.logger.error(f"Failed to get download status: {str(e)}")
        return jsonify({'error': f'Failed to get download status: {str(e)}'}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    try:
        settings = {
            'default_download_path': str(Path.home() / 'Downloads' / 'ArXiv_Papers'),
            'max_results': 50,
            'timeout': 30,
            'retry_count': 3
        }
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        app.logger.error(f"Failed to get settings: {str(e)}")
        return jsonify({'error': f'Failed to get settings: {str(e)}'}), 500

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """Get system information"""
    try:
        info = {
            'version': '1.0.0',
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            'platform': os.name,
            'current_time': datetime.now().isoformat()
        }
        return jsonify({
            'success': True,
            'info': info
        })
    except Exception as e:
        app.logger.error(f"Failed to get system information: {str(e)}")
        return jsonify({'error': f'Failed to get system information: {str(e)}'}), 500

@app.route('/api/keywords/recommendations', methods=['GET'])
def get_keyword_recommendations():
    """Get recommended keywords"""
    try:
        return jsonify({
            'success': True,
            'keywords': RECOMMENDED_KEYWORDS
        })
    except Exception as e:
        app.logger.error(f"Failed to get recommended keywords: {str(e)}")
        return jsonify({'error': f'Failed to get recommended keywords: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'ArXiv Paper Downloader API'
    })

@app.route('/api', methods=['GET'])
def api_info():
    """API information interface"""
    return jsonify({
        'message': 'ArXiv Paper Downloader API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'search': '/api/papers/search',
            'download': '/api/papers/download',
            'downloads': '/api/downloads',
            'download_status': '/api/downloads/<download_id>/status',
            'settings': '/api/settings',
            'system_info': '/api/system/info',
            'keyword_recommendations': '/api/keywords/recommendations'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Setup logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Starting ArXiv Paper Downloader Web API...")
    print("API URL: http://localhost:5002")
    print("Frontend URL: http://localhost:3000")
    
    app.run(host='0.0.0.0', port=5002, debug=False)