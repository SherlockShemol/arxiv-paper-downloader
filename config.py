"""配置管理模块"""

from pathlib import Path

class Config:
    """应用配置类"""
    
    # 默认配置
    DEFAULT_DOWNLOAD_DIR = "~/Downloads/arxiv_papers"
    DEFAULT_QUERY = "cat:cs.AI"
    DEFAULT_MAX_RESULTS = 10
    
    # 文件处理配置
    MAX_FILENAME_LENGTH = 100
    REQUEST_DELAY = 1  # 秒
    API_TIMEOUT = 30   # 秒
    DOWNLOAD_TIMEOUT = 60  # 秒
    CHUNK_SIZE = 8192
    
    # 文件名清理规则
    INVALID_CHARS_PATTERN = r'[<>:"/\\|?*]'
    WHITESPACE_PATTERN = r'\s+'
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 2  # 指数退避基数
    
    # 并发配置
    MAX_CONCURRENT_DOWNLOADS = 5
    
    # 日志配置
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @classmethod
    def get_download_dir(cls, custom_dir=None):
        """获取下载目录"""
        if custom_dir:
            return Path(custom_dir)
        return Path(cls.DEFAULT_DOWNLOAD_DIR)
    
    @classmethod
    def get_cache_dir(cls, download_dir=None):
        """获取缓存目录"""
        base_dir = cls.get_download_dir(download_dir)
        return base_dir / '.cache'
    
    @classmethod
    def get_log_dir(cls, download_dir=None):
        """获取日志目录"""
        base_dir = cls.get_download_dir(download_dir)
        return base_dir / '.logs'