#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArXiv论文下载器命令行接口
提供友好的命令行交互体验
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional, List

from arxiv_downloader import ArxivDownloader
from async_downloader import AsyncArxivDownloader, download_papers_async
from plugins import create_default_plugins, CategoryFilterPlugin
from config import Config
from logger import setup_logging

def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="ArXiv论文下载器 - 智能批量下载学术论文",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --query "cat:cs.AI" --max-results 20
  %(prog)s --query "ti:transformer" --date-from 2023-01-01 --date-to 2023-12-31
  %(prog)s --query "au:hinton" --download-dir ~/Papers --async
  %(prog)s --categories cs.AI,cs.LG --exclude-categories cs.CV
        """
    )
    
    # 基本参数
    parser.add_argument(
        "--query", "-q",
        default=Config.DEFAULT_QUERY,
        help=f"搜索查询 (默认: {Config.DEFAULT_QUERY})"
    )
    
    parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=Config.DEFAULT_MAX_RESULTS,
        help=f"最大下载数量 (默认: {Config.DEFAULT_MAX_RESULTS})"
    )
    
    parser.add_argument(
        "--download-dir", "-d",
        type=str,
        help=f"下载目录 (默认: {Config.DEFAULT_DOWNLOAD_DIR})"
    )
    
    # 日期范围
    parser.add_argument(
        "--date-from",
        type=str,
        help="开始日期 (格式: YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--date-to",
        type=str,
        help="结束日期 (格式: YYYY-MM-DD)"
    )
    
    # 分类过滤
    parser.add_argument(
        "--categories",
        type=str,
        help="允许的分类，用逗号分隔 (例如: cs.AI,cs.LG)"
    )
    
    parser.add_argument(
        "--exclude-categories",
        type=str,
        help="排除的分类，用逗号分隔 (例如: cs.CV,cs.RO)"
    )
    
    # 性能选项
    parser.add_argument(
        "--async",
        action="store_true",
        help="使用异步下载 (更快)"
    )
    
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=Config.MAX_CONCURRENT_DOWNLOADS,
        help=f"最大并发下载数 (默认: {Config.MAX_CONCURRENT_DOWNLOADS})"
    )
    
    # 插件选项
    parser.add_argument(
        "--no-plugins",
        action="store_true",
        help="禁用所有插件"
    )
    
    parser.add_argument(
        "--no-duplicate-check",
        action="store_true",
        help="禁用重复检查"
    )
    
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="不保存元数据"
    )
    
    # 日志选项
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式"
    )
    
    # 其他选项
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅搜索不下载"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="ArXiv Downloader 1.0.0"
    )
    
    return parser

def setup_logging_from_args(args) -> None:
    """根据命令行参数设置日志"""
    if args.quiet:
        log_level = 40  # ERROR
    elif args.verbose:
        log_level = 10  # DEBUG
    else:
        log_level = 20  # INFO
    
    setup_logging(
        log_level=log_level,
        log_dir=Config.get_log_dir(args.download_dir),
        console_output=not args.quiet
    )

def parse_categories(categories_str: Optional[str]) -> List[str]:
    """解析分类字符串"""
    if not categories_str:
        return []
    return [cat.strip() for cat in categories_str.split(',') if cat.strip()]

def print_search_results(papers, dry_run=False):
    """打印搜索结果"""
    if not papers:
        print("未找到符合条件的论文")
        return
    
    print(f"\n找到 {len(papers)} 篇论文:")
    print("-" * 80)
    
    for i, paper in enumerate(papers, 1):
        print(f"{i:2d}. {paper.id} - {paper.title[:60]}...")
        print(f"    作者: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        print(f"    分类: {', '.join(paper.categories)}")
        print(f"    发布: {paper.published}")
        print()
    
    if dry_run:
        print("[试运行模式] 未执行实际下载")

def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置日志
    setup_logging_from_args(args)
    
    try:
        # 创建下载器
        downloader = ArxivDownloader(args.download_dir)
        
        # 搜索论文
        print(f"搜索论文: {args.query}")
        if args.date_from or args.date_to:
            print(f"日期范围: {args.date_from or '不限'} 到 {args.date_to or '不限'}")
        
        papers = downloader.search_papers(
            query=args.query,
            date_from=args.date_from,
            date_to=args.date_to,
            max_results=args.max_results
        )
        
        # 设置插件
        if not args.no_plugins:
            plugin_manager = create_default_plugins(downloader.download_dir)
            
            # 分类过滤插件
            allowed_categories = parse_categories(args.categories)
            excluded_categories = parse_categories(args.exclude_categories)
            
            if allowed_categories or excluded_categories:
                category_filter = CategoryFilterPlugin(
                    allowed_categories=allowed_categories,
                    blocked_categories=excluded_categories
                )
                plugin_manager.register_plugin(category_filter)
            
            # 禁用特定插件
            if args.no_duplicate_check:
                duplicate_plugin = plugin_manager.get_plugin("duplicate_check")
                if duplicate_plugin:
                    duplicate_plugin.disable()
            
            if args.no_metadata:
                metadata_plugin = plugin_manager.get_plugin("metadata")
                if metadata_plugin:
                    metadata_plugin.disable()
            
            # 应用插件过滤
            filtered_papers = []
            for paper in papers:
                if plugin_manager.pre_download_hook(paper):
                    filtered_papers.append(paper)
            
            papers = filtered_papers
        
        # 显示搜索结果
        print_search_results(papers, args.dry_run)
        
        if args.dry_run or not papers:
            return
        
        # 确认下载
        if not args.quiet:
            response = input(f"\n是否下载这 {len(papers)} 篇论文? [y/N]: ")
            if response.lower() not in ['y', 'yes', '是']:
                print("取消下载")
                return
        
        # 执行下载
        print(f"\n开始下载到: {downloader.download_dir}")
        
        if getattr(args, 'async'):
            # 异步下载
            result = asyncio.run(
                download_papers_async(
                    papers, 
                    args.download_dir, 
                    args.max_concurrent
                )
            )
            
            print(f"\n下载完成!")
            print(f"成功: {result['successful']}")
            print(f"失败: {result['failed']}")
            print(f"跳过: {result['skipped']}")
            print(f"耗时: {result['total_time']:.2f}秒")
        else:
            # 同步下载
            successful = 0
            failed = 0
            
            for i, paper in enumerate(papers, 1):
                print(f"[{i}/{len(papers)}] 下载: {paper.title[:50]}...")
                
                try:
                    if downloader.download_pdf(paper.pdf_url, paper.title, paper.id):
                        successful += 1
                        if not args.no_plugins:
                            plugin_manager.post_download_hook(
                                paper, 
                                downloader.download_dir / f"{paper.id}_{paper.title[:50]}.pdf",
                                True
                            )
                    else:
                        failed += 1
                        if not args.no_plugins:
                            plugin_manager.post_download_hook(
                                paper, 
                                Path(""),
                                False
                            )
                except Exception as e:
                    print(f"下载失败: {str(e)}")
                    failed += 1
            
            print(f"\n下载完成! 成功: {successful}, 失败: {failed}")
    
    except KeyboardInterrupt:
        print("\n用户中断下载")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()