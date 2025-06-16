"""Configuration management module"""

from pathlib import Path

class Config:
    """Application configuration class"""
    
    # Default configuration
    DEFAULT_DOWNLOAD_DIR = "~/Downloads/arxiv_papers"
    DEFAULT_QUERY = "cat:cs.AI"
    DEFAULT_MAX_RESULTS = 10
    
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
    
    @classmethod
    def get_download_dir(cls, custom_dir=None):
        """Get download directory"""
        if custom_dir:
            return Path(custom_dir)
        return Path(cls.DEFAULT_DOWNLOAD_DIR)
    
    @classmethod
    def get_cache_dir(cls, download_dir=None):
        """Get cache directory"""
        return Path('./arxiv_papers/.cache')
    
    @classmethod
    def get_log_dir(cls, download_dir=None):
        """Get log directory"""
        base_dir = cls.get_download_dir(download_dir)
        return base_dir / '.logs'