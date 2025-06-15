#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async ArXiv Paper Downloader
Supports high concurrency downloads to improve download efficiency
"""

import asyncio
import aiohttp
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from config import Config
from models import Paper, DownloadStats, NetworkError, FileOperationError
from logger import LoggerMixin
from utils import sanitize_filename, get_file_size_mb, generate_unique_filename

class AsyncArxivDownloader(LoggerMixin):
    """Async ArXiv Paper Downloader"""
    
    def __init__(self, download_dir: Optional[str] = None, 
                 max_concurrent: int = Config.MAX_CONCURRENT_DOWNLOADS):
        """Initialize async downloader
        
        Args:
            download_dir: Download directory path
            max_concurrent: Maximum concurrent downloads
        """
        self.download_dir = Config.get_download_dir(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_concurrent = max_concurrent
        self.stats = DownloadStats()
        self.session: Optional[aiohttp.ClientSession] = None
        
        self.log_info(f"Async downloader initialized, max concurrent: {max_concurrent}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent * 2,
            limit_per_host=self.max_concurrent,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(
            total=Config.DOWNLOAD_TIMEOUT,
            connect=Config.API_TIMEOUT
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'ArXiv-Downloader/1.0 (Academic Research Tool)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def download_papers_async(self, papers: List[Paper]) -> Dict[str, Any]:
        """Async batch download papers
        
        Args:
            papers: List of papers
        
        Returns:
            Download result statistics
        """
        if not self.session:
            raise RuntimeError("Please use async downloader within async with statement")
        
        start_time = time.time()
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        self.log_info(f"Starting async download of {len(papers)} papers")
        
        # Create download tasks
        tasks = [
            self._download_single_async(paper, semaphore)
            for paper in papers
        ]
        
        # Execute all download tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        successful = sum(1 for r in results if r is True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        skipped = len(results) - successful - failed
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.stats.successful_downloads = successful
        self.stats.failed_downloads = failed
        self.stats.skipped_downloads = skipped
        self.stats.total_papers = len(papers)
        self.stats.download_time_seconds = total_time
        
        self.log_info(
            f"Async download completed: successful {successful}, failed {failed}, skipped {skipped}, "
            f"time taken {total_time:.2f} seconds"
        )
        
        return {
            'successful': successful,
            'failed': failed,
            'skipped': skipped,
            'total_time': total_time,
            'stats': self.stats
        }
    
    async def _download_single_async(self, paper: Paper, semaphore: asyncio.Semaphore) -> bool:
        """Async download single paper
        
        Args:
            paper: Paper object
            semaphore: Semaphore for concurrency control
        
        Returns:
            Whether download was successful
        """
        async with semaphore:
            try:
                # Generate filename
                clean_title = sanitize_filename(paper.title)
                filename = f"{paper.id}_{clean_title}.pdf"
                filepath = self.download_dir / filename
                
                # Check if file already exists
                if filepath.exists():
                    self.log_info(f"File already exists, skipping download: {filename}")
                    return True
                
                # Ensure filename is unique
                filepath = generate_unique_filename(filepath)
                
                # Download file
                async with self.session.get(paper.pdf_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Write file
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        file_size = get_file_size_mb(filepath)
                        self.stats.total_size_mb += file_size
                        
                        self.log_info(
                            f"Download successful: {filename} ({file_size:.2f}MB)"
                        )
                        return True
                    else:
                        raise NetworkError(
                            f"HTTP {response.status}: {response.reason}"
                        )
            
            except Exception as e:
                self.log_error(f"Download failed {paper.id}: {str(e)}")
                
                # Clean up incomplete file
                if filepath.exists():
                    try:
                        filepath.unlink()
                    except Exception:
                        pass
                
                raise e
    
    async def download_with_retry_async(self, paper: Paper, max_retries: int = 3) -> bool:
        """Async download with retry mechanism
        
        Args:
            paper: Paper object
            max_retries: Maximum retry attempts
        
        Returns:
            Whether download was successful
        """
        for attempt in range(max_retries):
            try:
                semaphore = asyncio.Semaphore(1)
                return await self._download_single_async(paper, semaphore)
            
            except Exception as e:
                if attempt == max_retries - 1:
                    self.log_error(
                        f"Download failed after {max_retries} retries: {paper.id} - {str(e)}"
                    )
                    return False
                
                wait_time = (2 ** attempt) * Config.RETRY_DELAY_BASE
                self.log_warning(
                    f"Download failed, retrying in {wait_time} seconds ({attempt + 1}/{max_retries}): "
                    f"{paper.id} - {str(e)}"
                )
                await asyncio.sleep(wait_time)
        
        return False

# Convenience function
async def download_papers_async(papers: List[Paper], 
                               download_dir: Optional[str] = None,
                               max_concurrent: int = Config.MAX_CONCURRENT_DOWNLOADS) -> Dict[str, Any]:
    """Convenient async download function
    
    Args:
        papers: List of papers
        download_dir: Download directory
        max_concurrent: Maximum concurrent downloads
    
    Returns:
        Download result statistics
    """
    async with AsyncArxivDownloader(download_dir, max_concurrent) as downloader:
        return await downloader.download_papers_async(papers)

if __name__ == "__main__":
    # Example usage
    async def main():
        # Create example papers
        papers = [
            Paper(
                id="2301.00001",
                title="Example Paper 1",
                authors=["Author 1"],
                abstract="Abstract 1",
                pdf_url="https://arxiv.org/pdf/2301.00001.pdf",
                published="2023-01-01",
                categories=["cs.AI"]
            )
        ]
        
        # Async download
        result = await download_papers_async(papers)
        print(f"Download result: {result}")
    
    # Run example
    asyncio.run(main())