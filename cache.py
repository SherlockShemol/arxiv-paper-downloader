"""Cache management module"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from config import Config
from models import Paper
from logger import LoggerMixin

class CacheManager(LoggerMixin):
    """Cache manager"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache manager
        
        Args:
            cache_dir: Cache directory, use default directory if None
        """
        if cache_dir is None:
            cache_dir = Config.get_cache_dir()
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache subdirectories
        self.paper_cache_dir = self.cache_dir / 'papers'
        self.search_cache_dir = self.cache_dir / 'searches'
        
        self.paper_cache_dir.mkdir(exist_ok=True)
        self.search_cache_dir.mkdir(exist_ok=True)
        
        self.log_info(f"Cache manager initialized, cache directory: {self.cache_dir}")
    
    def get_paper_info(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get paper information from cache
        
        Args:
            paper_id: Paper ID
        
        Returns:
            Paper information dictionary, None if not exists
        """
        cache_file = self.paper_cache_dir / f"{paper_id}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if cache is expired (7 days)
            cached_time = datetime.fromisoformat(data.get('cached_at', '1970-01-01'))
            if datetime.now() - cached_time > timedelta(days=7):
                self.log_debug(f"Paper {paper_id} cache expired")
                cache_file.unlink()
                return None
            
            self.log_debug(f"Retrieved paper info from cache: {paper_id}")
            return data.get('paper_info')
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.log_warning(f"Failed to read paper cache {paper_id}: {e}")
            # Delete corrupted cache file
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def save_paper_info(self, paper_id: str, paper_info: Dict[str, Any]) -> None:
        """Save paper information to cache
        
        Args:
            paper_id: Paper ID
            paper_info: Paper information dictionary
        """
        cache_file = self.paper_cache_dir / f"{paper_id}.json"
        
        try:
            cache_data = {
                'paper_info': paper_info,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.log_debug(f"Paper info cached: {paper_id}")
            
        except Exception as e:
            self.log_warning(f"Failed to save paper cache {paper_id}: {e}")
    
    def get_search_results(self, query_hash: str) -> Optional[list]:
        """Get search results from cache
        
        Args:
            query_hash: Query hash value
        
        Returns:
            Search results list, None if not exists
        """
        cache_file = self.search_cache_dir / f"{query_hash}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if cache is expired (1 hour)
            cached_time = datetime.fromisoformat(data.get('cached_at', '1970-01-01'))
            if datetime.now() - cached_time > timedelta(hours=1):
                self.log_debug(f"Search results cache expired: {query_hash}")
                cache_file.unlink()
                return None
            
            self.log_debug(f"Retrieved search results from cache: {query_hash}")
            return data.get('results', [])
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.log_warning(f"Failed to read search cache {query_hash}: {e}")
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def save_search_results(self, query_hash: str, results: list) -> None:
        """Save search results to cache
        
        Args:
            query_hash: Query hash value
            results: Search results list
        """
        cache_file = self.search_cache_dir / f"{query_hash}.json"
        
        try:
            cache_data = {
                'results': results,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.log_debug(f"Search results cached: {query_hash}")
            
        except Exception as e:
            self.log_warning(f"Failed to save search cache {query_hash}: {e}")
    
    def clear_expired_cache(self) -> None:
        """Clear expired cache"""
        self.log_info("Starting to clear expired cache")
        
        # Clear paper cache (7 days)
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
                # Delete corrupted cache files
                cache_file.unlink()
                paper_count += 1
        
        # Clear search cache (1 hour)
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
        
        self.log_info(f"Cache cleanup completed, deleted paper cache: {paper_count}, search cache: {search_count}")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        paper_count = len(list(self.paper_cache_dir.glob('*.json')))
        search_count = len(list(self.search_cache_dir.glob('*.json')))
        
        return {
            'paper_cache_count': paper_count,
            'search_cache_count': search_count
        }