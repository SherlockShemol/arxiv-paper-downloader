#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced features test
Test async downloader, plugin system and other new features
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from models import Paper, ValidationError
from async_downloader import AsyncArxivDownloader, download_papers_async
from plugins import (
    PluginManager, DuplicateCheckPlugin, CategoryFilterPlugin,
    MetadataPlugin, StatisticsPlugin, create_default_plugins
)
from config import Config

class TestPaperValidation:
    """Test paper data validation"""
    
    def test_valid_paper(self):
        """Test valid paper data"""
        paper = Paper(
            id="2301.00001",
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            abstract="This is a test abstract.",
            pdf_url="https://arxiv.org/pdf/2301.00001.pdf",
            published="2023-01-01",
            categories=["cs.AI"]
        )
        assert paper.id == "2301.00001"
        assert paper.title == "Test Paper"
    
    def test_invalid_paper_empty_id(self):
        """Test invalid paper with empty ID"""
        with pytest.raises(ValidationError):
            Paper(
                id="",
                title="Test Paper",
                authors=["Author 1"],
                abstract="Abstract",
                pdf_url="https://arxiv.org/pdf/test.pdf",
                published="2023-01-01",
                categories=["cs.AI"]
            )
    
    def test_invalid_paper_empty_title(self):
        """Test invalid paper with empty title"""
        with pytest.raises(ValidationError):
            Paper(
                id="2301.00001",
                title="",
                authors=["Author 1"],
                abstract="Abstract",
                pdf_url="https://arxiv.org/pdf/test.pdf",
                published="2023-01-01",
                categories=["cs.AI"]
            )
    
    def test_invalid_paper_bad_url(self):
        """Test paper with invalid URL"""
        with pytest.raises(ValidationError):
            Paper(
                id="2301.00001",
                title="Test Paper",
                authors=["Author 1"],
                abstract="Abstract",
                pdf_url="invalid-url",
                published="2023-01-01",
                categories=["cs.AI"]
            )

class TestAsyncDownloader:
    """Test async downloader"""
    
    @pytest.fixture
    def temp_dir(self):
        """Temporary directory fixture"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_papers(self):
        """Sample paper data"""
        return [
            Paper(
                id="2301.00001",
                title="Test Paper 1",
                authors=["Author 1"],
                abstract="Abstract 1",
                pdf_url="https://arxiv.org/pdf/2301.00001.pdf",
                published="2023-01-01",
                categories=["cs.AI"]
            ),
            Paper(
                id="2301.00002",
                title="Test Paper 2",
                authors=["Author 2"],
                abstract="Abstract 2",
                pdf_url="https://arxiv.org/pdf/2301.00002.pdf",
                published="2023-01-02",
                categories=["cs.LG"]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_async_downloader_init(self, temp_dir):
        """Test async downloader initialization"""
        async with AsyncArxivDownloader(str(temp_dir)) as downloader:
            assert downloader.download_dir == temp_dir
            assert downloader.session is not None
    
    @pytest.mark.asyncio
    async def test_async_download_papers_mock(self, temp_dir, sample_papers):
        """Test async download (mocked)"""
        async with AsyncArxivDownloader(str(temp_dir), max_concurrent=2) as downloader:
            # Mock successful HTTP response
            with patch.object(downloader.session, 'get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.read = AsyncMock(return_value=b'fake pdf content')
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = await downloader.download_papers_async(sample_papers)
                
                assert result['successful'] >= 0
                assert result['total_time'] > 0
                assert isinstance(result['stats'], type(downloader.stats))

class TestPluginSystem:
    """Test plugin system"""
    
    @pytest.fixture
    def temp_dir(self):
        """Temporary directory fixture"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_paper(self):
        """Sample paper"""
        return Paper(
            id="2301.00001",
            title="Test Paper",
            authors=["Author 1"],
            abstract="This is a test abstract.",
            pdf_url="https://arxiv.org/pdf/2301.00001.pdf",
            published="2023-01-01",
            categories=["cs.AI", "cs.LG"]
        )
    
    def test_plugin_manager_init(self):
        """Test plugin manager initialization"""
        manager = PluginManager()
        assert len(manager.plugins) == 0
    
    def test_duplicate_check_plugin(self, temp_dir, sample_paper):
        """Test duplicate check plugin"""
        plugin = DuplicateCheckPlugin(temp_dir)
        
        # First time should allow download
        assert plugin.pre_download(sample_paper) is True
        
        # Mock successful download
        plugin.post_download(sample_paper, temp_dir / "test.pdf", True)
        
        # Second time should skip (same ID)
        assert plugin.pre_download(sample_paper) is False
    
    def test_category_filter_plugin(self, sample_paper):
        """Test category filter plugin"""
        # Test allowed category
        plugin = CategoryFilterPlugin(allowed_categories=["cs.AI"])
        assert plugin.pre_download(sample_paper) is True
        
        # Test disallowed category
        plugin = CategoryFilterPlugin(allowed_categories=["cs.CV"])
        assert plugin.pre_download(sample_paper) is False
        
        # Test blocked category
        plugin = CategoryFilterPlugin(blocked_categories=["cs.AI"])
        assert plugin.pre_download(sample_paper) is False
    
    def test_metadata_plugin(self, temp_dir, sample_paper):
        """Test metadata plugin"""
        plugin = MetadataPlugin(temp_dir)
        
        # Create test file
        test_file = temp_dir / "test.pdf"
        test_file.write_text("fake content")
        
        # Execute post-processing
        plugin.post_download(sample_paper, test_file, True)
        
        # Check if metadata file was created
        metadata_file = temp_dir / '.metadata' / f"{sample_paper.id}.json"
        assert metadata_file.exists()
    
    def test_statistics_plugin(self, temp_dir, sample_paper):
        """Test statistics plugin"""
        plugin = StatisticsPlugin(temp_dir)
        
        # Execute post-processing
        plugin.post_download(sample_paper, temp_dir / "test.pdf", True)
        
        # Check statistics data
        assert plugin.stats['total_downloads'] == 1
        assert plugin.stats['successful_downloads'] == 1
        assert 'cs.AI' in plugin.stats['categories']
        assert 'Author 1' in plugin.stats['authors']
    
    def test_plugin_manager_hooks(self, temp_dir, sample_paper):
        """Test plugin manager hooks"""
        manager = create_default_plugins(temp_dir)
        
        # Test pre-download hook
        should_download = manager.pre_download_hook(sample_paper)
        assert should_download is True
        
        # Test post-download hook
        test_file = temp_dir / "test.pdf"
        test_file.write_text("fake content")
        
        # Should not throw exception
        manager.post_download_hook(sample_paper, test_file, True)
    
    def test_plugin_enable_disable(self):
        """Test plugin enable/disable"""
        manager = PluginManager()
        plugin = DuplicateCheckPlugin()
        
        manager.register_plugin(plugin)
        assert plugin.enabled is True
        
        plugin.disable()
        assert plugin.enabled is False
        
        plugin.enable()
        assert plugin.enabled is True
    
    def test_list_plugins(self, temp_dir):
        """Test list plugins"""
        manager = create_default_plugins(temp_dir)
        plugins = manager.list_plugins()
        
        assert len(plugins) >= 3  # At least 3 default plugins
        assert all('name' in p for p in plugins)
        assert all('enabled' in p for p in plugins)
        assert all('type' in p for p in plugins)

class TestConfig:
    """Test config class"""
    
    def test_get_download_dir_default(self):
        """Test get default download directory"""
        dir_path = Config.get_download_dir()
        assert isinstance(dir_path, Path)
        assert str(dir_path) == Config.DEFAULT_DOWNLOAD_DIR
    
    def test_get_download_dir_custom(self):
        """Test get custom download directory"""
        custom_dir = "/tmp/test"
        dir_path = Config.get_download_dir(custom_dir)
        assert isinstance(dir_path, Path)
        assert str(dir_path) == custom_dir
    
    def test_get_cache_dir(self):
        """Test get cache directory"""
        cache_dir = Config.get_cache_dir()
        assert isinstance(cache_dir, Path)
        assert cache_dir.name == '.cache'
    
    def test_get_log_dir(self):
        """Test get log directory"""
        log_dir = Config.get_log_dir()
        assert isinstance(log_dir, Path)
        assert 'log' in str(log_dir).lower() or '.log' in str(log_dir)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])