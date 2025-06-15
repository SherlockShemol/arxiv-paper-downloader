#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArXiv论文下载器安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取requirements文件
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="arxiv-downloader",
    version="1.0.0",
    author="ArXiv Downloader Team",
    author_email="your.email@example.com",
    description="智能ArXiv论文下载器，支持批量下载、智能命名和缓存机制",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/arxiv-downloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "types-requests>=2.28.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
            "asyncio>=3.4.3",
        ],
        "cli": [
            "click>=8.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "arxiv-dl=arxiv_downloader:main",
            "arxiv-downloader=arxiv_downloader:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="arxiv, papers, download, research, academic, pdf",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/arxiv-downloader/issues",
        "Source": "https://github.com/yourusername/arxiv-downloader",
        "Documentation": "https://github.com/yourusername/arxiv-downloader/wiki",
    },
)