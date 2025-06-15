#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强功能测试
测试异步下载器、插件系统等新功能
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
    """测试论文数据验证"""
    
    def test_valid_paper(self):
        """测试有效论文数据"""
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
        """测试空ID的无效论文"""
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
        """测试空标题的无效论文"""
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
        """测试无效URL的论文"""
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
    """测试异步下载器"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录fixture"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_papers(self):
        """示例论文数据"""
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
        """测试异步下载器初始化"""
        async with AsyncArxivDownloader(str(temp_dir)) as downloader:
            assert downloader.download_dir == temp_dir
            assert downloader.session is not None
    
    @pytest.mark.asyncio
    async def test_async_download_papers_mock(self, temp_dir, sample_papers):
        """测试异步下载（模拟）"""
        async with AsyncArxivDownloader(str(temp_dir), max_concurrent=2) as downloader:
            # 模拟成功的HTTP响应
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
    """测试插件系统"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录fixture"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_paper(self):
        """示例论文"""
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
        """测试插件管理器初始化"""
        manager = PluginManager()
        assert len(manager.plugins) == 0
    
    def test_duplicate_check_plugin(self, temp_dir, sample_paper):
        """测试重复检查插件"""
        plugin = DuplicateCheckPlugin(temp_dir)
        
        # 第一次应该允许下载
        assert plugin.pre_download(sample_paper) is True
        
        # 模拟下载成功
        plugin.post_download(sample_paper, temp_dir / "test.pdf", True)
        
        # 第二次应该跳过（相同ID）
        assert plugin.pre_download(sample_paper) is False
    
    def test_category_filter_plugin(self, sample_paper):
        """测试分类过滤插件"""
        # 测试允许的分类
        plugin = CategoryFilterPlugin(allowed_categories=["cs.AI"])
        assert plugin.pre_download(sample_paper) is True
        
        # 测试不允许的分类
        plugin = CategoryFilterPlugin(allowed_categories=["cs.CV"])
        assert plugin.pre_download(sample_paper) is False
        
        # 测试阻止的分类
        plugin = CategoryFilterPlugin(blocked_categories=["cs.AI"])
        assert plugin.pre_download(sample_paper) is False
    
    def test_metadata_plugin(self, temp_dir, sample_paper):
        """测试元数据插件"""
        plugin = MetadataPlugin(temp_dir)
        
        # 创建测试文件
        test_file = temp_dir / "test.pdf"
        test_file.write_text("fake content")
        
        # 执行后处理
        plugin.post_download(sample_paper, test_file, True)
        
        # 检查元数据文件是否创建
        metadata_file = temp_dir / '.metadata' / f"{sample_paper.id}.json"
        assert metadata_file.exists()
    
    def test_statistics_plugin(self, temp_dir, sample_paper):
        """测试统计插件"""
        plugin = StatisticsPlugin(temp_dir)
        
        # 执行后处理
        plugin.post_download(sample_paper, temp_dir / "test.pdf", True)
        
        # 检查统计数据
        assert plugin.stats['total_downloads'] == 1
        assert plugin.stats['successful_downloads'] == 1
        assert 'cs.AI' in plugin.stats['categories']
        assert 'Author 1' in plugin.stats['authors']
    
    def test_plugin_manager_hooks(self, temp_dir, sample_paper):
        """测试插件管理器钩子"""
        manager = create_default_plugins(temp_dir)
        
        # 测试预下载钩子
        should_download = manager.pre_download_hook(sample_paper)
        assert should_download is True
        
        # 测试后下载钩子
        test_file = temp_dir / "test.pdf"
        test_file.write_text("fake content")
        
        # 不应该抛出异常
        manager.post_download_hook(sample_paper, test_file, True)
    
    def test_plugin_enable_disable(self):
        """测试插件启用/禁用"""
        manager = PluginManager()
        plugin = DuplicateCheckPlugin()
        
        manager.register_plugin(plugin)
        assert plugin.enabled is True
        
        plugin.disable()
        assert plugin.enabled is False
        
        plugin.enable()
        assert plugin.enabled is True
    
    def test_list_plugins(self, temp_dir):
        """测试列出插件"""
        manager = create_default_plugins(temp_dir)
        plugins = manager.list_plugins()
        
        assert len(plugins) >= 3  # 至少有3个默认插件
        assert all('name' in p for p in plugins)
        assert all('enabled' in p for p in plugins)
        assert all('type' in p for p in plugins)

class TestConfig:
    """测试配置类"""
    
    def test_get_download_dir_default(self):
        """测试获取默认下载目录"""
        dir_path = Config.get_download_dir()
        assert isinstance(dir_path, Path)
        assert str(dir_path) == Config.DEFAULT_DOWNLOAD_DIR
    
    def test_get_download_dir_custom(self):
        """测试获取自定义下载目录"""
        custom_dir = "/tmp/test"
        dir_path = Config.get_download_dir(custom_dir)
        assert isinstance(dir_path, Path)
        assert str(dir_path) == custom_dir
    
    def test_get_cache_dir(self):
        """测试获取缓存目录"""
        cache_dir = Config.get_cache_dir()
        assert isinstance(cache_dir, Path)
        assert cache_dir.name == '.cache'
    
    def test_get_log_dir(self):
        """测试获取日志目录"""
        log_dir = Config.get_log_dir()
        assert isinstance(log_dir, Path)
        assert 'log' in str(log_dir).lower() or '.log' in str(log_dir)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])