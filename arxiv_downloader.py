"""ArXiv AI论文自动下载器 - 重构版本

支持指定日期范围搜索和下载人工智能相关论文
具备完善的错误处理、缓存机制、日志系统和类型提示
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
    """ArXiv论文下载器"""
    
    def __init__(self, download_dir: Optional[str] = None):
        """初始化下载器
        
        Args:
            download_dir: 下载目录路径
        """
        self.download_dir = Config.get_download_dir(download_dir)
        ensure_directory(self.download_dir)
        
        self.base_url = "http://export.arxiv.org/api/query"
        self.stats = DownloadStats()
        self.cache_manager = CacheManager()
        
        # 设置日志
        setup_logging(log_dir=Config.get_log_dir(self.download_dir))
        
        self.log_info(f"ArXiv下载器初始化完成，下载目录: {self.download_dir}")
    
    def search_papers(self, query: str = Config.DEFAULT_QUERY, 
                     date_from: Optional[str] = None, 
                     date_to: Optional[str] = None, 
                     max_results: int = Config.DEFAULT_MAX_RESULTS) -> List[Paper]:
        """搜索ArXiv论文
        
        Args:
            query: 搜索查询，默认为cs.AI类别
            date_from: 开始日期 (YYYY-MM-DD)
            date_to: 结束日期 (YYYY-MM-DD)
            max_results: 最大结果数
        
        Returns:
            论文列表
        
        Raises:
            ValidationError: 参数验证失败
            NetworkError: 网络请求失败
            ParseError: XML解析失败
        """
        # 参数验证
        if date_from and not is_valid_date_format(date_from):
            raise ValidationError(f"无效的开始日期格式: {date_from}")
        
        if date_to and not is_valid_date_format(date_to):
            raise ValidationError(f"无效的结束日期格式: {date_to}")
        
        if max_results <= 0:
            raise ValidationError(f"最大结果数必须大于0: {max_results}")
        
        # 检查缓存
        query_hash = generate_query_hash(query, date_from, date_to, max_results)
        cached_results = self.cache_manager.get_search_results(query_hash)
        
        if cached_results is not None:
            self.log_info(f"从缓存获取搜索结果，共 {len(cached_results)} 篇论文")
            return [Paper(**paper_data) for paper_data in cached_results]
        
        # 构建搜索查询
        search_query = query
        
        # 添加日期范围过滤
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
        
        self.log_info(f"搜索查询: {search_query}")
        self.log_info("正在搜索ArXiv论文...")
        
        try:
            response = self._make_request_with_retry(self.base_url, params)
            papers = self._parse_arxiv_response(response.text)
            
            # 缓存搜索结果
            paper_data_list = [self._paper_to_dict(paper) for paper in papers]
            self.cache_manager.save_search_results(query_hash, paper_data_list)
            
            self.log_info(f"搜索完成，找到 {len(papers)} 篇论文")
            return papers
             
        except requests.RequestException as e:
            raise NetworkError(f"搜索请求失败: {e}")
    
    def _make_request_with_retry(self, url: str, params: Dict[str, Any], 
                                max_retries: int = Config.MAX_RETRIES) -> requests.Response:
        """带重试机制的HTTP请求
        
        Args:
            url: 请求URL
            params: 请求参数
            max_retries: 最大重试次数
        
        Returns:
            响应对象
        
        Raises:
            NetworkError: 请求失败
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=Config.API_TIMEOUT)
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"请求失败，已重试{max_retries}次: {e}")
                
                wait_time = Config.RETRY_DELAY_BASE ** attempt
                self.log_warning(f"请求失败，{wait_time}秒后重试 ({attempt + 1}/{max_retries}): {e}")
                time.sleep(wait_time)
        
        raise NetworkError("请求重试次数已用尽")
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Paper]:
        """解析ArXiv API的XML响应
        
        Args:
            xml_content: XML内容
        
        Returns:
            论文列表
        
        Raises:
            ParseError: XML解析失败
        """
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # 定义命名空间
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
                    self.log_warning(f"跳过无效论文条目: {e}")
                    continue
            
        except ET.ParseError as e:
            raise ParseError(f"XML解析错误: {e}")
        
        return papers
    
    def _parse_paper_entry(self, entry: ET.Element, namespaces: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """解析单个论文条目
        
        Args:
            entry: XML条目元素
            namespaces: XML命名空间
        
        Returns:
            论文数据字典
        """
        paper_data = {}
        
        # 获取ID
        id_elem = entry.find('atom:id', namespaces)
        if id_elem is None:
            return None
        paper_data['id'] = id_elem.text.split('/')[-1]
        
        # 获取标题
        title_elem = entry.find('atom:title', namespaces)
        if title_elem is None:
            return None
        paper_data['title'] = clean_text(title_elem.text)
        
        # 获取作者
        authors = []
        for author in entry.findall('atom:author', namespaces):
            name_elem = author.find('atom:name', namespaces)
            if name_elem is not None:
                authors.append(name_elem.text.strip())
        paper_data['authors'] = authors
        
        # 获取摘要
        summary_elem = entry.find('atom:summary', namespaces)
        if summary_elem is not None:
            paper_data['abstract'] = clean_text(summary_elem.text)
        else:
            paper_data['abstract'] = ""
        
        # 获取PDF链接
        pdf_url = None
        for link in entry.findall('atom:link', namespaces):
            if link.get('type') == 'application/pdf':
                pdf_url = link.get('href')
                break
        
        if not pdf_url or not validate_url(pdf_url):
            return None
        paper_data['pdf_url'] = pdf_url
        
        # 获取发布日期
        published_elem = entry.find('atom:published', namespaces)
        if published_elem is not None:
            paper_data['published'] = published_elem.text
        else:
            paper_data['published'] = ""
        
        # 获取类别
        categories = []
        for category in entry.findall('atom:category', namespaces):
            term = category.get('term')
            if term:
                categories.append(term)
        paper_data['categories'] = categories
        
        return paper_data
    
    def download_pdf(self, paper: Paper) -> bool:
        """下载单篇论文的PDF
        
        Args:
            paper: 论文对象
        
        Returns:
            是否下载成功
        """
        # 生成文件名
        clean_title = sanitize_filename(paper.title)
        filename = f"{clean_title}.pdf"
        filepath = generate_unique_filename(self.download_dir, filename, paper.id)
        
        # 检查文件是否已存在
        if filepath.exists():
            self.log_info(f"✓ 文件已存在: {filepath.name}")
            self.stats.add_skip()
            return True
        
        try:
            self.log_info(f"正在下载: {paper.title[:50]}...")
            
            # 下载文件
            response = self._download_with_retry(paper.pdf_url)
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=Config.CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
            
            # 记录统计信息
            file_size_mb = get_file_size_mb(filepath)
            self.stats.add_success(file_size_mb)
            
            self.log_info(f"✓ 下载完成: {filepath.name}")
            return True
            
        except (NetworkError, FileOperationError) as e:
            self.log_error(f"✗ 下载失败 {filename}: {e}")
            
            # 删除不完整的文件
            if filepath.exists():
                try:
                    filepath.unlink()
                except OSError:
                    pass
            
            self.stats.add_failure()
            return False
    
    def _download_with_retry(self, url: str, max_retries: int = Config.MAX_RETRIES) -> requests.Response:
        """带重试机制的文件下载
        
        Args:
            url: 下载URL
            max_retries: 最大重试次数
        
        Returns:
            响应对象
        
        Raises:
            NetworkError: 下载失败
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=Config.DOWNLOAD_TIMEOUT, stream=True)
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"下载失败，已重试{max_retries}次: {e}")
                
                wait_time = Config.RETRY_DELAY_BASE ** attempt
                self.log_warning(f"下载失败，{wait_time}秒后重试 ({attempt + 1}/{max_retries}): {e}")
                time.sleep(wait_time)
        
        raise NetworkError("下载重试次数已用尽")
    
    def download_papers(self, papers: List[Paper]) -> None:
        """批量下载论文
        
        Args:
            papers: 论文列表
        """
        if not papers:
            self.log_info("没有找到论文")
            return
        
        self.log_info(f"找到 {len(papers)} 篇论文，开始下载...")
        
        # 重置统计信息
        self.stats = DownloadStats()
        self.stats.total_papers = len(papers)
        
        start_time = time.time()
        
        for i, paper in enumerate(papers, 1):
            self.log_info(f"[{i}/{len(papers)}] ", end="")
            self.download_pdf(paper)
            
            # 添加延迟避免请求过于频繁
            if i < len(papers):
                time.sleep(Config.REQUEST_DELAY)
        
        # 计算下载时间
        self.stats.download_time_seconds = time.time() - start_time
        
        self.log_info(f"下载完成！{self.stats}")
        self.log_info(f"文件保存在: {self.download_dir}")
        
        if self.stats.total_size_mb > 0:
            self.log_info(f"平均下载速度: {self.stats.average_speed_mbps:.2f} MB/s")
    
    def generate_summary(self, papers: List[Paper]) -> None:
        """生成下载总结文档
        
        Args:
            papers: 论文列表
        """
        if not papers:
            return
        
        # 生成带时间戳的文件名，精确到分钟
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        summary_file = self.download_dir / f"下载总结_{timestamp}.md"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("# ArXiv AI论文下载总结\n\n")
                f.write(f"## 下载时间\n{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
                f.write(f"## 统计信息\n")
                f.write(f"- 论文总数: {self.stats.total_papers}\n")
                f.write(f"- 成功下载: {self.stats.successful_downloads}\n")
                f.write(f"- 下载失败: {self.stats.failed_downloads}\n")
                f.write(f"- 跳过下载: {self.stats.skipped_downloads}\n")
                f.write(f"- 成功率: {self.stats.success_rate:.1%}\n")
                if self.stats.total_size_mb > 0:
                    f.write(f"- 总大小: {self.stats.total_size_mb:.2f} MB\n")
                    f.write(f"- 平均速度: {self.stats.average_speed_mbps:.2f} MB/s\n")
                f.write("\n## 论文列表\n\n")
                
                for i, paper in enumerate(papers, 1):
                    f.write(f"### {i}. {paper.title}\n")
                    f.write(f"- **论文ID**: {paper.id}\n")
                    f.write(f"- **作者**: {paper.authors_str}\n")
                    f.write(f"- **类别**: {paper.categories_str}\n")
                    f.write(f"- **发布日期**: {paper.published}\n")
                    f.write(f"- **摘要**: {paper.short_abstract}\n")
                    
                    # 确定实际的文件名
                    clean_title = sanitize_filename(paper.title)
                    filename = f"{clean_title}.pdf"
                    filepath = self.download_dir / filename
                    
                    # 检查是否有ID后缀的文件
                    if not filepath.exists():
                        filepath_with_id = self.download_dir / f"{clean_title}_{paper.id}.pdf"
                        if filepath_with_id.exists():
                            filename = f"{clean_title}_{paper.id}.pdf"
                    
                    f.write(f"- **文件**: {filename}\n\n")
            
            self.log_info(f"总结文档已生成: {summary_file}")
            
        except Exception as e:
            self.log_error(f"生成总结文档失败: {e}")
    
    def download_paper_by_id(self, paper_id: str) -> bool:
        """通过论文ID下载单篇论文
        
        Args:
            paper_id: ArXiv论文ID (例如: 2301.00001 或 2301.00001v1)
        
        Returns:
            是否下载成功
        """
        try:
            # 去掉版本号（如果存在）
            # ArXiv ID格式: YYMM.NNNNN[vN]
            clean_paper_id = paper_id
            if 'v' in paper_id:
                clean_paper_id = paper_id.split('v')[0]
            
            # 构建搜索查询，通过ID精确搜索
            query = f"id:{clean_paper_id}"
            
            self.log_info(f"搜索论文ID: {paper_id} (清理后: {clean_paper_id})")
            
            # 搜索论文
            papers = self.search_papers(query=query, max_results=1)
            
            if not papers:
                self.log_error(f"未找到论文ID: {paper_id} (搜索ID: {clean_paper_id})")
                return False
            
            paper = papers[0]
            
            # 下载论文
            success = self.download_pdf(paper)
            
            if success:
                self.log_info(f"论文下载成功: {paper.title}")
            else:
                self.log_error(f"论文下载失败: {paper.title}")
            
            return success
            
        except Exception as e:
            self.log_error(f"下载论文 {paper_id} 时发生错误: {e}")
            return False
    
    def _paper_to_dict(self, paper: Paper) -> Dict[str, Any]:
        """将Paper对象转换为字典"""
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
    """主函数"""
    parser = argparse.ArgumentParser(description='ArXiv AI论文下载器 - 重构版本')
    parser.add_argument('--query', default=Config.DEFAULT_QUERY, help=f'搜索查询 (默认: {Config.DEFAULT_QUERY})')
    parser.add_argument('--date-from', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--date-to', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--max-results', type=int, default=Config.DEFAULT_MAX_RESULTS, 
                       help=f'最大结果数 (默认: {Config.DEFAULT_MAX_RESULTS})')
    parser.add_argument('--download-dir', default=Config.DEFAULT_DOWNLOAD_DIR, help='下载目录')
    parser.add_argument('--today', action='store_true', help='下载今天的论文')
    parser.add_argument('--yesterday', action='store_true', help='下载昨天的论文')
    parser.add_argument('--last-week', action='store_true', help='下载最近一周的论文')
    parser.add_argument('--clear-cache', action='store_true', help='清理过期缓存')
    parser.add_argument('--cache-stats', action='store_true', help='显示缓存统计信息')
    
    args = parser.parse_args()
    
    try:
        # 创建下载器实例
        downloader = ArxivDownloader(args.download_dir)
        
        # 处理缓存相关命令
        if args.clear_cache:
            downloader.cache_manager.clear_expired_cache()
            return
        
        if args.cache_stats:
            stats = downloader.cache_manager.get_cache_stats()
            print(f"缓存统计: 论文缓存 {stats['paper_cache_count']} 个，搜索缓存 {stats['search_cache_count']} 个")
            return
        
        # 处理快捷日期选项
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
        
        # 搜索论文
        papers = downloader.search_papers(
            query=args.query,
            date_from=args.date_from,
            date_to=args.date_to,
            max_results=args.max_results
        )
        
        if papers:
            # 下载论文
            downloader.download_papers(papers)
            
            # 生成总结
            downloader.generate_summary(papers)
        else:
            downloader.log_info("没有找到符合条件的论文")
    
    except (ValidationError, NetworkError, ParseError, FileOperationError) as e:
        print(f"错误: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n用户中断下载")
        return 1
    except Exception as e:
        print(f"未知错误: {e}")
        return 1
    
    return 0

def cli_main():
    """CLI入口点"""
    from cli import main as cli_main_func
    cli_main_func()

if __name__ == "__main__":
    # 如果直接运行此文件，使用原有的main函数
    # 如果要使用CLI，请运行: python -m cli
    exit(main())