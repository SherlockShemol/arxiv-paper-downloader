#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin System
Provides extensible pre and post download processing mechanisms
"""

import json
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from models import Paper
from logger import LoggerMixin
from config import Config

class DownloadPlugin(ABC):
    """Base class for download plugins"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
    
    @abstractmethod
    def pre_download(self, paper: Paper) -> bool:
        """Pre-download processing
        
        Args:
            paper: Paper object
        
        Returns:
            True to continue download, False to skip download
        """
        pass
    
    @abstractmethod
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """Post-download processing
        
        Args:
            paper: Paper object
            filepath: Downloaded file path
            success: Whether download was successful
        """
        pass
    
    def enable(self):
        """Enable plugin"""
        self.enabled = True
    
    def disable(self):
        """Disable plugin"""
        self.enabled = False

class DuplicateCheckPlugin(DownloadPlugin, LoggerMixin):
    """Duplicate check plugin"""
    
    def __init__(self, download_dir: Optional[Path] = None):
        super().__init__("duplicate_check")
        self.download_dir = download_dir or Config.get_download_dir()
        self.downloaded_papers: Set[str] = set()
        self.paper_hashes: Dict[str, str] = {}
        self._load_existing_papers()
    
    def _load_existing_papers(self):
        """Load existing papers"""
        if not self.download_dir.exists():
            return
        
        for pdf_file in self.download_dir.glob("*.pdf"):
            # Extract paper ID from filename
            filename = pdf_file.stem
            if '_' in filename:
                paper_id = filename.split('_')[0]
                self.downloaded_papers.add(paper_id)
        
        self.log_info(f"Loaded {len(self.downloaded_papers)} downloaded papers")
    
    def _calculate_paper_hash(self, paper: Paper) -> str:
        """Calculate paper content hash"""
        content = f"{paper.title}_{paper.abstract}_{','.join(paper.authors)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def pre_download(self, paper: Paper) -> bool:
        """Check if paper is duplicate"""
        # Check ID duplication
        if paper.id in self.downloaded_papers:
            self.log_info(f"Paper ID duplicate, skipping download: {paper.id}")
            return False
        
        # Check content duplication
        paper_hash = self._calculate_paper_hash(paper)
        if paper_hash in self.paper_hashes.values():
            self.log_info(f"Paper content duplicate, skipping download: {paper.id}")
            return False
        
        self.paper_hashes[paper.id] = paper_hash
        return True
    
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """Record downloaded paper"""
        if success:
            self.downloaded_papers.add(paper.id)
            self.log_info(f"Recorded downloaded paper: {paper.id}")

class CategoryFilterPlugin(DownloadPlugin, LoggerMixin):
    """Category filter plugin"""
    
    def __init__(self, allowed_categories: List[str] = None, 
                 blocked_categories: List[str] = None):
        super().__init__("category_filter")
        self.allowed_categories = set(allowed_categories or [])
        self.blocked_categories = set(blocked_categories or [])
    
    def pre_download(self, paper: Paper) -> bool:
        """Filter papers by category"""
        paper_categories = set(paper.categories)
        
        # Check if contains blocked categories
        if self.blocked_categories and paper_categories & self.blocked_categories:
            self.log_info(f"Paper contains blocked category, skipping download: {paper.id}")
            return False
        
        # Check if contains allowed categories
        if self.allowed_categories and not (paper_categories & self.allowed_categories):
            self.log_info(f"Paper does not contain allowed category, skipping download: {paper.id}")
            return False
        
        return True
    
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """Category filter plugin requires no post-processing"""
        pass

class MetadataPlugin(DownloadPlugin, LoggerMixin):
    """Metadata saving plugin"""
    
    def __init__(self, download_dir: Optional[Path] = None):
        super().__init__("metadata")
        self.download_dir = download_dir or Config.get_download_dir()
        self.metadata_dir = self.download_dir / '.metadata'
        self.metadata_dir.mkdir(exist_ok=True)
    
    def pre_download(self, paper: Paper) -> bool:
        """Metadata plugin does not affect download decision"""
        return True
    
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """Save paper metadata"""
        if not success:
            return
        
        metadata = {
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'pdf_url': paper.pdf_url,
            'published': paper.published,
            'categories': paper.categories,
            'download_time': datetime.now().isoformat(),
            'file_path': str(filepath),
            'file_size': filepath.stat().st_size if filepath.exists() else 0
        }
        
        metadata_file = self.metadata_dir / f"{paper.id}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        self.log_info(f"Saved metadata: {paper.id}")

class StatisticsPlugin(DownloadPlugin, LoggerMixin):
    """Statistics plugin"""
    
    def __init__(self, download_dir: Optional[Path] = None):
        super().__init__("statistics")
        self.download_dir = download_dir or Config.get_download_dir()
        self.stats_file = self.download_dir / '.stats.json'
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics data"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'total_downloads': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'categories': {},
            'authors': {},
            'daily_stats': {}
        }
    
    def _save_stats(self):
        """Save statistics data"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def pre_download(self, paper: Paper) -> bool:
        """Statistics plugin does not affect download decision"""
        return True
    
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """Update statistics data"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update overall statistics
        self.stats['total_downloads'] += 1
        if success:
            self.stats['successful_downloads'] += 1
        else:
            self.stats['failed_downloads'] += 1
        
        # Update category statistics
        for category in paper.categories:
            self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
        
        # Update author statistics
        for author in paper.authors:
            self.stats['authors'][author] = self.stats['authors'].get(author, 0) + 1
        
        # Update daily statistics
        if today not in self.stats['daily_stats']:
            self.stats['daily_stats'][today] = {'downloads': 0, 'successful': 0}
        
        self.stats['daily_stats'][today]['downloads'] += 1
        if success:
            self.stats['daily_stats'][today]['successful'] += 1
        
        self._save_stats()
        self.log_info(f"Updated statistics data: {paper.id}")

class PluginManager(LoggerMixin):
    """Plugin manager"""
    
    def __init__(self):
        self.plugins: List[DownloadPlugin] = []
    
    def register_plugin(self, plugin: DownloadPlugin):
        """Register plugin"""
        self.plugins.append(plugin)
        self.log_info(f"Registered plugin: {plugin.name}")
    
    def unregister_plugin(self, plugin_name: str):
        """Unregister plugin"""
        self.plugins = [p for p in self.plugins if p.name != plugin_name]
        self.log_info(f"Unregistered plugin: {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[DownloadPlugin]:
        """Get plugin"""
        for plugin in self.plugins:
            if plugin.name == plugin_name:
                return plugin
        return None
    
    def pre_download_hook(self, paper: Paper) -> bool:
        """Execute pre-download hooks for all plugins
        
        Returns:
            True to continue download, False to skip download
        """
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    if not plugin.pre_download(paper):
                        return False
                except Exception as e:
                    self.log_error(f"Plugin {plugin.name} execution failed: {str(e)}")
        return True
    
    def post_download_hook(self, paper: Paper, filepath: Path, success: bool):
        """Execute post-download hooks for all plugins"""
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin.post_download(paper, filepath, success)
                except Exception as e:
                    self.log_error(f"Plugin {plugin.name} execution failed: {str(e)}")
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins"""
        return [
            {
                'name': plugin.name,
                'enabled': plugin.enabled,
                'type': type(plugin).__name__
            }
            for plugin in self.plugins
        ]

# Predefined plugin configuration
def create_default_plugins(download_dir: Optional[Path] = None) -> PluginManager:
    """Create default plugin configuration"""
    manager = PluginManager()
    
    # Add default plugins
    manager.register_plugin(DuplicateCheckPlugin(download_dir))
    manager.register_plugin(MetadataPlugin(download_dir))
    manager.register_plugin(StatisticsPlugin(download_dir))
    
    return manager

if __name__ == "__main__":
    # Example usage
    manager = create_default_plugins()
    
    # Create example paper
    paper = Paper(
        id="2301.00001",
        title="Example Paper",
        authors=["Author 1", "Author 2"],
        abstract="This is an example abstract.",
        pdf_url="https://arxiv.org/pdf/2301.00001.pdf",
        published="2023-01-01",
        categories=["cs.AI", "cs.LG"]
    )
    
    # Execute plugin hooks
    should_download = manager.pre_download_hook(paper)
    print(f"Should download: {should_download}")
    
    if should_download:
        # Simulate download
        filepath = Path("/tmp/example.pdf")
        success = True
        manager.post_download_hook(paper, filepath, success)
    
    # List plugins
    plugins = manager.list_plugins()
    print(f"Registered plugins: {plugins}")