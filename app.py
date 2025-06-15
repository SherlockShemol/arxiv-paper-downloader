#!/usr/bin/env python3
"""
Flask Web API for ArXiv Paper Downloader
提供论文搜索、下载和管理的Web API接口
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
CORS(app)  # 允许跨域请求

class DownloadManager(LoggerMixin):
    """下载管理器"""
    
    def __init__(self):
        self.downloads = {}  # 存储下载任务
        self.download_history = []  # 下载历史
        setup_logging()
    
    def add_download(self, paper_id: str, title: str, download_path: str) -> str:
        """添加下载任务"""
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
        """更新下载状态"""
        if download_id in self.downloads:
            self.downloads[download_id]['status'] = status
            if progress is not None:
                self.downloads[download_id]['progress'] = progress
            
            # 更新历史记录
            for item in self.download_history:
                if item['id'] == download_id:
                    item['status'] = status
                    if progress is not None:
                        item['progress'] = progress
                    break
    
    def get_download_status(self, download_id: str) -> Dict[str, Any]:
        """获取下载状态"""
        return self.downloads.get(download_id, {})
    
    def get_download_history(self) -> List[Dict[str, Any]]:
        """获取下载历史"""
        return self.download_history

# 全局实例
download_manager = DownloadManager()

def _validate_date_format(date_str: str) -> bool:
    """验证日期格式 YYYY-MM-DD"""
    try:
        from datetime import datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# 推荐关键词列表
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

@app.route('/api/papers/search', methods=['GET'])
def search_papers():
    """搜索论文"""
    try:
        # 获取搜索参数
        query = request.args.get('query', '')
        max_results = int(request.args.get('max_results', 10))
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # 验证日期格式
        if date_from and not _validate_date_format(date_from):
            return jsonify({'error': '日期格式错误，请使用YYYY-MM-DD格式'}), 400
        if date_to and not _validate_date_format(date_to):
            return jsonify({'error': '日期格式错误，请使用YYYY-MM-DD格式'}), 400
        
        if not query.strip():
            return jsonify({'error': '搜索关键词不能为空'}), 400
        
        # 创建下载器实例（使用临时目录进行搜索）
        downloader = ArxivDownloader()
        
        # 搜索论文
        papers = downloader.search_papers(
            query=query,
            date_from=date_from,
            date_to=date_to,
            max_results=max_results
        )
        
        # 转换为字典格式
        papers_data = []
        for paper in papers:
            paper_dict = {
                'id': paper.id,
                'title': paper.title,
                'authors': paper.authors,
                'summary': paper.abstract,
                'abstract': paper.abstract,  # 兼容前端
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
        app.logger.error(f"搜索论文失败: {str(e)}")
        return jsonify({'error': f'搜索失败: {str(e)}'}), 500

@app.route('/api/papers/download', methods=['POST'])
def download_paper():
    """下载论文"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        paper_id = data.get('paper_id')
        title = data.get('title', '')
        download_path = data.get('download_path')
        
        if not paper_id:
            return jsonify({'error': '论文ID不能为空'}), 400
        
        if not download_path:
            return jsonify({'error': '下载路径不能为空'}), 400
        
        # 确保下载目录存在
        ensure_directory(download_path)
        
        # 创建下载器实例
        downloader = ArxivDownloader(download_path)
        
        # 添加下载任务
        download_id = download_manager.add_download(paper_id, title, download_path)
        
        try:
            # 更新状态为下载中
            download_manager.update_download_status(download_id, 'downloading', 0)
            
            # 执行下载
            success = downloader.download_paper_by_id(paper_id)
            
            if success:
                download_manager.update_download_status(download_id, 'completed', 100)
                return jsonify({
                    'success': True,
                    'download_id': download_id,
                    'message': '下载成功'
                })
            else:
                download_manager.update_download_status(download_id, 'failed', 0)
                return jsonify({'error': '下载失败'}), 500
                
        except Exception as e:
            download_manager.update_download_status(download_id, 'failed', 0)
            raise e
        
    except Exception as e:
        app.logger.error(f"下载论文失败: {str(e)}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/downloads', methods=['GET'])
def get_downloads():
    """获取下载列表"""
    try:
        downloads = download_manager.get_download_history()
        return jsonify({
            'success': True,
            'downloads': downloads
        })
    except Exception as e:
        app.logger.error(f"获取下载列表失败: {str(e)}")
        return jsonify({'error': f'获取下载列表失败: {str(e)}'}), 500

@app.route('/api/downloads/<download_id>/status', methods=['GET'])
def get_download_status(download_id):
    """获取下载状态"""
    try:
        status = download_manager.get_download_status(download_id)
        if not status:
            return jsonify({'error': '下载任务不存在'}), 404
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        app.logger.error(f"获取下载状态失败: {str(e)}")
        return jsonify({'error': f'获取下载状态失败: {str(e)}'}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """获取系统设置"""
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
        app.logger.error(f"获取设置失败: {str(e)}")
        return jsonify({'error': f'获取设置失败: {str(e)}'}), 500

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
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
        app.logger.error(f"获取系统信息失败: {str(e)}")
        return jsonify({'error': f'获取系统信息失败: {str(e)}'}), 500

@app.route('/api/keywords/recommendations', methods=['GET'])
def get_keyword_recommendations():
    """获取推荐关键词"""
    try:
        return jsonify({
            'success': True,
            'keywords': RECOMMENDED_KEYWORDS
        })
    except Exception as e:
        app.logger.error(f"获取推荐关键词失败: {str(e)}")
        return jsonify({'error': f'获取推荐关键词失败: {str(e)}'}), 500

@app.route('/api', methods=['GET'])
def api_info():
    """API信息接口"""
    return jsonify({
        'message': 'ArXiv 论文下载器 API',
        'version': '1.0.0',
        'endpoints': {
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
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 设置日志
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("启动 ArXiv 论文下载器 Web API...")
    print("API 地址: http://localhost:5001")
    print("前端地址: http://localhost:3000")
    
    app.run(host='0.0.0.0', port=5001, debug=True)