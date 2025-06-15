"""Logging system module"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import Config

def setup_logging(log_level: int = logging.INFO, 
                 log_dir: Optional[Path] = None,
                 console_output: bool = True) -> logging.Logger:
    """Setup logging system
    
    Args:
        log_level: Log level
        log_dir: Log directory, use default if None
        console_output: Whether to output to console
    
    Returns:
        Configured logger instance
    """
    # Get log directory
    if log_dir is None:
        log_dir = Config.get_log_dir()
    
    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('arxiv_downloader')
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        Config.LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    )
    
    # File handler
    log_file = log_dir / f'arxiv_downloader_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = 'arxiv_downloader') -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

class LoggerMixin:
    """Logger mixin class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger instance"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger()
        return self._logger
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def log_debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)