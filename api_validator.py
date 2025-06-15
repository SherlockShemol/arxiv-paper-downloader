#!/usr/bin/env python3
"""
API response validation utilities for enhanced error handling
"""

import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
import requests

from models import NetworkError, ParseError, ValidationError
from logger import LoggerMixin
from enhanced_config import EnhancedConfig

class APIValidator(LoggerMixin):
    """API response validator with comprehensive error checking"""
    
    def __init__(self):
        """Initialize validator"""
        self.config = EnhancedConfig()
    
    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response
        
        Args:
            response: HTTP response object
            
        Raises:
            NetworkError: If response is invalid
            ValidationError: If response format is invalid
        """
        # Check status code
        if response.status_code != 200:
            raise NetworkError(f"HTTP {response.status_code}: {response.reason}")
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        expected_types = self.config.EXPECTED_CONTENT_TYPES
        
        if not any(ct in content_type for ct in expected_types):
            self.log_warning(f"Unexpected content type: {content_type}")
        
        # Check response length
        if len(response.text) < self.config.MIN_RESPONSE_LENGTH:
            raise ValidationError(f"Response too short: {len(response.text)} bytes")
        
        # Check for ArXiv API errors in response
        self._check_arxiv_errors(response.text)
    
    def _check_arxiv_errors(self, response_text: str) -> None:
        """Check for ArXiv-specific errors in response
        
        Args:
            response_text: Response content
            
        Raises:
            ValidationError: If ArXiv API returns an error
        """
        try:
            root = ET.fromstring(response_text)
            
            # Check for error elements
            error_elements = root.findall('.//{http://www.w3.org/2005/Atom}error')
            if error_elements:
                error_msg = error_elements[0].text or "Unknown ArXiv API error"
                raise ValidationError(f"ArXiv API error: {error_msg}")
            
            # Check for empty results with error message
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            if not entries:
                # Check if this is due to an error or just no results
                title_elem = root.find('.//{http://www.w3.org/2005/Atom}title')
                if title_elem is not None and 'error' in title_elem.text.lower():
                    raise ValidationError(f"ArXiv search error: {title_elem.text}")
                
                self.log_info("Search returned no results")
        
        except ET.ParseError as e:
            raise ParseError(f"Invalid XML response: {e}")
    
    def validate_search_params(self, params: Dict[str, Any]) -> None:
        """Validate search parameters
        
        Args:
            params: Search parameters dictionary
            
        Raises:
            ValidationError: If parameters are invalid
        """
        required_params = ['search_query', 'start', 'max_results']
        
        for param in required_params:
            if param not in params:
                raise ValidationError(f"Missing required parameter: {param}")
        
        # Validate specific parameter values
        if not isinstance(params['start'], int) or params['start'] < 0:
            raise ValidationError("Start parameter must be a non-negative integer")
        
        if not isinstance(params['max_results'], int) or params['max_results'] <= 0:
            raise ValidationError("Max results must be a positive integer")
        
        if not params['search_query'] or not isinstance(params['search_query'], str):
            raise ValidationError("Search query must be a non-empty string")
        
        # Validate sort parameters if present
        if 'sortBy' in params:
            valid_sort_options = ['relevance', 'submittedDate', 'lastUpdatedDate']
            if params['sortBy'] not in valid_sort_options:
                raise ValidationError(f"Invalid sortBy value: {params['sortBy']}")
        
        if 'sortOrder' in params:
            valid_order_options = ['ascending', 'descending']
            if params['sortOrder'] not in valid_order_options:
                raise ValidationError(f"Invalid sortOrder value: {params['sortOrder']}")
    
    def suggest_fallback_params(self, original_params: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest fallback parameters if original request fails
        
        Args:
            original_params: Original parameters that failed
            
        Returns:
            Modified parameters with fallback options
        """
        fallback_params = original_params.copy()
        
        # If relevance sort failed, try submitted date
        if original_params.get('sortBy') == 'relevance':
            fallback_params['sortBy'] = self.config.FALLBACK_SORT_BY.value
            self.log_info("Falling back to submittedDate sorting")
        
        # Reduce max_results if it's too high
        if original_params.get('max_results', 0) > 100:
            fallback_params['max_results'] = 100
            self.log_info("Reducing max_results to 100")
        
        return fallback_params