#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件系统
提供可扩展的下载前后处理机制
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
    """下载插件基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
    
    @abstractmethod
    def pre_download(self, paper: Paper) -> bool:
        """下载前处理
        
        Args:
            paper: 论文对象
        
        Returns:
            True继续下载，False跳过下载
        """
        pass
    
    @abstractmethod
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """下载后处理
        
        Args:
            paper: 论文对象
            filepath: 下载的文件路径
            success: 下载是否成功
        """
        pass
    
    def enable(self):
        """启用插件"""
        self.enabled = True
    
    def disable(self):
        """禁用插件"""
        self.enabled = False

class DuplicateCheckPlugin(DownloadPlugin, LoggerMixin):
    """重复检查插件"""
    
    def __init__(self, download_dir: Optional[Path] = None):
        super().__init__("duplicate_check")
        self.download_dir = download_dir or Config.get_download_dir()
        self.downloaded_papers: Set[str] = set()
        self.paper_hashes: Dict[str, str] = {}
        self._load_existing_papers()
    
    def _load_existing_papers(self):
        """加载已存在的论文"""
        if not self.download_dir.exists():
            return
        
        for pdf_file in self.download_dir.glob("*.pdf"):
            # 从文件名提取论文ID
            filename = pdf_file.stem
            if '_' in filename:
                paper_id = filename.split('_')[0]
                self.downloaded_papers.add(paper_id)
        
        self.log_info(f"加载了 {len(self.downloaded_papers)} 个已下载论文")
    
    def _calculate_paper_hash(self, paper: Paper) -> str:
        """计算论文内容哈希"""
        content = f"{paper.title}_{paper.abstract}_{','.join(paper.authors)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def pre_download(self, paper: Paper) -> bool:
        """检查是否为重复论文"""
        # 检查ID重复
        if paper.id in self.downloaded_papers:
            self.log_info(f"论文ID重复，跳过下载: {paper.id}")
            return False
        
        # 检查内容重复
        paper_hash = self._calculate_paper_hash(paper)
        if paper_hash in self.paper_hashes.values():
            self.log_info(f"论文内容重复，跳过下载: {paper.id}")
            return False
        
        self.paper_hashes[paper.id] = paper_hash
        return True
    
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """记录下载的论文"""
        if success:
            self.downloaded_papers.add(paper.id)
            self.log_info(f"记录已下载论文: {paper.id}")

class CategoryFilterPlugin(DownloadPlugin, LoggerMixin):
    """分类过滤插件"""
    
    def __init__(self, allowed_categories: List[str] = None, 
                 blocked_categories: List[str] = None):
        super().__init__("category_filter")
        self.allowed_categories = set(allowed_categories or [])
        self.blocked_categories = set(blocked_categories or [])
    
    def pre_download(self, paper: Paper) -> bool:
        """根据分类过滤论文"""
        paper_categories = set(paper.categories)
        
        # 检查是否包含被阻止的分类
        if self.blocked_categories and paper_categories & self.blocked_categories:
            self.log_info(f"论文包含被阻止的分类，跳过下载: {paper.id}")
            return False
        
        # 检查是否包含允许的分类
        if self.allowed_categories and not (paper_categories & self.allowed_categories):
            self.log_info(f"论文不包含允许的分类，跳过下载: {paper.id}")
            return False
        
        return True
    
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """分类过滤插件无需后处理"""
        pass

class MetadataPlugin(DownloadPlugin, LoggerMixin):
    """元数据保存插件"""
    
    def __init__(self, download_dir: Optional[Path] = None):
        super().__init__("metadata")
        self.download_dir = download_dir or Config.get_download_dir()
        self.metadata_dir = self.download_dir / '.metadata'
        self.metadata_dir.mkdir(exist_ok=True)
    
    def pre_download(self, paper: Paper) -> bool:
        """元数据插件不影响下载决策"""
        return True
    
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """保存论文元数据"""
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
        
        self.log_info(f"保存元数据: {paper.id}")

class StatisticsPlugin(DownloadPlugin, LoggerMixin):
    """统计插件"""
    
    def __init__(self, download_dir: Optional[Path] = None):
        super().__init__("statistics")
        self.download_dir = download_dir or Config.get_download_dir()
        self.stats_file = self.download_dir / '.stats.json'
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict[str, Any]:
        """加载统计数据"""
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
        """保存统计数据"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def pre_download(self, paper: Paper) -> bool:
        """统计插件不影响下载决策"""
        return True
    
    def post_download(self, paper: Paper, filepath: Path, success: bool) -> None:
        """更新统计数据"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 更新总体统计
        self.stats['total_downloads'] += 1
        if success:
            self.stats['successful_downloads'] += 1
        else:
            self.stats['failed_downloads'] += 1
        
        # 更新分类统计
        for category in paper.categories:
            self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
        
        # 更新作者统计
        for author in paper.authors:
            self.stats['authors'][author] = self.stats['authors'].get(author, 0) + 1
        
        # 更新日期统计
        if today not in self.stats['daily_stats']:
            self.stats['daily_stats'][today] = {'downloads': 0, 'successful': 0}
        
        self.stats['daily_stats'][today]['downloads'] += 1
        if success:
            self.stats['daily_stats'][today]['successful'] += 1
        
        self._save_stats()
        self.log_info(f"更新统计数据: {paper.id}")

class PluginManager(LoggerMixin):
    """插件管理器"""
    
    def __init__(self):
        self.plugins: List[DownloadPlugin] = []
    
    def register_plugin(self, plugin: DownloadPlugin):
        """注册插件"""
        self.plugins.append(plugin)
        self.log_info(f"注册插件: {plugin.name}")
    
    def unregister_plugin(self, plugin_name: str):
        """注销插件"""
        self.plugins = [p for p in self.plugins if p.name != plugin_name]
        self.log_info(f"注销插件: {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[DownloadPlugin]:
        """获取插件"""
        for plugin in self.plugins:
            if plugin.name == plugin_name:
                return plugin
        return None
    
    def pre_download_hook(self, paper: Paper) -> bool:
        """执行所有插件的下载前钩子
        
        Returns:
            True继续下载，False跳过下载
        """
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    if not plugin.pre_download(paper):
                        return False
                except Exception as e:
                    self.log_error(f"插件 {plugin.name} 执行失败: {str(e)}")
        return True
    
    def post_download_hook(self, paper: Paper, filepath: Path, success: bool):
        """执行所有插件的下载后钩子"""
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin.post_download(paper, filepath, success)
                except Exception as e:
                    self.log_error(f"插件 {plugin.name} 执行失败: {str(e)}")
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件"""
        return [
            {
                'name': plugin.name,
                'enabled': plugin.enabled,
                'type': type(plugin).__name__
            }
            for plugin in self.plugins
        ]

# 预定义插件配置
def create_default_plugins(download_dir: Optional[Path] = None) -> PluginManager:
    """创建默认插件配置"""
    manager = PluginManager()
    
    # 添加默认插件
    manager.register_plugin(DuplicateCheckPlugin(download_dir))
    manager.register_plugin(MetadataPlugin(download_dir))
    manager.register_plugin(StatisticsPlugin(download_dir))
    
    return manager

if __name__ == "__main__":
    # 示例用法
    manager = create_default_plugins()
    
    # 创建示例论文
    paper = Paper(
        id="2301.00001",
        title="Example Paper",
        authors=["Author 1", "Author 2"],
        abstract="This is an example abstract.",
        pdf_url="https://arxiv.org/pdf/2301.00001.pdf",
        published="2023-01-01",
        categories=["cs.AI", "cs.LG"]
    )
    
    # 执行插件钩子
    should_download = manager.pre_download_hook(paper)
    print(f"是否应该下载: {should_download}")
    
    if should_download:
        # 模拟下载
        filepath = Path("/tmp/example.pdf")
        success = True
        manager.post_download_hook(paper, filepath, success)
    
    # 列出插件
    plugins = manager.list_plugins()
    print(f"已注册插件: {plugins}")