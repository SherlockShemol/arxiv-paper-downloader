"""工具函数模块"""

import re
import hashlib
from pathlib import Path
from typing import Union, Optional

from config import Config

def sanitize_filename(title: str, max_length: Optional[int] = None) -> str:
    """清理文件名，移除或替换不合法的字符
    
    Args:
        title: 原始标题
        max_length: 最大长度，默认使用配置中的值
    
    Returns:
        清理后的文件名
    """
    if max_length is None:
        max_length = Config.MAX_FILENAME_LENGTH
    
    # 移除或替换不合法的文件名字符
    title = re.sub(Config.INVALID_CHARS_PATTERN, '', title)
    # 替换多个空格为单个空格
    title = re.sub(Config.WHITESPACE_PATTERN, ' ', title)
    # 移除首尾空格
    title = title.strip()
    
    # 限制文件名长度
    if len(title) > max_length:
        title = title[:max_length].rstrip()
    
    # 如果标题为空，返回默认值
    if not title:
        return "untitled"
    
    return title

def generate_query_hash(query: str, date_from: Optional[str] = None, 
                       date_to: Optional[str] = None, max_results: int = 10) -> str:
    """生成查询的哈希值，用于缓存
    
    Args:
        query: 搜索查询
        date_from: 开始日期
        date_to: 结束日期
        max_results: 最大结果数
    
    Returns:
        查询的MD5哈希值
    """
    query_str = f"{query}|{date_from}|{date_to}|{max_results}"
    return hashlib.md5(query_str.encode('utf-8')).hexdigest()

def get_file_size_mb(filepath: Union[str, Path]) -> float:
    """获取文件大小（MB）
    
    Args:
        filepath: 文件路径
    
    Returns:
        文件大小（MB）
    """
    try:
        size_bytes = Path(filepath).stat().st_size
        return size_bytes / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0.0

def ensure_directory(directory: Union[str, Path]) -> Path:
    """确保目录存在
    
    Args:
        directory: 目录路径
    
    Returns:
        Path对象
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def is_valid_date_format(date_str: str) -> bool:
    """检查日期格式是否有效（YYYY-MM-DD）
    
    Args:
        date_str: 日期字符串
    
    Returns:
        是否有效
    """
    if not date_str:
        return False
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
    
    Returns:
        格式化的文件大小字符串
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
    """截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_text(text: str) -> str:
    """清理文本，移除多余的空白字符
    
    Args:
        text: 原始文本
    
    Returns:
        清理后的文本
    """
    # 替换换行符为空格
    text = text.replace('\n', ' ').replace('\r', ' ')
    # 替换多个空格为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空格
    return text.strip()

def validate_url(url: str) -> bool:
    """验证URL格式
    
    Args:
        url: URL字符串
    
    Returns:
        是否有效
    """
    if not url:
        return False
    
    # 简单的URL验证
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url, re.IGNORECASE))

def generate_unique_filename(base_path: Path, filename: str, 
                           paper_id: Optional[str] = None) -> Path:
    """生成唯一的文件名，避免冲突
    
    Args:
        base_path: 基础路径
        filename: 原始文件名
        paper_id: 论文ID，用于生成唯一后缀
    
    Returns:
        唯一的文件路径
    """
    filepath = base_path / filename
    
    # 如果文件不存在，直接返回
    if not filepath.exists():
        return filepath
    
    # 如果提供了paper_id，使用它作为后缀
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
    
    # 使用数字后缀
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