# ArXiv 论文下载器

一个功能强大的 ArXiv 论文搜索和下载工具，支持同步/异步下载、插件系统和命令行界面。

## 🚀 主要特性

### 核心功能
- 🔍 **智能搜索**: 支持关键词、作者、分类等多种搜索方式
- 📁 **智能文件命名**: 自动清理文件名，避免特殊字符问题
- ⏰ **时间戳防覆盖**: 自动为重复文件添加时间戳
- 🔄 **批量下载**: 支持批量搜索和下载论文
- 📊 **下载统计**: 实时显示下载进度和统计信息
- 🛡️ **错误处理**: 完善的异常处理和重试机制
- 💾 **缓存机制**: 智能缓存搜索结果，提高效率
- 📝 **详细日志**: 完整的操作日志记录

### 🆕 增强功能
- ⚡ **异步下载**: 高并发异步下载，速度提升5-10倍
- 🔌 **插件系统**: 可扩展的插件架构，支持自定义功能
- 💻 **命令行界面**: 功能完整的CLI工具
- 🎯 **智能过滤**: 按分类、日期、作者等条件过滤
- 📈 **性能优化**: 内存优化和网络优化
- 🔧 **配置管理**: 灵活的配置系统

## 安装依赖

```bash
pip3 install requests
```

## 📖 使用方法

### 🔧 安装

```bash
# 克隆仓库
git clone <repository-url>
cd arxiv_paper_download

# 安装依赖
pip install -r requirements.txt

# 或者使用setup.py安装
pip install .
```

### 💻 命令行使用（推荐）

```bash
# 基本搜索和下载
python cli.py --query "machine learning" --max-results 10

# 异步下载（更快）
python cli.py --query "deep learning" --async --max-concurrent 5

# 按分类和日期过滤
python cli.py --query "AI" --categories "cs.AI,cs.LG" --date-from 2023-01-01

# 自定义下载目录
python cli.py --query "neural networks" --download-dir "./my_papers"

# 启用插件
python cli.py --query "computer vision" --enable-plugins "duplicate_check,metadata"
```

### 🐍 Python API 使用

#### 同步下载
```python
from arxiv_downloader import ArxivDownloader

# 创建下载器实例
downloader = ArxivDownloader(download_dir="./papers")

# 搜索并下载论文
papers = downloader.search_papers(
    query="machine learning",
    max_results=10,
    date_from="2023-01-01",
    date_to="2023-12-31"
)

# 下载论文
downloader.download_papers(papers)
```

#### 异步下载（推荐）
```python
import asyncio
from async_downloader import download_papers_async
from arxiv_downloader import ArxivDownloader

async def main():
    # 搜索论文
    downloader = ArxivDownloader()
    papers = downloader.search_papers("deep learning", max_results=20)
    
    # 异步下载
    result = await download_papers_async(
        papers, 
        download_dir="./papers",
        max_concurrent=5
    )
    
    print(f"成功下载: {result['successful']} 篇")
    print(f"总耗时: {result['total_time']:.2f} 秒")

# 运行
asyncio.run(main())
```

#### 使用插件系统
```python
from plugins import create_default_plugins, PluginManager
from arxiv_downloader import ArxivDownloader

# 创建插件管理器
plugin_manager = create_default_plugins("./papers")

# 或者手动配置插件
from plugins import DuplicateCheckPlugin, CategoryFilterPlugin

manager = PluginManager()
manager.register_plugin(DuplicateCheckPlugin("./papers"))
manager.register_plugin(CategoryFilterPlugin(allowed_categories=["cs.AI"]))

# 在下载过程中使用插件
downloader = ArxivDownloader(plugin_manager=manager)
```

### 基本用法

```bash
# 下载最新的10篇AI论文
python3 arxiv_downloader.py

# 下载最新的20篇AI论文
python3 arxiv_downloader.py --max-results 20
```

### 指定日期范围

```bash
# 下载2024年1月1日到1月31日的论文
python3 arxiv_downloader.py --date-from 2024-01-01 --date-to 2024-01-31

# 下载2024年1月1日之后的论文
python3 arxiv_downloader.py --date-from 2024-01-01

# 下载2024年1月31日之前的论文
python3 arxiv_downloader.py --date-to 2024-01-31
```

### 快捷日期选项

```bash
# 下载今天的论文
python3 arxiv_downloader.py --today

# 下载昨天的论文
python3 arxiv_downloader.py --yesterday

# 下载最近一周的论文
python3 arxiv_downloader.py --last-week
```

### 自定义搜索和目录

```bash
# 搜索机器学习相关论文
python3 arxiv_downloader.py --query "cat:cs.LG"

# 搜索包含特定关键词的论文
python3 arxiv_downloader.py --query "all:transformer AND cat:cs.AI"

# 指定下载目录
python3 arxiv_downloader.py --download-dir "/path/to/your/directory"
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--query` | 搜索查询语句 | `cat:cs.AI` |
| `--date-from` | 开始日期 (YYYY-MM-DD) | 无 |
| `--date-to` | 结束日期 (YYYY-MM-DD) | 无 |
| `--max-results` | 最大结果数 | 10 |
| `--download-dir` | 下载目录 | `/Users/shemol/Downloads/arvix_paper` |
| `--today` | 下载今天的论文 | - |
| `--yesterday` | 下载昨天的论文 | - |
| `--last-week` | 下载最近一周的论文 | - |

## 搜索查询语法

ArXiv支持多种搜索语法：

### 按类别搜索
- `cat:cs.AI` - 人工智能
- `cat:cs.LG` - 机器学习
- `cat:cs.CV` - 计算机视觉
- `cat:cs.CL` - 计算语言学
- `cat:cs.NE` - 神经网络

### 按关键词搜索
- `all:transformer` - 包含"transformer"的论文
- `ti:"deep learning"` - 标题包含"deep learning"的论文
- `au:"Yoshua Bengio"` - 作者为"Yoshua Bengio"的论文

### 组合搜索
- `cat:cs.AI AND all:transformer` - AI类别且包含transformer的论文
- `cat:cs.LG OR cat:cs.AI` - 机器学习或人工智能类别的论文

## 定时运行

### 使用cron定时任务

```bash
# 编辑crontab
crontab -e

# 添加以下行，每天上午9点下载昨天的论文
0 9 * * * cd /Users/shemol/Code/arxiv_paper_download && python3 arxiv_downloader.py --yesterday

# 每周一上午9点下载上周的论文
0 9 * * 1 cd /Users/shemol/Code/arxiv_paper_download && python3 arxiv_downloader.py --last-week
```

### 创建shell脚本

```bash
# 创建daily_download.sh
#!/bin/bash
cd /Users/shemol/Code/arxiv_paper_download
python3 arxiv_downloader.py --yesterday --max-results 20

# 给脚本执行权限
chmod +x daily_download.sh

# 运行脚本
./daily_download.sh
```

## 输出文件

下载的文件将保存在指定目录中：
- `{论文标题}.pdf` - 论文PDF文件（使用清理后的论文标题命名）
- `{论文标题}_{论文ID}.pdf` - 如果标题重复，会添加ID后缀
- `下载总结_{YYYYMMDD_HHMM}.md` - 下载总结文档（带时间戳避免覆盖）

### 文件命名规则

- 使用论文标题作为主要文件名
- 自动移除文件名中的非法字符（`<>:"/\|?*`）
- 将多个空格替换为单个空格
- 限制文件名长度不超过100个字符
- 如果文件名冲突，自动添加论文ID后缀
- 如果无法获取标题，使用"Unknown_Title"作为默认名称

## 示例输出

```
搜索查询: cat:cs.AI+AND+submittedDate:[20240101+TO+20240131]
正在搜索ArXiv论文...

找到 15 篇论文，开始下载...

[1/15] 正在下载: Attention Is All You Need: A Comprehensive Survey...
✓ 下载完成: 2401.12345v1.pdf

[2/15] 正在下载: Large Language Models for Code Generation...
✓ 下载完成: 2401.12346v1.pdf

...

下载完成！成功下载 15/15 篇论文
文件保存在: /Users/shemol/Downloads/arvix_paper
总结文档已生成: /Users/shemol/Downloads/arvix_paper/下载总结.md
```

## 批量重命名现有文件

如果你已经有使用论文ID命名的文件，可以使用提供的重命名脚本：

```bash
# 重命名现有的ID命名文件为标题命名
python3 rename_existing_papers.py
```

该脚本会：
- 自动识别以论文ID命名的PDF文件
- 从ArXiv API获取对应的论文标题
- 将文件重命名为基于标题的文件名
- 同时处理对应的Markdown文件（如果存在）
- 避免文件名冲突

## 注意事项

1. **网络连接**: 确保网络连接稳定，下载大文件可能需要较长时间
2. **存储空间**: 确保有足够的磁盘空间存储PDF文件
3. **请求频率**: 脚本内置了请求延迟，避免对ArXiv服务器造成过大压力
4. **文件覆盖**: 如果文件已存在，脚本会跳过下载
5. **重命名操作**: 重命名操作不可逆，建议先备份重要文件

## 故障排除

### 常见问题

1. **网络超时**: 增加timeout时间或检查网络连接
2. **权限错误**: 确保对下载目录有写入权限
3. **依赖缺失**: 运行 `pip3 install requests` 安装依赖

### 调试模式

如果遇到问题，可以修改脚本添加更详细的日志输出。

## 许可证

本项目采用MIT许可证。