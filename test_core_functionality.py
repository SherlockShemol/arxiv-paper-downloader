#!/usr/bin/env python3
"""
Unit tests for core functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path

from arxiv_downloader import ArxivDownloader
from models import Paper, ValidationError, NetworkError
from utils import sanitize_filename, generate_query_hash
from enhanced_config import EnhancedConfig, SortBy, SortOrder
from api_validator import APIValidator

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test invalid characters removal
        self.assertEqual(sanitize_filename('Test<>:"/\\|?*File'), 'TestFile')
        
        # Test whitespace normalization
        self.assertEqual(sanitize_filename('Test   Multiple   Spaces'), 'Test Multiple Spaces')
        
        # Test length limitation
        long_title = 'A' * 200
        result = sanitize_filename(long_title, max_length=50)
        self.assertEqual(len(result), 50)
        
        # Test empty string handling
        self.assertEqual(sanitize_filename(''), 'untitled')
        self.assertEqual(sanitize_filename('   '), 'untitled')
    
    def test_generate_query_hash(self):
        """Test query hash generation"""
        # Same parameters should generate same hash
        hash1 = generate_query_hash('machine learning', '2023-01-01', '2023-12-31', 10)
        hash2 = generate_query_hash('machine learning', '2023-01-01', '2023-12-31', 10)
        self.assertEqual(hash1, hash2)
        
        # Different parameters should generate different hashes
        hash3 = generate_query_hash('quantum computing', '2023-01-01', '2023-12-31', 10)
        self.assertNotEqual(hash1, hash3)

class TestEnhancedConfig(unittest.TestCase):
    """Test enhanced configuration"""
    
    def test_sort_enums(self):
        """Test sort enumeration values"""
        self.assertEqual(SortBy.RELEVANCE.value, 'relevance')
        self.assertEqual(SortBy.SUBMITTED_DATE.value, 'submittedDate')
        self.assertEqual(SortOrder.DESCENDING.value, 'descending')
    
    def test_get_search_params(self):
        """Test search parameters generation"""
        # Test default parameters
        params = EnhancedConfig.get_search_params()
        self.assertEqual(params['sortBy'], 'relevance')
        self.assertEqual(params['sortOrder'], 'descending')
        
        # Test custom parameters
        params = EnhancedConfig.get_search_params(
            sort_by=SortBy.SUBMITTED_DATE,
            sort_order=SortOrder.ASCENDING
        )
        self.assertEqual(params['sortBy'], 'submittedDate')
        self.assertEqual(params['sortOrder'], 'ascending')
    
    def test_directory_paths(self):
        """Test directory path generation"""
        # Test default paths
        download_dir = EnhancedConfig.get_download_dir()
        self.assertIsInstance(download_dir, Path)
        
        # Test custom paths
        custom_dir = EnhancedConfig.get_download_dir('/tmp/test')
        self.assertEqual(custom_dir, Path('/tmp/test'))
        
        # Test cache and log directories
        cache_dir = EnhancedConfig.get_cache_dir('/tmp/test')
        log_dir = EnhancedConfig.get_log_dir('/tmp/test')
        self.assertEqual(cache_dir, Path('arxiv_papers/.cache'))
        self.assertEqual(log_dir, Path('/tmp/test/logs'))

class TestAPIValidator(unittest.TestCase):
    """Test API validator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = APIValidator()
    
    def test_validate_search_params(self):
        """Test search parameter validation"""
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
        
        # Invalid parameters
        with self.assertRaises(ValidationError):
            self.validator.validate_search_params({'search_query': ''})
        
        with self.assertRaises(ValidationError):
            self.validator.validate_search_params({
                'search_query': 'test',
                'start': -1,
                'max_results': 10
            })
        
        with self.assertRaises(ValidationError):
            self.validator.validate_search_params({
                'search_query': 'test',
                'start': 0,
                'max_results': 0
            })
    
    def test_suggest_fallback_params(self):
        """Test fallback parameter suggestions"""
        original_params = {
            'search_query': 'test',
            'start': 0,
            'max_results': 200,
            'sortBy': 'relevance'
        }
        
        fallback_params = self.validator.suggest_fallback_params(original_params)
        
        # Should change sortBy to fallback option
        self.assertEqual(fallback_params['sortBy'], 'submittedDate')
        
        # Should reduce max_results
        self.assertEqual(fallback_params['max_results'], 100)

class TestPaperModel(unittest.TestCase):
    """Test Paper model"""
    
    def test_paper_creation(self):
        """Test paper object creation"""
        # Valid paper
        paper = Paper(
            id='2023.12345',
            title='Test Paper',
            authors=['Author One', 'Author Two'],
            abstract='Test abstract',
            pdf_url='http://arxiv.org/pdf/2023.12345.pdf',
            published='2023-01-01',
            categories=['cs.AI']
        )
        
        self.assertEqual(paper.id, '2023.12345')
        self.assertEqual(paper.title, 'Test Paper')
        self.assertEqual(len(paper.authors), 2)
    
    def test_paper_validation(self):
        """Test paper validation"""
        # Invalid paper - empty ID
        with self.assertRaises(ValidationError):
            Paper(
                id='',
                title='Test Paper',
                authors=['Author'],
                abstract='Abstract',
                pdf_url='http://arxiv.org/pdf/test.pdf',
                published='2023-01-01',
                categories=['cs.AI']
            )
        
        # Invalid paper - invalid URL
        with self.assertRaises(ValidationError):
            Paper(
                id='2023.12345',
                title='Test Paper',
                authors=['Author'],
                abstract='Abstract',
                pdf_url='invalid-url',
                published='2023-01-01',
                categories=['cs.AI']
            )

class TestArxivDownloaderIntegration(unittest.TestCase):
    """Integration tests for ArxivDownloader"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = ArxivDownloader(download_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    @patch('arxiv_downloader.requests.get')
    def test_search_papers_mock(self, mock_get):
        """Test search papers enhanced with mocked response"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2023.12345v1</id>
                <title>Test Paper Title</title>
                <author><name>Test Author</name></author>
                <summary>Test abstract</summary>
                <link href="http://arxiv.org/pdf/2023.12345v1.pdf" rel="alternate" type="application/pdf"/>
                <published>2023-01-01T00:00:00Z</published>
                <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
                <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">Test comment</arxiv:comment>
                <arxiv:journal_ref xmlns:arxiv="http://arxiv.org/schemas/atom">Test Journal</arxiv:journal_ref>
                <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1000/test</arxiv:doi>
            </entry>
        </feed>
        '''
        mock_get.return_value = mock_response
        
        # Test search
        papers = self.downloader.search_papers_enhanced(query='test query', max_results=1)
        
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, 'Test Paper Title')
        self.assertEqual(papers[0].id, '2023.12345v1')
        self.assertEqual(papers[0].comment, 'Test comment')
        self.assertEqual(papers[0].journal_ref, 'Test Journal')
        self.assertEqual(papers[0].doi, '10.1000/test')

if __name__ == '__main__':
    unittest.main()