"""ArXiv AI Paper Automatic Downloader - Refactored Version

Support searching and downloading AI-related papers with specified date ranges
Features comprehensive error handling, caching mechanism, logging system and type hints
"""

import argparse
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

import requests

from config import Config
from models import Paper, DownloadStats, NetworkError, FileOperationError, ParseError, ValidationError
from logger import setup_logging, LoggerMixin
from cache import CacheManager
from utils import (
    sanitize_filename, generate_query_hash, get_file_size_mb,
    ensure_directory, is_valid_date_format, clean_text,
    validate_url, generate_unique_filename
)

class ArxivDownloader(LoggerMixin):
    """ArXiv paper downloader"""
    
    def __init__(self, download_dir: Optional[str] = None):
        """Initialize downloader
        
        Args:
            download_dir: Download directory path
        """
        self.download_dir = Config.get_download_dir(download_dir)
        ensure_directory(self.download_dir)
        
        self.base_url = "http://export.arxiv.org/api/query"
        self.stats = DownloadStats()
        self.cache_manager = CacheManager()
        
        # Setup logging
        setup_logging(log_dir=Config.get_log_dir(self.download_dir))
        
        self.log_info(f"ArXiv downloader initialized, download directory: {self.download_dir}")
    
    def search_papers(self, query: str = Config.DEFAULT_QUERY, 
                     date_from: Optional[str] = None, 
                     date_to: Optional[str] = None, 
                     max_results: int = Config.DEFAULT_MAX_RESULTS) -> List[Paper]:
        """Search ArXiv papers
        
        Args:
            query: Search query, default to cs.AI category
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            max_results: Maximum number of results
        
        Returns:
            List of papers
        
        Raises:
            ValidationError: Parameter validation failed
            NetworkError: Network request failed
            ParseError: XML parsing failed
        """
        # Parameter validation
        if date_from and not is_valid_date_format(date_from):
            raise ValidationError(f"Invalid start date format: {date_from}")
        
        if date_to and not is_valid_date_format(date_to):
            raise ValidationError(f"Invalid end date format: {date_to}")
        
        if max_results <= 0:
            raise ValidationError(f"Maximum results must be greater than 0: {max_results}")
        
        # Check cache
        query_hash = generate_query_hash(query, date_from, date_to, max_results)
        cached_results = self.cache_manager.get_search_results(query_hash)
        
        if cached_results is not None:
            self.log_info(f"Retrieved search results from cache, {len(cached_results)} papers total")
            return [Paper(**paper_data) for paper_data in cached_results]
        
        # Build search query
        search_query = query
        
        # Add date range filter
        if date_from or date_to:
            date_filter = "submittedDate:"
            if date_from and date_to:
                date_filter += f"[{date_from.replace('-', '')}0000+TO+{date_to.replace('-', '')}2359]"
            elif date_from:
                date_filter += f"[{date_from.replace('-', '')}0000+TO+*]"
            elif date_to:
                date_filter += f"[*+TO+{date_to.replace('-', '')}2359]"
            
            search_query += f"+AND+{date_filter}"
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        self.log_info(f"Search query: {search_query}")
        self.log_info("Searching ArXiv papers...")
        
        try:
            response = self._make_request_with_retry(self.base_url, params)
            papers = self._parse_arxiv_response(response.text)
            
            # Cache search results
            paper_data_list = [self._paper_to_dict(paper) for paper in papers]
            self.cache_manager.save_search_results(query_hash, paper_data_list)
            
            self.log_info(f"Search completed, found {len(papers)} papers")
            return papers
             
        except requests.RequestException as e:
            raise NetworkError(f"Search request failed: {e}")
    
    def _make_request_with_retry(self, url: str, params: Dict[str, Any], 
                                max_retries: int = Config.MAX_RETRIES) -> requests.Response:
        """HTTP request with retry mechanism
        
        Args:
            url: Request URL
            params: Request parameters
            max_retries: Maximum retry attempts
        
        Returns:
            Response object
        
        Raises:
            NetworkError: Request failed
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=Config.API_TIMEOUT)
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"Request failed after {max_retries} retries: {e}")
                
                wait_time = Config.RETRY_DELAY_BASE ** attempt
                self.log_warning(f"Request failed, retrying in {wait_time} seconds ({attempt + 1}/{max_retries}): {e}")
                time.sleep(wait_time)
        
        raise NetworkError("Request retry attempts exhausted")
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Paper]:
        """Parse ArXiv API XML response
        
        Args:
            xml_content: XML content
        
        Returns:
            List of papers
        
        Raises:
            ParseError: XML parsing failed
        """
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entries = root.findall('atom:entry', namespaces)
            
            for entry in entries:
                try:
                    paper_data = self._parse_paper_entry(entry, namespaces)
                    if paper_data:
                        paper = Paper(**paper_data)
                        papers.append(paper)
                        
                except (ValidationError, KeyError) as e:
                    self.log_warning(f"Skipping invalid paper entry: {e}")
                    continue
            
        except ET.ParseError as e:
            raise ParseError(f"XML parsing error: {e}")
        
        return papers
    
    def _parse_paper_entry(self, entry: ET.Element, namespaces: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Parse single paper entry
        
        Args:
            entry: XML entry element
            namespaces: XML namespaces
        
        Returns:
            Paper data dictionary
        """
        paper_data = {}
        
        # Get ID
        id_elem = entry.find('atom:id', namespaces)
        if id_elem is None:
            return None
        paper_data['id'] = id_elem.text.split('/')[-1]
        
        # Get title
        title_elem = entry.find('atom:title', namespaces)
        if title_elem is None:
            return None
        paper_data['title'] = clean_text(title_elem.text)
        
        # Get authors
        authors = []
        for author in entry.findall('atom:author', namespaces):
            name_elem = author.find('atom:name', namespaces)
            if name_elem is not None:
                authors.append(name_elem.text.strip())
        paper_data['authors'] = authors
        
        # Get abstract
        summary_elem = entry.find('atom:summary', namespaces)
        if summary_elem is not None:
            paper_data['abstract'] = clean_text(summary_elem.text)
        else:
            paper_data['abstract'] = ""
        
        # Get PDF link
        pdf_url = None
        for link in entry.findall('atom:link', namespaces):
            if link.get('type') == 'application/pdf':
                pdf_url = link.get('href')
                break
        
        if not pdf_url or not validate_url(pdf_url):
            return None
        paper_data['pdf_url'] = pdf_url
        
        # Get publication date
        published_elem = entry.find('atom:published', namespaces)
        if published_elem is not None:
            paper_data['published'] = published_elem.text
        else:
            paper_data['published'] = ""
        
        # Get categories
        categories = []
        for category in entry.findall('atom:category', namespaces):
            term = category.get('term')
            if term:
                categories.append(term)
        paper_data['categories'] = categories
        
        return paper_data
    
    def download_pdf(self, paper: Paper) -> bool:
        """Download PDF of a single paper
        
        Args:
            paper: Paper object
        
        Returns:
            Whether download was successful
        """
        # Generate filename
        clean_title = sanitize_filename(paper.title)
        filename = f"{clean_title}.pdf"
        filepath = generate_unique_filename(self.download_dir, filename, paper.id)
        
        # Check if file already exists
        if filepath.exists():
            self.log_info(f"✓ File already exists: {filepath.name}")
            self.stats.add_skip()
            return True
        
        try:
            self.log_info(f"Downloading: {paper.title[:50]}...")
            
            # Download file
            response = self._download_with_retry(paper.pdf_url)
            
            # Save file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=Config.CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
            
            # Record statistics
            file_size_mb = get_file_size_mb(filepath)
            self.stats.add_success(file_size_mb)
            
            self.log_info(f"✓ Download completed: {filepath.name}")
            return True
            
        except (NetworkError, FileOperationError) as e:
            self.log_error(f"✗ Download failed {filename}: {e}")
            
            # Delete incomplete file
            if filepath.exists():
                try:
                    filepath.unlink()
                except OSError:
                    pass
            
            self.stats.add_failure()
            return False
    
    def _download_with_retry(self, url: str, max_retries: int = Config.MAX_RETRIES) -> requests.Response:
        """File download with retry mechanism
        
        Args:
            url: Download URL
            max_retries: Maximum retry attempts
        
        Returns:
            Response object
        
        Raises:
            NetworkError: Download failed
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=Config.DOWNLOAD_TIMEOUT, stream=True)
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"Download failed after {max_retries} retries: {e}")
                
                wait_time = Config.RETRY_DELAY_BASE ** attempt
                self.log_warning(f"Download failed, retrying in {wait_time} seconds ({attempt + 1}/{max_retries}): {e}")
                time.sleep(wait_time)
        
        raise NetworkError("Download retry attempts exhausted")
    
    def download_papers(self, papers: List[Paper]) -> None:
        """Batch download papers
        
        Args:
            papers: List of papers
        """
        if not papers:
            self.log_info("No papers found")
            return
        
        self.log_info(f"Found {len(papers)} papers, starting download...")
        
        # Reset statistics
        self.stats = DownloadStats()
        self.stats.total_papers = len(papers)
        
        start_time = time.time()
        
        for i, paper in enumerate(papers, 1):
            self.log_info(f"[{i}/{len(papers)}] ", end="")
            self.download_pdf(paper)
            
            # Add delay to avoid too frequent requests
            if i < len(papers):
                time.sleep(Config.REQUEST_DELAY)
        
        # Calculate download time
        self.stats.download_time_seconds = time.time() - start_time
        
        self.log_info(f"Download completed! {self.stats}")
        self.log_info(f"Files saved in: {self.download_dir}")
        
        if self.stats.total_size_mb > 0:
            self.log_info(f"Average download speed: {self.stats.average_speed_mbps:.2f} MB/s")
    
    def generate_summary(self, papers: List[Paper]) -> None:
        """Generate download summary document
        
        Args:
            papers: List of papers
        """
        if not papers:
            return
        
        # Generate timestamped filename, accurate to minute
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        summary_file = self.download_dir / f"download_summary_{timestamp}.md"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("# ArXiv AI Paper Download Summary\n\n")
                f.write(f"## Download Time\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"## Statistics\n")
                f.write(f"- Total papers: {self.stats.total_papers}\n")
                f.write(f"- Successfully downloaded: {self.stats.successful_downloads}\n")
                f.write(f"- Failed downloads: {self.stats.failed_downloads}\n")
                f.write(f"- Skipped downloads: {self.stats.skipped_downloads}\n")
                f.write(f"- Success rate: {self.stats.success_rate:.1%}\n")
                if self.stats.total_size_mb > 0:
                    f.write(f"- Total size: {self.stats.total_size_mb:.2f} MB\n")
                    f.write(f"- Average speed: {self.stats.average_speed_mbps:.2f} MB/s\n")
                f.write("\n## Paper List\n\n")
                
                for i, paper in enumerate(papers, 1):
                    f.write(f"### {i}. {paper.title}\n")
                    f.write(f"- **Paper ID**: {paper.id}\n")
                    f.write(f"- **Authors**: {paper.authors_str}\n")
                    f.write(f"- **Categories**: {paper.categories_str}\n")
                    f.write(f"- **Published**: {paper.published}\n")
                    f.write(f"- **Abstract**: {paper.short_abstract}\n")
                    
                    # Determine the actual filename
                    clean_title = sanitize_filename(paper.title)
                    filename = f"{clean_title}.pdf"
                    filepath = self.download_dir / filename
                    
                    # Check if there's a file with ID suffix
                    if not filepath.exists():
                        filepath_with_id = self.download_dir / f"{clean_title}_{paper.id}.pdf"
                        if filepath_with_id.exists():
                            filename = f"{clean_title}_{paper.id}.pdf"
                    
                    f.write(f"- **File**: {filename}\n\n")
            
            self.log_info(f"Summary document generated: {summary_file}")
            
        except Exception as e:
            self.log_error(f"Failed to generate summary document: {e}")
    
    def download_paper_by_id(self, paper_id: str) -> bool:
        """Download a single paper by paper ID
        
        Args:
            paper_id: ArXiv paper ID (e.g.: 2301.00001 or 2301.00001v1)
        
        Returns:
            Whether download was successful
        """
        try:
            # Remove version number (if exists)
            # ArXiv ID format: YYMM.NNNNN[vN]
            clean_paper_id = paper_id
            if 'v' in paper_id:
                clean_paper_id = paper_id.split('v')[0]
            
            # Build search query for exact ID search
            query = f"id:{clean_paper_id}"
            
            self.log_info(f"Searching paper ID: {paper_id} (cleaned: {clean_paper_id})")
            
            # Search papers
            papers = self.search_papers(query=query, max_results=1)
            
            if not papers:
                self.log_error(f"Paper ID not found: {paper_id} (search ID: {clean_paper_id})")
                return False
            
            paper = papers[0]
            
            # Download paper
            success = self.download_pdf(paper)
            
            if success:
                self.log_info(f"Paper downloaded successfully: {paper.title}")
            else:
                self.log_error(f"Paper download failed: {paper.title}")
            
            return success
            
        except Exception as e:
            self.log_error(f"Error occurred while downloading paper {paper_id}: {e}")
            return False
    
    def _paper_to_dict(self, paper: Paper) -> Dict[str, Any]:
        """Convert Paper object to dictionary"""
        return {
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'pdf_url': paper.pdf_url,
            'published': paper.published,
            'categories': paper.categories
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='ArXiv AI Paper Downloader - Refactored Version')
    parser.add_argument('--query', default=Config.DEFAULT_QUERY, help=f'Search query (default: {Config.DEFAULT_QUERY})')
    parser.add_argument('--date-from', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--date-to', help='End date (YYYY-MM-DD)')
    parser.add_argument('--max-results', type=int, default=Config.DEFAULT_MAX_RESULTS, 
                       help=f'Maximum number of results (default: {Config.DEFAULT_MAX_RESULTS})')
    parser.add_argument('--download-dir', default=Config.DEFAULT_DOWNLOAD_DIR, help='Download directory')
    parser.add_argument('--today', action='store_true', help='Download today\'s papers')
    parser.add_argument('--yesterday', action='store_true', help='Download yesterday\'s papers')
    parser.add_argument('--last-week', action='store_true', help='Download papers from the last week')
    parser.add_argument('--clear-cache', action='store_true', help='Clear expired cache')
    parser.add_argument('--cache-stats', action='store_true', help='Show cache statistics')
    
    args = parser.parse_args()
    
    try:
        # Create downloader instance
        downloader = ArxivDownloader(args.download_dir)
        
        # Handle cache-related commands
        if args.clear_cache:
            downloader.cache_manager.clear_expired_cache()
            return
        
        if args.cache_stats:
            stats = downloader.cache_manager.get_cache_stats()
            print(f"Cache statistics: {stats['paper_cache_count']} paper caches, {stats['search_cache_count']} search caches")
            return
        
        # Handle shortcut date options
        if args.today:
            today = datetime.now().strftime('%Y-%m-%d')
            args.date_from = today
            args.date_to = today
        elif args.yesterday:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            args.date_from = yesterday
            args.date_to = yesterday
        elif args.last_week:
            today = datetime.now()
            week_ago = today - timedelta(days=7)
            args.date_from = week_ago.strftime('%Y-%m-%d')
            args.date_to = today.strftime('%Y-%m-%d')
        
        # Search papers
        papers = downloader.search_papers(
            query=args.query,
            date_from=args.date_from,
            date_to=args.date_to,
            max_results=args.max_results
        )
        
        if papers:
            # Download papers
            downloader.download_papers(papers)
            
            # Generate summary
            downloader.generate_summary(papers)
        else:
            downloader.log_info("No papers found matching the criteria")
    
    except (ValidationError, NetworkError, ParseError, FileOperationError) as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nUser interrupted download")
        return 1
    except Exception as e:
        print(f"Unknown error: {e}")
        return 1
    
    return 0

def cli_main():
    """CLI entry point"""
    from cli import main as cli_main_func
    cli_main_func()

if __name__ == "__main__":
    # If running this file directly, use the original main function
    # To use CLI, run: python -m cli
    exit(main())