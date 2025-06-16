import os
import re
import time
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from dataclasses import dataclass
from enum import Enum

from models import Paper, ValidationError, NetworkError, ParseError
from config import Config
from logger import get_logger
from cache import CacheManager
from utils import (
    sanitize_filename, 
    is_valid_date_format, 
    generate_query_hash
)

class SearchField(Enum):
    """Search field enumeration"""
    ALL = "all"
    TITLE = "ti"
    AUTHOR = "au"
    ABSTRACT = "abs"
    COMMENT = "co"
    JOURNAL = "jr"
    CATEGORY = "cat"
    REPORT_NUMBER = "rn"
    ID = "id"

class SortBy(Enum):
    """Sort by enumeration"""
    RELEVANCE = "relevance"
    LAST_UPDATED_DATE = "lastUpdatedDate"
    SUBMITTED_DATE = "submittedDate"

class SortOrder(Enum):
    """Sort order enumeration"""
    ASCENDING = "ascending"
    DESCENDING = "descending"

@dataclass
class DownloadStats:
    """Download statistics"""
    total_papers: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    
    def add_success(self):
        self.successful_downloads += 1
    
    def add_failure(self):
        self.failed_downloads += 1
    
    @property
    def success_rate(self) -> float:
        if self.total_papers == 0:
            return 0.0
        return (self.successful_downloads / self.total_papers) * 100

class ArxivDownloader:
    """ArXiv paper downloader with enhanced search capabilities"""
    
    def __init__(self, download_dir: str = Config.DEFAULT_DOWNLOAD_DIR):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_url = "http://export.arxiv.org/api/query"
        self.logger = get_logger()
        self.cache_manager = CacheManager()
        self.stats = DownloadStats()
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def search_papers(self, query: str = Config.DEFAULT_QUERY,
                     date_from: Optional[str] = None, 
                     date_to: Optional[str] = None, 
                     max_results: int = Config.DEFAULT_MAX_RESULTS,
                     categories: List[str] = None) -> List[Paper]:
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
        search_query = self._build_search_query(query, date_from, date_to)
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        self.log_info("Searching ArXiv papers...")
        
        try:
            response = self._make_request_with_retry(self.base_url, params)
            papers = self._parse_arxiv_response(response.text)
            
            paper_data_list = [self._paper_to_dict(paper) for paper in papers]
            self.cache_manager.save_search_results(query_hash, paper_data_list)
            
            self.log_info(f"Search completed, found {len(papers)} papers")
            return papers
             
        except requests.RequestException as e:
            raise NetworkError(f"Search request failed: {e}")
    
    def _generate_cache_key(self, query: str, max_results: int, 
                           date_from: str = None, date_to: str = None,
                           categories: List[str] = None) -> str:
        """Generate cache key for search parameters"""
        key_parts = [query, str(max_results)]
        if date_from:
            key_parts.append(f"from:{date_from}")
        if date_to:
            key_parts.append(f"to:{date_to}")
        if categories:
            cats_str = ",".join(sorted(categories))
            key_parts.append(f"cats:{cats_str}")
        return "|".join(key_parts)
    
    def _build_search_query(self, query: str, date_from: str = None, date_to: str = None) -> str:
        """Build search query with date filters"""
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
        
        return search_query
    
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
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            papers = []
            entries = root.findall('atom:entry', namespaces)
            
            for entry in entries:
                try:
                    paper = self._parse_entry(entry, namespaces)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    self.log_warning(f"Failed to parse entry: {e}")
                    continue
            
            return papers
            
        except ET.ParseError as e:
            raise ParseError(f"XML parsing failed: {e}")
    
    def _parse_entry(self, entry, namespaces: Dict[str, str]) -> Optional[Paper]:
        """Parse single entry from ArXiv response
        
        Args:
            entry: XML entry element
            namespaces: XML namespaces
        
        Returns:
            Paper object or None if parsing failed
        """
        try:
            # Extract basic information
            title = entry.find('atom:title', namespaces)
            title_text = title.text.strip().replace('\n', ' ') if title is not None else "Unknown Title"
            
            summary = entry.find('atom:summary', namespaces)
            summary_text = summary.text.strip().replace('\n', ' ') if summary is not None else ""
            
            # Extract ArXiv ID from URL
            id_elem = entry.find('atom:id', namespaces)
            if id_elem is None:
                return None
            
            arxiv_id = id_elem.text.split('/')[-1]
            
            # Extract authors
            authors = []
            author_elements = entry.findall('atom:author', namespaces)
            for author_elem in author_elements:
                name_elem = author_elem.find('atom:name', namespaces)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            
            # Extract categories
            categories = []
            category_elements = entry.findall('atom:category', namespaces)
            for cat_elem in category_elements:
                term = cat_elem.get('term')
                if term:
                    categories.append(term)
            
            # Extract publication date
            published = entry.find('atom:published', namespaces)
            published_text = published.text if published is not None else ""
            
            # Extract PDF URL
            pdf_url = ""
            link_elements = entry.findall('atom:link', namespaces)
            for link in link_elements:
                if link.get('type') == 'application/pdf':
                    pdf_url = link.get('href', '')
                    break
            
            return Paper(
                id=arxiv_id,
                title=title_text,
                authors=authors,
                abstract=summary_text,
                categories=categories,
                published=published_text,
                pdf_url=pdf_url
            )
            
        except Exception as e:
            self.log_warning(f"Failed to parse paper entry: {e}")
            return None
    
    def download_pdf(self, paper: Paper) -> bool:
        """Download single paper PDF
        
        Args:
            paper: Paper object
        
        Returns:
            Whether download was successful
        """
        try:
            if not paper.pdf_url:
                self.log_error(f"No PDF URL found for paper: {paper.title}")
                return False
            
            # Generate filename
            clean_title = sanitize_filename(paper.title)
            filename = f"{clean_title}_{paper.id}.pdf"
            filepath = self.download_dir / filename
            
            # Check if file already exists
            if filepath.exists():
                self.log_info(f"File already exists, skipping: {filename}")
                return True
            
            self.log_info(f"Downloading: {paper.title}")
            
            # Download file
            response = self._download_with_retry(paper.pdf_url)
            
            # Save file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.log_info(f"Downloaded successfully: {filename}")
            self.stats.add_success()
            return True
            
        except Exception as e:
            self.log_error(f"Download failed for {paper.title}: {e}")
            # Clean up partial file
            try:
                if 'filepath' in locals() and filepath.exists():
                    filepath.unlink()
            except Exception:
                pass
            
            self.stats.add_failure()
            return False
    
    def download_paper_by_id(self, paper_id: str) -> bool:
        """Download paper by ArXiv ID
        
        Args:
            paper_id: ArXiv paper ID
        
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
            self.log_error(f"Download by ID failed for {paper_id}: {e}")
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
        
        for i, paper in enumerate(papers, 1):
            self.log_info(f"Processing paper {i}/{len(papers)}: {paper.title}")
            self.download_pdf(paper)
        
        # Print statistics
        self.log_info(f"Download completed. Success: {self.stats.successful_downloads}, "
                     f"Failed: {self.stats.failed_downloads}, "
                     f"Success rate: {self.stats.success_rate:.1f}%")
    
    def _paper_to_dict(self, paper: Paper) -> Dict[str, Any]:
        """Convert Paper object to dictionary for caching
        
        Args:
            paper: Paper object
        
        Returns:
            Dictionary representation
        """
        return {
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'categories': paper.categories,
            'published': paper.published,
            'pdf_url': paper.pdf_url
        }