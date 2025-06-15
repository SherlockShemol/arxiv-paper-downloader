#!/usr/bin/env python3
"""
Enhanced configuration with additional options for better maintainability
"""

from pathlib import Path
from enum import Enum
from typing import Optional

class SortBy(Enum):
    """ArXiv API sort options"""
    RELEVANCE = "relevance"
    SUBMITTED_DATE = "submittedDate"
    LAST_UPDATED_DATE = "lastUpdatedDate"

class SortOrder(Enum):
    """Sort order options"""
    ASCENDING = "ascending"
    DESCENDING = "descending"

class EnhancedConfig:
    """Enhanced application configuration with additional options"""
    
    # Default configuration
    DEFAULT_DOWNLOAD_DIR = "~/Downloads/arxiv_papers"
    DEFAULT_QUERY = "cat:cs.AI"
    DEFAULT_MAX_RESULTS = 10
    
    # Search configuration
    DEFAULT_SORT_BY = SortBy.RELEVANCE  # Changed from submittedDate to relevance
    DEFAULT_SORT_ORDER = SortOrder.DESCENDING
    FALLBACK_SORT_BY = SortBy.SUBMITTED_DATE  # Fallback if relevance fails
    
    # File processing configuration
    MAX_FILENAME_LENGTH = 100
    REQUEST_DELAY = 1  # seconds
    API_TIMEOUT = 30   # seconds
    DOWNLOAD_TIMEOUT = 60  # seconds
    CHUNK_SIZE = 8192
    
    # Filename cleaning rules
    INVALID_CHARS_PATTERN = r'[<>:"/\\|?*]'
    WHITESPACE_PATTERN = r'\s+'
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 2  # exponential backoff base
    
    # Concurrency configuration
    MAX_CONCURRENT_DOWNLOADS = 5
    
    # Logging configuration
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # API Response validation
    EXPECTED_CONTENT_TYPES = ['application/atom+xml', 'text/xml']
    MIN_RESPONSE_LENGTH = 100  # Minimum expected response length
    
    # Cache configuration
    CACHE_EXPIRY_HOURS = 24  # Cache expiry time
    MAX_CACHE_SIZE_MB = 100  # Maximum cache size
    
    @classmethod
    def get_download_dir(cls, custom_dir: Optional[str] = None) -> Path:
        """Get download directory
        
        Args:
            custom_dir: Custom directory path
            
        Returns:
            Path object for download directory
        """
        if custom_dir:
            return Path(custom_dir).expanduser()
        return Path(cls.DEFAULT_DOWNLOAD_DIR).expanduser()
    
    @classmethod
    def get_cache_dir(cls, download_dir: Optional[str] = None) -> Path:
        """Get cache directory
        
        Args:
            download_dir: Base download directory
            
        Returns:
            Path object for cache directory
        """
        base_dir = cls.get_download_dir(download_dir)
        return base_dir / '.cache'
    
    @classmethod
    def get_log_dir(cls, download_dir: Optional[str] = None) -> Path:
        """Get log directory
        
        Args:
            download_dir: Base download directory
            
        Returns:
            Path object for log directory
        """
        base_dir = cls.get_download_dir(download_dir)
        return base_dir / 'logs'
    
    @classmethod
    def get_search_params(cls, sort_by: Optional[SortBy] = None, 
                         sort_order: Optional[SortOrder] = None) -> dict:
        """Get search parameters with fallback options
        
        Args:
            sort_by: Sort method
            sort_order: Sort order
            
        Returns:
            Dictionary with search parameters
        """
        return {
            'sortBy': (sort_by or cls.DEFAULT_SORT_BY).value,
            'sortOrder': (sort_order or cls.DEFAULT_SORT_ORDER).value
        }
    
    @classmethod
    def validate_response(cls, response) -> bool:
        """Validate API response
        
        Args:
            response: HTTP response object
            
        Returns:
            True if response is valid
        """
        if response.status_code != 200:
            return False
            
        content_type = response.headers.get('content-type', '').lower()
        if not any(ct in content_type for ct in cls.EXPECTED_CONTENT_TYPES):
            return False
            
        if len(response.text) < cls.MIN_RESPONSE_LENGTH:
            return False
            
        return True