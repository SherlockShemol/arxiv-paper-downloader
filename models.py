"""Data models and exception definitions"""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

# Exception class definitions
class ArxivDownloadError(Exception):
    """Base class for ArXiv download related exceptions"""
    pass

class NetworkError(ArxivDownloadError):
    """Network related exceptions"""
    pass

class FileOperationError(ArxivDownloadError):
    """File operation exceptions"""
    pass

class ValidationError(ArxivDownloadError):
    """Data validation exceptions"""
    pass

class ParseError(ArxivDownloadError):
    """Parsing exceptions"""
    pass

@dataclass
class Paper:
    """Paper data class"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    pdf_url: str
    published: str
    categories: List[str]
    
    def __post_init__(self):
        """Data validation"""
        if not self.id or not self.title:
            raise ValidationError("Paper ID and title cannot be empty")
        
        if not self.pdf_url or not self.pdf_url.startswith('http'):
            raise ValidationError("Invalid PDF URL")
        
        if not isinstance(self.authors, list):
            raise ValidationError("Author information must be in list format")
        
        if not isinstance(self.categories, list):
            raise ValidationError("Category information must be in list format")
    
    @property
    def short_abstract(self, max_length: int = 200) -> str:
        """Get short abstract"""
        if len(self.abstract) <= max_length:
            return self.abstract
        return self.abstract[:max_length] + "..."
    
    @property
    def authors_str(self) -> str:
        """Get authors string"""
        return ', '.join(self.authors)
    
    @property
    def categories_str(self) -> str:
        """Get categories string"""
        return ', '.join(self.categories)

@dataclass
class DownloadStats:
    """Download statistics data class"""
    total_papers: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    skipped_downloads: int = 0
    total_size_mb: float = 0.0
    download_time_seconds: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Success rate"""
        if self.total_papers == 0:
            return 0.0
        return self.successful_downloads / self.total_papers
    
    @property
    def average_speed_mbps(self) -> float:
        """Average download speed (MB/s)"""
        if self.download_time_seconds == 0:
            return 0.0
        return self.total_size_mb / self.download_time_seconds
    
    def add_success(self, file_size_mb: float = 0.0):
        """Add successful download record"""
        self.successful_downloads += 1
        self.total_size_mb += file_size_mb
    
    def add_failure(self):
        """Add failed download record"""
        self.failed_downloads += 1
    
    def add_skip(self):
        """Add skipped download record"""
        self.skipped_downloads += 1
    
    def reset(self):
        """Reset statistics data"""
        self.total_papers = 0
        self.successful_downloads = 0
        self.failed_downloads = 0
        self.skipped_downloads = 0
        self.total_size_mb = 0.0
        self.download_time_seconds = 0.0
    
    def __str__(self) -> str:
        """String representation of statistics"""
        return (f"Total: {self.total_papers}, "
                f"Success: {self.successful_downloads}, "
                f"Failed: {self.failed_downloads}, "
                f"Skipped: {self.skipped_downloads}, "
                f"Success rate: {self.success_rate:.1%}")