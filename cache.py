"""缓存管理模块"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from config import Config
from models import Paper
from logger import LoggerMixin

class CacheManager(LoggerMixin):
    """缓存管理器"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录，如果为None则使用默认目录
        """
        if cache_dir is None:
            cache_dir = Config.get_cache_dir()
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存子目录
        self.paper_cache_dir = self.cache_dir / 'papers'
        self.search_cache_dir = self.cache_dir / 'searches'
        
        self.paper_cache_dir.mkdir(exist_ok=True)
        self.search_cache_dir.mkdir(exist_ok=True)
        
        self.log_info(f"缓存管理器初始化完成，缓存目录: {self.cache_dir}")
    
    def get_paper_info(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """从缓存获取论文信息
        
        Args:
            paper_id: 论文ID
        
        Returns:
            论文信息字典，如果不存在则返回None
        """
        cache_file = self.paper_cache_dir / f"{paper_id}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查缓存是否过期（7天）
            cached_time = datetime.fromisoformat(data.get('cached_at', '1970-01-01'))
            if datetime.now() - cached_time > timedelta(days=7):
                self.log_debug(f"论文 {paper_id} 缓存已过期")
                cache_file.unlink()
                return None
            
            self.log_debug(f"从缓存获取论文信息: {paper_id}")
            return data.get('paper_info')
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.log_warning(f"读取论文缓存失败 {paper_id}: {e}")
            # 删除损坏的缓存文件
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def save_paper_info(self, paper_id: str, paper_info: Dict[str, Any]) -> None:
        """保存论文信息到缓存
        
        Args:
            paper_id: 论文ID
            paper_info: 论文信息字典
        """
        cache_file = self.paper_cache_dir / f"{paper_id}.json"
        
        try:
            cache_data = {
                'paper_info': paper_info,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.log_debug(f"论文信息已缓存: {paper_id}")
            
        except Exception as e:
            self.log_warning(f"保存论文缓存失败 {paper_id}: {e}")
    
    def get_search_results(self, query_hash: str) -> Optional[list]:
        """从缓存获取搜索结果
        
        Args:
            query_hash: 查询哈希值
        
        Returns:
            搜索结果列表，如果不存在则返回None
        """
        cache_file = self.search_cache_dir / f"{query_hash}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查缓存是否过期（1小时）
            cached_time = datetime.fromisoformat(data.get('cached_at', '1970-01-01'))
            if datetime.now() - cached_time > timedelta(hours=1):
                self.log_debug(f"搜索结果缓存已过期: {query_hash}")
                cache_file.unlink()
                return None
            
            self.log_debug(f"从缓存获取搜索结果: {query_hash}")
            return data.get('results', [])
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.log_warning(f"读取搜索缓存失败 {query_hash}: {e}")
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def save_search_results(self, query_hash: str, results: list) -> None:
        """保存搜索结果到缓存
        
        Args:
            query_hash: 查询哈希值
            results: 搜索结果列表
        """
        cache_file = self.search_cache_dir / f"{query_hash}.json"
        
        try:
            cache_data = {
                'results': results,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.log_debug(f"搜索结果已缓存: {query_hash}")
            
        except Exception as e:
            self.log_warning(f"保存搜索缓存失败 {query_hash}: {e}")
    
    def clear_expired_cache(self) -> None:
        """清理过期缓存"""
        self.log_info("开始清理过期缓存")
        
        # 清理论文缓存（7天）
        paper_count = 0
        for cache_file in self.paper_cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                cached_time = datetime.fromisoformat(data.get('cached_at', '1970-01-01'))
                if datetime.now() - cached_time > timedelta(days=7):
                    cache_file.unlink()
                    paper_count += 1
                    
            except Exception:
                # 删除损坏的缓存文件
                cache_file.unlink()
                paper_count += 1
        
        # 清理搜索缓存（1小时）
        search_count = 0
        for cache_file in self.search_cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                cached_time = datetime.fromisoformat(data.get('cached_at', '1970-01-01'))
                if datetime.now() - cached_time > timedelta(hours=1):
                    cache_file.unlink()
                    search_count += 1
                    
            except Exception:
                cache_file.unlink()
                search_count += 1
        
        self.log_info(f"缓存清理完成，删除论文缓存: {paper_count}个，搜索缓存: {search_count}个")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        paper_count = len(list(self.paper_cache_dir.glob('*.json')))
        search_count = len(list(self.search_cache_dir.glob('*.json')))
        
        return {
            'paper_cache_count': paper_count,
            'search_cache_count': search_count
        }