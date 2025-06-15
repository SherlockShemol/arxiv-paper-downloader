#!/usr/bin/env python3
"""
Enhanced ArXiv API Client

This module provides an improved interface to the arXiv API based on the official documentation.
It includes comprehensive query syntax support, proper parameter validation, and robust error handling.

Reference: https://info.arxiv.org/help/api/user-manual.html
"""

import requests
import xml.etree.ElementTree as ET
import time
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode
from dataclasses import dataclass
from enum import Enum

from models import Paper, NetworkError, ValidationError, ParseError
from logger import LoggerMixin
from config import Config


class SortBy(Enum):
    """Sort criteria for arXiv API results"""
    RELEVANCE = "relevance"
    LAST_UPDATED_DATE = "lastUpdatedDate"
    SUBMITTED_DATE = "submittedDate"


class SortOrder(Enum):
    """Sort order for arXiv API results"""
    ASCENDING = "ascending"
    DESCENDING = "descending"


class SearchField(Enum):
    """Search fields supported by arXiv API"""
    ALL = "all"  # All fields
    TITLE = "ti"  # Title
    AUTHOR = "au"  # Author
    ABSTRACT = "abs"  # Abstract
    COMMENT = "co"  # Comment
    JOURNAL_REF = "jr"  # Journal reference
    CATEGORY = "cat"  # Subject category
    REPORT_NUM = "rn"  # Report number
    ID = "id"  # arXiv ID
    SUBMITTED_DATE = "submittedDate"  # Submission date
    LAST_UPDATED_DATE = "lastUpdatedDate"  # Last update date


@dataclass
class SearchQuery:
    """Represents a structured search query for arXiv API"""
    terms: List[str]
    field: SearchField = SearchField.ALL
    operator: str = "AND"  # AND, OR, ANDNOT
    
    def to_string(self) -> str:
        """Convert search query to arXiv API query string"""
        if not self.terms:
            return ""
        
        field_prefix = f"{self.field.value}:" if self.field != SearchField.ALL else ""
        
        if len(self.terms) == 1:
            return f"{field_prefix}{self.terms[0]}"
        
        # For multiple terms, wrap each in quotes and join with operator
        quoted_terms = [f'"{term}"' if ' ' in term else term for term in self.terms]
        return f"{field_prefix}({f' {self.operator} '.join(quoted_terms)})"


@dataclass
class DateRange:
    """Represents a date range for filtering arXiv papers"""
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    field: SearchField = SearchField.SUBMITTED_DATE
    
    def to_query_string(self) -> str:
        """Convert date range to arXiv API query string"""
        if not self.start_date and not self.end_date:
            return ""
        
        # Convert YYYY-MM-DD to YYYYMMDD format
        start = self.start_date.replace('-', '') + '0000' if self.start_date else '*'
        end = self.end_date.replace('-', '') + '2359' if self.end_date else '*'
        
        return f"{self.field.value}:[{start}+TO+{end}]"


class EnhancedArxivAPI(LoggerMixin):
    """Enhanced ArXiv API client with comprehensive query support"""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    # arXiv API namespaces
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom',
        'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
    }
    
    def __init__(self, 
                 timeout: int = Config.API_TIMEOUT,
                 max_retries: int = Config.MAX_RETRIES,
                 retry_delay: float = Config.RETRY_DELAY_BASE,
                 user_agent: str = "Enhanced-ArXiv-Client/1.0"):
        """Initialize the enhanced arXiv API client
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay for exponential backoff
            user_agent: User agent string for requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/atom+xml'
        })
    
    def search_papers(self,
                     query: Union[str, SearchQuery, List[SearchQuery]] = None,
                     id_list: Optional[List[str]] = None,
                     date_range: Optional[DateRange] = None,
                     categories: Optional[List[str]] = None,
                     max_results: int = Config.DEFAULT_MAX_RESULTS,
                     start: int = 0,
                     sort_by: SortBy = SortBy.RELEVANCE,
                     sort_order: SortOrder = SortOrder.DESCENDING) -> List[Paper]:
        """Search arXiv papers with enhanced query capabilities
        
        Args:
            query: Search query (string, SearchQuery object, or list of SearchQuery objects)
            id_list: List of arXiv IDs to retrieve
            date_range: Date range filter
            categories: List of subject categories to filter by
            max_results: Maximum number of results to return
            start: Starting index for pagination
            sort_by: Sort criterion
            sort_order: Sort order
            
        Returns:
            List of Paper objects
            
        Raises:
            ValidationError: Invalid parameters
            NetworkError: Network request failed
            ParseError: XML parsing failed
        """
        # Validate parameters
        self._validate_search_params(query, id_list, max_results, start, categories)
        
        # Build query parameters
        params = self._build_query_params(
            query=query,
            id_list=id_list,
            date_range=date_range,
            categories=categories,
            max_results=max_results,
            start=start,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Make API request
        response_text = self._make_request(params)
        
        # Parse response
        papers = self._parse_response(response_text)
        
        self.log_info(f"Retrieved {len(papers)} papers from arXiv API")
        return papers
    
    def get_paper_by_id(self, arxiv_id: str, version: Optional[int] = None) -> Optional[Paper]:
        """Get a specific paper by arXiv ID
        
        Args:
            arxiv_id: arXiv paper ID
            version: Specific version number (optional)
            
        Returns:
            Paper object or None if not found
        """
        full_id = f"{arxiv_id}v{version}" if version else arxiv_id
        papers = self.search_papers(id_list=[full_id], max_results=1)
        return papers[0] if papers else None
    
    def _validate_search_params(self, 
                               query: Union[str, SearchQuery, List[SearchQuery]], 
                               id_list: Optional[List[str]], 
                               max_results: int, 
                               start: int,
                               categories: Optional[List[str]] = None) -> None:
        """Validate search parameters"""
        if not query and not id_list and not categories:
            raise ValidationError("Either query, id_list, or categories must be provided")
        
        if max_results <= 0:
            raise ValidationError(f"max_results must be positive: {max_results}")
        
        if start < 0:
            raise ValidationError(f"start must be non-negative: {start}")
        
        # Validate arXiv IDs format
        if id_list:
            for arxiv_id in id_list:
                if not self._is_valid_arxiv_id(arxiv_id):
                    raise ValidationError(f"Invalid arXiv ID format: {arxiv_id}")
    
    def _is_valid_arxiv_id(self, arxiv_id: str) -> bool:
        """Validate arXiv ID format"""
        import re
        # Support both old and new arXiv ID formats
        old_format = re.match(r'^[a-z-]+/\d{7}(v\d+)?$', arxiv_id)
        new_format = re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', arxiv_id)
        return bool(old_format or new_format)
    
    def _build_query_params(self, **kwargs) -> Dict[str, Any]:
        """Build query parameters for arXiv API request"""
        params = {}
        
        # Handle search query
        query_parts = []
        
        if kwargs.get('query'):
            query = kwargs['query']
            if isinstance(query, str):
                query_parts.append(query)
            elif isinstance(query, SearchQuery):
                query_parts.append(query.to_string())
            elif isinstance(query, list):
                query_parts.extend([q.to_string() for q in query if isinstance(q, SearchQuery)])
        
        # Add date range filter
        if kwargs.get('date_range'):
            date_query = kwargs['date_range'].to_query_string()
            if date_query:
                query_parts.append(date_query)
        
        # Add category filter
        if kwargs.get('categories'):
            cat_queries = [f"cat:{cat}" for cat in kwargs['categories']]
            if len(cat_queries) == 1:
                query_parts.append(cat_queries[0])
            else:
                query_parts.append(f"({' OR '.join(cat_queries)})")
        
        # Combine query parts
        if query_parts:
            params['search_query'] = ' AND '.join(query_parts)
        
        # Handle ID list
        if kwargs.get('id_list'):
            params['id_list'] = ','.join(kwargs['id_list'])
        
        # Add pagination and sorting
        params.update({
            'start': kwargs.get('start', 0),
            'max_results': kwargs.get('max_results', Config.DEFAULT_MAX_RESULTS),
            'sortBy': kwargs.get('sort_by', SortBy.RELEVANCE).value,
            'sortOrder': kwargs.get('sort_order', SortOrder.DESCENDING).value
        })
        
        return params
    
    def _make_request(self, params: Dict[str, Any]) -> str:
        """Make HTTP request to arXiv API with retry logic"""
        url = f"{self.BASE_URL}?{urlencode(params)}"
        self.log_info(f"Making request to: {url}")
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.text
                
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise NetworkError(f"Request failed after {self.max_retries} attempts: {e}")
                
                wait_time = self.retry_delay ** attempt
                self.log_warning(f"Request failed, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(wait_time)
        
        raise NetworkError("Request retry attempts exhausted")
    
    def _parse_response(self, response_text: str) -> List[Paper]:
        """Parse arXiv API XML response"""
        try:
            root = ET.fromstring(response_text)
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse XML response: {e}")
        
        papers = []
        
        # Find all entry elements
        entries = root.findall('atom:entry', self.NAMESPACES)
        
        for entry in entries:
            try:
                paper = self._parse_paper_entry(entry)
                if paper:
                    papers.append(paper)
            except Exception as e:
                self.log_warning(f"Failed to parse paper entry: {e}")
                continue
        
        return papers
    
    def _parse_paper_entry(self, entry: ET.Element) -> Optional[Paper]:
        """Parse a single paper entry from XML"""
        try:
            # Extract basic information
            paper_id = self._extract_text(entry, 'atom:id', self.NAMESPACES)
            if paper_id:
                # Extract arXiv ID from URL
                paper_id = paper_id.split('/')[-1]
            
            title = self._extract_text(entry, 'atom:title', self.NAMESPACES)
            if title:
                title = ' '.join(title.split())  # Clean whitespace
            
            summary = self._extract_text(entry, 'atom:summary', self.NAMESPACES)
            if summary:
                summary = ' '.join(summary.split())  # Clean whitespace
            
            published = self._extract_text(entry, 'atom:published', self.NAMESPACES)
            updated = self._extract_text(entry, 'atom:updated', self.NAMESPACES)
            
            # Extract authors
            authors = []
            author_elements = entry.findall('atom:author', self.NAMESPACES)
            for author_elem in author_elements:
                name = self._extract_text(author_elem, 'atom:name', self.NAMESPACES)
                if name:
                    authors.append(name)
            
            # Extract categories
            categories = []
            category_elements = entry.findall('atom:category', self.NAMESPACES)
            for cat_elem in category_elements:
                term = cat_elem.get('term')
                if term:
                    categories.append(term)
            
            # Extract PDF URL
            pdf_url = None
            link_elements = entry.findall('atom:link', self.NAMESPACES)
            for link_elem in link_elements:
                if link_elem.get('type') == 'application/pdf':
                    pdf_url = link_elem.get('href')
                    break
            
            # Extract arXiv-specific metadata
            comment = self._extract_text(entry, 'arxiv:comment', self.NAMESPACES)
            journal_ref = self._extract_text(entry, 'arxiv:journal_ref', self.NAMESPACES)
            doi = self._extract_text(entry, 'arxiv:doi', self.NAMESPACES)
            
            # Create Paper object
            return Paper(
                id=paper_id or "",
                title=title or "",
                authors=authors,
                abstract=summary or "",
                pdf_url=pdf_url or "",
                published=published or "",
                categories=categories,
                comment=comment,
                journal_ref=journal_ref,
                doi=doi
            )
            
        except Exception as e:
            self.log_warning(f"Error parsing paper entry: {e}")
            return None
    
    def _extract_text(self, element: ET.Element, xpath: str, namespaces: Dict[str, str]) -> Optional[str]:
        """Extract text content from XML element"""
        found = element.find(xpath, namespaces)
        return found.text.strip() if found is not None and found.text else None
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions for common use cases
def search_by_keyword(keyword: str, 
                     field: SearchField = SearchField.ALL,
                     max_results: int = 10) -> List[Paper]:
    """Search papers by keyword in specified field"""
    with EnhancedArxivAPI() as api:
        query = SearchQuery(terms=[keyword], field=field)
        return api.search_papers(query=query, max_results=max_results)


def search_by_author(author_name: str, max_results: int = 10) -> List[Paper]:
    """Search papers by author name"""
    with EnhancedArxivAPI() as api:
        query = SearchQuery(terms=[author_name], field=SearchField.AUTHOR)
        return api.search_papers(query=query, max_results=max_results)


def search_by_category(category: str, 
                      date_range: Optional[DateRange] = None,
                      max_results: int = 10) -> List[Paper]:
    """Search papers by category with optional date range"""
    with EnhancedArxivAPI() as api:
        return api.search_papers(
            categories=[category],
            date_range=date_range,
            max_results=max_results,
            sort_by=SortBy.SUBMITTED_DATE,
            sort_order=SortOrder.DESCENDING
        )


def get_recent_papers(category: str = "cs.AI", days: int = 7, max_results: int = 20) -> List[Paper]:
    """Get recent papers from the last N days in specified category"""
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    date_range = DateRange(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    return search_by_category(category, date_range, max_results)