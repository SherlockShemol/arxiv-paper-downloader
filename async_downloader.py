#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步ArXiv论文下载器
支持高并发下载，提升下载效率
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
    """异步ArXiv论文下载器"""
    
    def __init__(self, download_dir: Optional[str] = None, 
                 max_concurrent: int = Config.MAX_CONCURRENT_DOWNLOADS):
        """初始化异步下载器
        
        Args:
            download_dir: 下载目录路径
            max_concurrent: 最大并发下载数
        """
        self.download_dir = Config.get_download_dir(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_concurrent = max_concurrent
        self.stats = DownloadStats()
        self.session: Optional[aiohttp.ClientSession] = None
        
        self.log_info(f"异步下载器初始化完成，最大并发数: {max_concurrent}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
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
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def download_papers_async(self, papers: List[Paper]) -> Dict[str, Any]:
        """异步批量下载论文
        
        Args:
            papers: 论文列表
        
        Returns:
            下载结果统计
        """
        if not self.session:
            raise RuntimeError("请在async with语句中使用异步下载器")
        
        start_time = time.time()
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        self.log_info(f"开始异步下载 {len(papers)} 篇论文")
        
        # 创建下载任务
        tasks = [
            self._download_single_async(paper, semaphore)
            for paper in papers
        ]
        
        # 执行所有下载任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
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
            f"异步下载完成: 成功 {successful}, 失败 {failed}, 跳过 {skipped}, "
            f"耗时 {total_time:.2f}秒"
        )
        
        return {
            'successful': successful,
            'failed': failed,
            'skipped': skipped,
            'total_time': total_time,
            'stats': self.stats
        }
    
    async def _download_single_async(self, paper: Paper, semaphore: asyncio.Semaphore) -> bool:
        """异步下载单个论文
        
        Args:
            paper: 论文对象
            semaphore: 信号量控制并发
        
        Returns:
            下载是否成功
        """
        async with semaphore:
            try:
                # 生成文件名
                clean_title = sanitize_filename(paper.title)
                filename = f"{paper.id}_{clean_title}.pdf"
                filepath = self.download_dir / filename
                
                # 检查文件是否已存在
                if filepath.exists():
                    self.log_info(f"文件已存在，跳过下载: {filename}")
                    return True
                
                # 确保文件名唯一
                filepath = generate_unique_filename(filepath)
                
                # 下载文件
                async with self.session.get(paper.pdf_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # 写入文件
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        file_size = get_file_size_mb(filepath)
                        self.stats.total_size_mb += file_size
                        
                        self.log_info(
                            f"下载成功: {filename} ({file_size:.2f}MB)"
                        )
                        return True
                    else:
                        raise NetworkError(
                            f"HTTP {response.status}: {response.reason}"
                        )
            
            except Exception as e:
                self.log_error(f"下载失败 {paper.id}: {str(e)}")
                
                # 清理不完整的文件
                if filepath.exists():
                    try:
                        filepath.unlink()
                    except Exception:
                        pass
                
                raise e
    
    async def download_with_retry_async(self, paper: Paper, max_retries: int = 3) -> bool:
        """带重试机制的异步下载
        
        Args:
            paper: 论文对象
            max_retries: 最大重试次数
        
        Returns:
            下载是否成功
        """
        for attempt in range(max_retries):
            try:
                semaphore = asyncio.Semaphore(1)
                return await self._download_single_async(paper, semaphore)
            
            except Exception as e:
                if attempt == max_retries - 1:
                    self.log_error(
                        f"下载失败，已重试{max_retries}次: {paper.id} - {str(e)}"
                    )
                    return False
                
                wait_time = (2 ** attempt) * Config.RETRY_DELAY_BASE
                self.log_warning(
                    f"下载失败，{wait_time}秒后重试 ({attempt + 1}/{max_retries}): "
                    f"{paper.id} - {str(e)}"
                )
                await asyncio.sleep(wait_time)
        
        return False

# 便捷函数
async def download_papers_async(papers: List[Paper], 
                               download_dir: Optional[str] = None,
                               max_concurrent: int = Config.MAX_CONCURRENT_DOWNLOADS) -> Dict[str, Any]:
    """便捷的异步下载函数
    
    Args:
        papers: 论文列表
        download_dir: 下载目录
        max_concurrent: 最大并发数
    
    Returns:
        下载结果统计
    """
    async with AsyncArxivDownloader(download_dir, max_concurrent) as downloader:
        return await downloader.download_papers_async(papers)

if __name__ == "__main__":
    # 示例用法
    async def main():
        # 创建示例论文
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
        
        # 异步下载
        result = await download_papers_async(papers)
        print(f"下载结果: {result}")
    
    # 运行示例
    asyncio.run(main())