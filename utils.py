"""Utility functions module"""

import re
import hashlib
from pathlib import Path
from typing import Union, Optional

from config import Config

def sanitize_filename(title: str, max_length: Optional[int] = None) -> str:
    """Clean filename, remove or replace invalid characters
    
    Args:
        title: Original title
        max_length: Maximum length, use config value by default
    
    Returns:
        Cleaned filename
    """
    if max_length is None:
        max_length = Config.MAX_FILENAME_LENGTH
    
    # Remove or replace invalid filename characters
    title = re.sub(Config.INVALID_CHARS_PATTERN, '', title)
    # Replace multiple spaces with single space
    title = re.sub(Config.WHITESPACE_PATTERN, ' ', title)
    # Remove leading and trailing spaces
    title = title.strip()
    
    # Limit filename length
    if len(title) > max_length:
        title = title[:max_length].rstrip()
    
    # If title is empty, return default value
    if not title:
        return "untitled"
    
    return title

def generate_query_hash(query: str, date_from: Optional[str] = None, 
                       date_to: Optional[str] = None, max_results: int = 10) -> str:
    """Generate hash value for query, used for caching
    
    Args:
        query: Search query
        date_from: Start date
        date_to: End date
        max_results: Maximum results
    
    Returns:
        MD5 hash value of query
    """
    query_str = f"{query}|{date_from}|{date_to}|{max_results}"
    return hashlib.md5(query_str.encode('utf-8')).hexdigest()

def get_file_size_mb(filepath: Union[str, Path]) -> float:
    """Get file size in MB
    
    Args:
        filepath: File path
    
    Returns:
        File size in MB
    """
    try:
        size_bytes = Path(filepath).stat().st_size
        return size_bytes / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0.0

def ensure_directory(directory: Union[str, Path]) -> Path:
    """Ensure directory exists
    
    Args:
        directory: Directory path
    
    Returns:
        Path object
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def is_valid_date_format(date_str: str) -> bool:
    """Check if date format is valid (YYYY-MM-DD)
    
    Args:
        date_str: Date string
    
    Returns:
        Whether valid
    """
    if not date_str:
        return False
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))

def format_file_size(size_bytes: int) -> str:
    """Format file size display
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text
    
    Args:
        text: Original text
        max_length: Maximum length
        suffix: Truncation suffix
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_text(text: str) -> str:
    """Clean text, remove extra whitespace characters
    
    Args:
        text: Original text
    
    Returns:
        Cleaned text
    """
    # Replace newlines with spaces
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading and trailing spaces
    return text.strip()

def validate_url(url: str) -> bool:
    """Validate URL format
    
    Args:
        url: URL string
    
    Returns:
        Whether valid
    """
    if not url:
        return False
    
    # Simple URL validation
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url, re.IGNORECASE))

def generate_unique_filename(base_path: Path, filename: str, 
                           paper_id: Optional[str] = None) -> Path:
    """Generate unique filename to avoid conflicts
    
    Args:
        base_path: Base path
        filename: Original filename
        paper_id: Paper ID, used to generate unique suffix
    
    Returns:
        Unique file path
    """
    filepath = base_path / filename
    
    # If file doesn't exist, return directly
    if not filepath.exists():
        return filepath
    
    # If paper_id is provided, use it as suffix
    if paper_id:
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            new_filename = f"{name}_{paper_id}.{ext}"
        else:
            new_filename = f"{filename}_{paper_id}"
        
        new_filepath = base_path / new_filename
        if not new_filepath.exists():
            return new_filepath
    
    # Use numeric suffix
    name_parts = filename.rsplit('.', 1)
    if len(name_parts) == 2:
        name, ext = name_parts
        template = f"{name}_{{}}.{ext}"
    else:
        template = f"{filename}_{{}}"
    
    counter = 1
    while True:
        new_filename = template.format(counter)
        new_filepath = base_path / new_filename
        if not new_filepath.exists():
            return new_filepath
        counter += 1