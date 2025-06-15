"""日志系统模块"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import Config

def setup_logging(log_level: int = logging.INFO, 
                 log_dir: Optional[Path] = None,
                 console_output: bool = True) -> logging.Logger:
    """设置日志系统
    
    Args:
        log_level: 日志级别
        log_dir: 日志目录，如果为None则使用默认目录
        console_output: 是否输出到控制台
    
    Returns:
        配置好的logger实例
    """
    # 获取日志目录
    if log_dir is None:
        log_dir = Config.get_log_dir()
    
    # 确保日志目录存在
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger('arxiv_downloader')
    logger.setLevel(log_level)
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 创建格式器
    formatter = logging.Formatter(
        Config.LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    )
    
    # 文件处理器
    log_file = log_dir / f'arxiv_downloader_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = 'arxiv_downloader') -> logging.Logger:
    """获取logger实例"""
    return logging.getLogger(name)

class LoggerMixin:
    """日志混入类"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取logger实例"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger()
        return self._logger
    
    def log_info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)
    
    def log_debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)