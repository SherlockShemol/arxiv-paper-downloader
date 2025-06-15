#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArXiv Paper Downloader Command Line Interface
Provides friendly command line interaction experience
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
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="ArXiv Paper Downloader - Intelligent batch download of academic papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s --query "cat:cs.AI" --max-results 20
  %(prog)s --query "ti:transformer" --date-from 2023-01-01 --date-to 2023-12-31
  %(prog)s --query "au:hinton" --download-dir ~/Papers --async
  %(prog)s --categories cs.AI,cs.LG --exclude-categories cs.CV
        """
    )
    
    # Basic parameters
    parser.add_argument(
        "--query", "-q",
        default=Config.DEFAULT_QUERY,
        help=f"Search query (default: {Config.DEFAULT_QUERY})"
    )
    
    parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=Config.DEFAULT_MAX_RESULTS,
        help=f"Maximum download count (default: {Config.DEFAULT_MAX_RESULTS})"
    )
    
    parser.add_argument(
        "--download-dir", "-d",
        type=str,
        help=f"Download directory (default: {Config.DEFAULT_DOWNLOAD_DIR})"
    )
    
    # Date range
    parser.add_argument(
        "--date-from",
        type=str,
        help="Start date (format: YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--date-to",
        type=str,
        help="End date (format: YYYY-MM-DD)"
    )
    
    # Category filtering
    parser.add_argument(
        "--categories",
        type=str,
        help="Allowed categories, comma-separated (e.g.: cs.AI,cs.LG)"
    )
    
    parser.add_argument(
        "--exclude-categories",
        type=str,
        help="Excluded categories, comma-separated (e.g.: cs.CV,cs.RO)"
    )
    
    # Performance options
    parser.add_argument(
        "--async",
        action="store_true",
        help="Use async download (faster)"
    )
    
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=Config.MAX_CONCURRENT_DOWNLOADS,
        help=f"Maximum concurrent downloads (default: {Config.MAX_CONCURRENT_DOWNLOADS})"
    )
    
    # Plugin options
    parser.add_argument(
        "--no-plugins",
        action="store_true",
        help="Disable all plugins"
    )
    
    parser.add_argument(
        "--no-duplicate-check",
        action="store_true",
        help="Disable duplicate check"
    )
    
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Do not save metadata"
    )
    
    # Logging options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Quiet mode"
    )
    
    # Other options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Search only, do not download"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="ArXiv Downloader 1.0.0"
    )
    
    return parser

def setup_logging_from_args(args) -> None:
    """Setup logging based on command line arguments"""
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
    """Parse category string"""
    if not categories_str:
        return []
    return [cat.strip() for cat in categories_str.split(',') if cat.strip()]

def print_search_results(papers, dry_run=False):
    """Print search results"""
    if not papers:
        print("No papers found matching the criteria")
        return
    
    print(f"\nFound {len(papers)} papers:")
    print("-" * 80)
    
    for i, paper in enumerate(papers, 1):
        print(f"{i:2d}. {paper.id} - {paper.title[:60]}...")
        print(f"    Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        print(f"    Categories: {', '.join(paper.categories)}")
        print(f"    Published: {paper.published}")
        print()
    
    if dry_run:
        print("[Dry run mode] No actual download performed")

def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging_from_args(args)
    
    try:
        # Create downloader
        downloader = ArxivDownloader(args.download_dir)
        
        # Search papers
        print(f"Searching papers: {args.query}")
        if args.date_from or args.date_to:
            print(f"Date range: {args.date_from or 'unlimited'} to {args.date_to or 'unlimited'}")
        
        papers = downloader.search_papers(
            query=args.query,
            date_from=args.date_from,
            date_to=args.date_to,
            max_results=args.max_results
        )
        
        # Setup plugins
        if not args.no_plugins:
            plugin_manager = create_default_plugins(downloader.download_dir)
            
            # Category filter plugin
            allowed_categories = parse_categories(args.categories)
            excluded_categories = parse_categories(args.exclude_categories)
            
            if allowed_categories or excluded_categories:
                category_filter = CategoryFilterPlugin(
                    allowed_categories=allowed_categories,
                    blocked_categories=excluded_categories
                )
                plugin_manager.register_plugin(category_filter)
            
            # Disable specific plugins
            if args.no_duplicate_check:
                duplicate_plugin = plugin_manager.get_plugin("duplicate_check")
                if duplicate_plugin:
                    duplicate_plugin.disable()
            
            if args.no_metadata:
                metadata_plugin = plugin_manager.get_plugin("metadata")
                if metadata_plugin:
                    metadata_plugin.disable()
            
            # Apply plugin filtering
            filtered_papers = []
            for paper in papers:
                if plugin_manager.pre_download_hook(paper):
                    filtered_papers.append(paper)
            
            papers = filtered_papers
        
        # Display search results
        print_search_results(papers, args.dry_run)
        
        if args.dry_run or not papers:
            return
        
        # Confirm download
        if not args.quiet:
            response = input(f"\nDownload these {len(papers)} papers? [y/N]: ")
            if response.lower() not in ['y', 'yes']:
                print("Download cancelled")
                return
        
        # Execute download
        print(f"\nStarting download to: {downloader.download_dir}")
        
        if getattr(args, 'async'):
            # Async download
            result = asyncio.run(
                download_papers_async(
                    papers, 
                    args.download_dir, 
                    args.max_concurrent
                )
            )
            
            print(f"\nDownload completed!")
            print(f"Successful: {result['successful']}")
            print(f"Failed: {result['failed']}")
            print(f"Skipped: {result['skipped']}")
            print(f"Time taken: {result['total_time']:.2f} seconds")
        else:
            # Sync download
            successful = 0
            failed = 0
            
            for i, paper in enumerate(papers, 1):
                print(f"[{i}/{len(papers)}] Downloading: {paper.title[:50]}...")
                
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
                    print(f"Download failed: {str(e)}")
                    failed += 1
            
            print(f"\nDownload completed! Successful: {successful}, Failed: {failed}")
    
    except KeyboardInterrupt:
        print("\nUser interrupted download")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()