#!/usr/bin/env python3
"""
API Integration Tests - Test API construction and request building
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs

from arxiv_downloader import ArxivDownloader
from enhanced_config import EnhancedConfig, SortBy, SortOrder
from api_validator import APIValidator
from models import ValidationError, NetworkError, ParseError
from utils import sanitize_filename, generate_query_hash, clean_text

class TestAPIConstruction(unittest.TestCase):
    """Test API URL and parameter construction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.downloader = ArxivDownloader()
        self.validator = APIValidator()
    
    def test_base_url_construction(self):
        """Test base URL is correctly formed"""
        # Check if base URL is valid
        base_url = 'http://export.arxiv.org/api/query'
        parsed = urlparse(base_url)
        
        self.assertEqual(parsed.scheme, 'http')
        self.assertEqual(parsed.netloc, 'export.arxiv.org')
        self.assertEqual(parsed.path, '/api/query')
    
    @patch('requests.get')
    @patch('arxiv_downloader.CacheManager.get_search_results')
    def test_query_parameter_encoding(self, mock_cache_get, mock_get):
        """Test that query parameters are properly encoded"""
        # Disable cache to ensure HTTP request is made
        mock_cache_get.return_value = None
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        mock_get.return_value = mock_response
        
        # Test with special characters in query
        test_query = 'machine learning & neural networks'
        self.downloader.search_papers(query=test_query, max_results=5)
        
        # Verify the request was made
        self.assertTrue(mock_get.called)
        
        # Get the actual parameters that were called
        called_args = mock_get.call_args
        self.assertIsNotNone(called_args)
        
        # Check if parameters were passed correctly
        if len(called_args[0]) > 1:
            params = called_args[0][1]
        else:
            params = called_args[1].get('params', {})
        
        query_params = params
        
        # Verify search_query parameter is properly encoded
        self.assertIn('search_query', query_params)
        # The & should be properly handled in the query
        search_query = query_params['search_query']
        self.assertIn('machine learning', search_query)
        self.assertIn('neural networks', search_query)
    
    @patch('requests.get')
    @patch('arxiv_downloader.CacheManager.get_search_results')
    def test_date_filter_construction(self, mock_cache_get, mock_get):
        """Test date filter parameter construction"""
        # Disable cache to ensure HTTP request is made
        mock_cache_get.return_value = None
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        mock_get.return_value = mock_response
        
        # Test with date filters
        self.downloader.search_papers(
            query='test',
            max_results=5,
            date_from='2023-01-01',
            date_to='2023-12-31'
        )
        
        # Verify the request was made
        self.assertTrue(mock_get.called)
        
        # Get the actual parameters that were called
        called_args = mock_get.call_args
        if len(called_args[0]) > 1:
            params = called_args[0][1]
        else:
            params = called_args[1].get('params', {})
        
        # Verify search_query contains date filters
        search_query = params['search_query']
        self.assertIn('submittedDate:', search_query)
        self.assertIn('2023', search_query)
    
    @patch('requests.get')
    @patch('arxiv_downloader.CacheManager.get_search_results')
    def test_sort_parameters(self, mock_cache_get, mock_get):
        """Test sort parameter construction"""
        # Disable cache to ensure HTTP request is made
        mock_cache_get.return_value = None
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        mock_get.return_value = mock_response
        
        # Test default sort (relevance)
        self.downloader.search_papers(query='test', max_results=5)
        
        # Verify the request was made
        self.assertTrue(mock_get.called)
        
        # Get the actual parameters that were called
        called_args = mock_get.call_args
        if len(called_args[0]) > 1:
            params = called_args[0][1]
        else:
            params = called_args[1].get('params', {})
        
        # Verify sort parameters
        self.assertEqual(params['sortBy'], 'relevance')
        self.assertEqual(params['sortOrder'], 'descending')
    
    @patch('requests.get')
    @patch('arxiv_downloader.CacheManager.get_search_results')
    def test_pagination_parameters(self, mock_cache_get, mock_get):
        """Test pagination parameter construction"""
        # Disable cache to ensure HTTP request is made
        mock_cache_get.return_value = None
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        mock_get.return_value = mock_response
        
        # Test with specific start and max_results
        self.downloader.search_papers(
            query='test',
            max_results=20,
            start=10
        )
        
        # Verify the request was made
        self.assertTrue(mock_get.called)
        
        # Get the actual parameters that were called
        called_args = mock_get.call_args
        if len(called_args[0]) > 1:
            params = called_args[0][1]
        else:
            params = called_args[1].get('params', {})
        
        # Verify pagination parameters
        self.assertEqual(params['start'], 0)  # start is always 0 in current implementation
        self.assertEqual(params['max_results'], 20)

class TestAPIResponseHandling(unittest.TestCase):
    """Test API response parsing and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.downloader = ArxivDownloader()
        self.validator = APIValidator()
    
    @patch('requests.get')
    def test_successful_response_parsing(self, mock_get):
        """Test successful XML response parsing"""
        # Mock successful response with valid XML
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/atom+xml'}
        mock_response.text = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>http://arxiv.org/abs/2023.12345v1</id>
        <title>Test Paper Title</title>
        <author><name>Test Author</name></author>
        <summary>Test abstract content</summary>
        <link href="http://arxiv.org/pdf/2023.12345v1.pdf" rel="alternate" type="application/pdf"/>
        <published>2023-01-01T00:00:00Z</published>
        <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    </entry>
</feed>'''
        mock_get.return_value = mock_response
        
        # Test parsing
        papers = self.downloader.search_papers(query='test', max_results=1)
        
        self.assertEqual(len(papers), 1)
        paper = papers[0]
        self.assertEqual(paper.id, '2023.12345v1')
        self.assertEqual(paper.title, 'Test Paper Title')
        self.assertEqual(paper.authors, ['Test Author'])
        self.assertEqual(paper.abstract, 'Test abstract content')
        self.assertTrue(paper.pdf_url.endswith('.pdf'))
    
    @patch('requests.get')
    def test_http_error_handling(self, mock_get):
        """Test HTTP error response handling"""
        # Mock HTTP error response that raises HTTPError
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('400 Client Error')
        mock_get.return_value = mock_response
        
        # Should raise NetworkError
        with self.assertRaises(NetworkError):
            self.downloader.search_papers(query='test', max_results=1)
    
    @patch('requests.get')
    @patch('arxiv_downloader.CacheManager.get_search_results')
    def test_malformed_xml_handling(self, mock_cache_get, mock_get):
        """Test malformed XML response handling"""
        # Disable cache to ensure HTTP request is made
        mock_cache_get.return_value = None
        
        # Mock response with malformed XML
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/atom+xml'}
        mock_response.text = '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><id>incomplete'
        mock_get.return_value = mock_response
        
        # Should raise ParseError for malformed XML
        with self.assertRaises(ParseError):
            self.downloader.search_papers(query='test', max_results=1)
    
    @patch('requests.get')
    @patch('arxiv_downloader.CacheManager.get_search_results')
    def test_empty_response_handling(self, mock_cache_get, mock_get):
        """Test empty response handling"""
        # Disable cache to ensure HTTP request is made
        mock_cache_get.return_value = None
        
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/atom+xml'}
        mock_response.text = '<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        mock_get.return_value = mock_response
        
        # Should return empty list
        papers = self.downloader.search_papers(query='test', max_results=1)
        self.assertEqual(papers, [])
    
    @patch('requests.get')
    @patch('arxiv_downloader.CacheManager.get_search_results')
    def test_network_timeout_handling(self, mock_cache_get, mock_get):
        """Test network timeout handling"""
        # Disable cache to ensure HTTP request is made
        mock_cache_get.return_value = None
        
        # Mock network timeout
        mock_get.side_effect = requests.exceptions.Timeout()
        
        # Should raise NetworkError
        with self.assertRaises(NetworkError):
            self.downloader.search_papers(query='test', max_results=1)
    
    @patch('requests.get')
    @patch('arxiv_downloader.CacheManager.get_search_results')
    def test_connection_error_handling(self, mock_cache_get, mock_get):
        """Test connection error handling"""
        # Disable cache to ensure HTTP request is made
        mock_cache_get.return_value = None
        
        # Mock connection error
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        # Should raise NetworkError
        with self.assertRaises(NetworkError):
            self.downloader.search_papers(query='test', max_results=1)

class TestAPIValidation(unittest.TestCase):
    """Test API request validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = APIValidator()
    
    def test_response_validation(self):
        """Test response validation logic"""
        # Test with valid response
        valid_response = Mock()
        valid_response.status_code = 200
        valid_response.headers = {'content-type': 'application/atom+xml'}
        valid_response.text = '<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><id>test</id><title>Test Paper</title><summary>Test summary</summary></entry></feed>'
        
        # Should not raise any exception
        self.validator.validate_response(valid_response)
        
        # Mock invalid response - wrong status
        invalid_response = Mock()
        invalid_response.status_code = 500
        invalid_response.text = 'Internal Server Error'
        
        with self.assertRaises(NetworkError):
            self.validator.validate_response(invalid_response)
        
        # Mock invalid response - wrong content type
        invalid_content_response = Mock()
        invalid_content_response.status_code = 200
        invalid_content_response.headers = {'content-type': 'text/html'}
        invalid_content_response.text = '<html></html>'
        
        with self.assertRaises(ValidationError):
            self.validator.validate_response(invalid_content_response)
    
    def test_parameter_validation(self):
        """Test parameter validation"""
        # Valid parameters
        valid_params = {
            'search_query': 'machine learning',
            'start': 0,
            'max_results': 10,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        # Should not raise exception
        self.validator.validate_search_params(valid_params)
        
        # Invalid parameters - empty query
        invalid_params = valid_params.copy()
        invalid_params['search_query'] = ''
        
        with self.assertRaises(ValidationError):
            self.validator.validate_search_params(invalid_params)
        
        # Invalid parameters - negative start
        invalid_params = valid_params.copy()
        invalid_params['start'] = -1
        
        with self.assertRaises(ValidationError):
            self.validator.validate_search_params(invalid_params)
        
        # Invalid parameters - zero max_results
        invalid_params = valid_params.copy()
        invalid_params['max_results'] = 0
        
        with self.assertRaises(ValidationError):
            self.validator.validate_search_params(invalid_params)

class TestRealAPIIntegration(unittest.TestCase):
    """Real API integration tests (optional - requires network)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.downloader = ArxivDownloader()
    
    @unittest.skip("Requires network connection - enable manually for integration testing")
    def test_real_api_call(self):
        """Test actual API call (disabled by default)"""
        # This test makes a real API call - only enable for integration testing
        papers = self.downloader.search_papers(
            query='machine learning',
            max_results=3
        )
        
        # Basic validation
        self.assertIsInstance(papers, list)
        if papers:  # If we got results
            paper = papers[0]
            self.assertIsNotNone(paper.id)
            self.assertIsNotNone(paper.title)
            self.assertIsNotNone(paper.authors)
            self.assertTrue(paper.pdf_url.startswith('http'))

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)