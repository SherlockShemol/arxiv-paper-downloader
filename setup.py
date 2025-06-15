#!/usr/bin/env python3
"""
ArXiv Paper Downloader Installation Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements file
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="arxiv-paper-downloader",
    version="2.0.0",
    author="AI Assistant",
    author_email="assistant@example.com",
    description="Intelligent ArXiv paper downloader with batch download, smart naming and caching mechanism",
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