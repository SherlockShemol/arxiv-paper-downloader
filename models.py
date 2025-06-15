"""数据模型和异常定义"""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

# 异常类定义
class ArxivDownloadError(Exception):
    """ArXiv下载相关异常基类"""
    pass

class NetworkError(ArxivDownloadError):
    """网络相关异常"""
    pass

class FileOperationError(ArxivDownloadError):
    """文件操作异常"""
    pass

class ValidationError(ArxivDownloadError):
    """数据验证异常"""
    pass

class ParseError(ArxivDownloadError):
    """解析异常"""
    pass

@dataclass
class Paper:
    """论文数据类"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    pdf_url: str
    published: str
    categories: List[str]
    
    def __post_init__(self):
        """数据验证"""
        if not self.id or not self.title:
            raise ValidationError("论文ID和标题不能为空")
        
        if not self.pdf_url or not self.pdf_url.startswith('http'):
            raise ValidationError("无效的PDF URL")
        
        if not isinstance(self.authors, list):
            raise ValidationError("作者信息必须是列表格式")
        
        if not isinstance(self.categories, list):
            raise ValidationError("类别信息必须是列表格式")
    
    @property
    def short_abstract(self, max_length: int = 200) -> str:
        """获取简短摘要"""
        if len(self.abstract) <= max_length:
            return self.abstract
        return self.abstract[:max_length] + "..."
    
    @property
    def authors_str(self) -> str:
        """获取作者字符串"""
        return ', '.join(self.authors)
    
    @property
    def categories_str(self) -> str:
        """获取类别字符串"""
        return ', '.join(self.categories)

@dataclass
class DownloadStats:
    """下载统计数据类"""
    total_papers: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    skipped_downloads: int = 0
    total_size_mb: float = 0.0
    download_time_seconds: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_papers == 0:
            return 0.0
        return self.successful_downloads / self.total_papers
    
    @property
    def average_speed_mbps(self) -> float:
        """平均下载速度 (MB/s)"""
        if self.download_time_seconds == 0:
            return 0.0
        return self.total_size_mb / self.download_time_seconds
    
    def add_success(self, file_size_mb: float = 0.0):
        """添加成功下载记录"""
        self.successful_downloads += 1
        self.total_size_mb += file_size_mb
    
    def add_failure(self):
        """添加失败下载记录"""
        self.failed_downloads += 1
    
    def add_skip(self):
        """添加跳过下载记录"""
        self.skipped_downloads += 1
    
    def reset(self):
        """重置统计数据"""
        self.total_papers = 0
        self.successful_downloads = 0
        self.failed_downloads = 0
        self.skipped_downloads = 0
        self.total_size_mb = 0.0
        self.download_time_seconds = 0.0
    
    def __str__(self) -> str:
        """统计信息字符串表示"""
        return (f"总计: {self.total_papers}, "
                f"成功: {self.successful_downloads}, "
                f"失败: {self.failed_downloads}, "
                f"跳过: {self.skipped_downloads}, "
                f"成功率: {self.success_rate:.1%}")