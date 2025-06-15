# ArXiv 论文下载器

一个功能强大的 ArXiv 论文搜索和下载工具，提供 **Web 界面**、**命令行工具** 和 **Python API** 三种使用方式，支持同步/异步下载、插件系统和智能管理功能。

## 🌟 项目亮点

### 🖥️ **现代化 Web 界面**
- 🎨 **直观易用**: 基于 Vue.js 的现代化用户界面
- 🔍 **实时搜索**: 支持关键词、日期范围、分类筛选
- 📱 **响应式设计**: 完美适配桌面和移动设备
- 📊 **可视化管理**: 下载历史、统计图表、进度跟踪
- 🎯 **智能推荐**: 基于搜索历史的关键词推荐
- 📁 **自定义路径**: 用户可选择下载目录

### 🚀 核心功能
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
- 🌐 **RESTful API**: 完整的后端API接口

## 🛠️ 快速开始

### 📦 安装依赖

```bash
# 克隆仓库
git clone https://github.com/your-username/arxiv-paper-downloader.git
cd arxiv_paper_download

# 安装后端依赖
pip install -r requirements_backend.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 🚀 启动应用

#### 方式一：Web 界面（推荐）

```bash
# 启动后端服务器
python app.py

# 在新终端启动前端服务器
cd frontend
npm run dev
```

然后在浏览器中访问 `http://localhost:3000` 即可使用 Web 界面。

#### 方式二：命令行工具

```bash
# 基本使用
python cli.py --query "machine learning" --max-results 10

# 异步下载（更快）
python cli.py --query "deep learning" --async --max-concurrent 5
```

#### 方式三：Python API

```python
from arxiv_downloader import ArxivDownloader

# 创建下载器实例
downloader = ArxivDownloader(download_dir="./papers")

# 搜索并下载论文
papers = downloader.search_papers("machine learning", max_results=10)
downloader.download_papers(papers)
```

## 📖 详细使用指南

### 🌐 Web 界面功能

#### 主要功能
- **📝 论文搜索**: 支持关键词搜索，可设置日期范围和最大结果数
- **📊 搜索结果**: 显示论文标题、作者、摘要、发布日期等详细信息
- **⬇️ 一键下载**: 点击下载按钮即可下载PDF，支持自定义下载路径
- **📈 下载历史**: 查看所有下载记录，包括状态和进度
- **🎯 关键词推荐**: 基于搜索历史智能推荐相关关键词
- **📱 响应式设计**: 完美适配各种设备屏幕

#### 使用步骤
1. 在搜索框中输入关键词（如："machine learning"、"transformer"等）
2. 可选择设置日期范围和最大结果数
3. 点击"搜索论文"按钮
4. 在搜索结果中点击"下载 PDF"按钮
5. 选择下载路径（首次使用需要设置）
6. 在"下载历史"中查看下载状态

### 💻 命令行使用

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
| `--download-dir` | 下载目录 | `~/Downloads/arxiv_papers` |
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
0 9 * * * cd /path/to/arxiv_paper_download && python3 arxiv_downloader.py --yesterday

# 每周一上午9点下载上周的论文
0 9 * * 1 cd /path/to/arxiv_paper_download && python3 arxiv_downloader.py --last-week
```

### 创建shell脚本

```bash
# 创建daily_download.sh
#!/bin/bash
cd /path/to/arxiv_paper_download
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
文件保存在: ~/Downloads/arxiv_papers
总结文档已生成: ~/Downloads/arxiv_papers/下载总结.md
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

## 🏗️ 技术栈

### 后端
- **Python 3.7+**: 主要编程语言
- **Flask**: Web 框架，提供 RESTful API
- **Requests**: HTTP 请求库，用于与 ArXiv API 交互
- **Flask-CORS**: 跨域资源共享支持

### 前端
- **Vue.js 3**: 现代化前端框架
- **Vite**: 快速构建工具
- **CSS3**: 响应式样式设计
- **JavaScript ES6+**: 现代 JavaScript 特性

### 核心依赖
- **ArXiv API**: 论文数据来源
- **PDF 处理**: 自动下载和管理 PDF 文件
- **异步处理**: 支持高并发下载

## 📁 项目结构

```
arxiv_paper_download/
├── 📄 app.py                 # Flask 后端服务器
├── 📄 arxiv_downloader.py     # 核心下载器类
├── 📄 async_downloader.py     # 异步下载器
├── 📄 cli.py                  # 命令行界面
├── 📄 plugins.py              # 插件系统
├── 📄 models.py               # 数据模型
├── 📄 config.py               # 配置管理
├── 📄 utils.py                # 工具函数
├── 📄 logger.py               # 日志系统
├── 📄 cache.py                # 缓存机制
├── 📄 requirements_backend.txt # 后端依赖
├── 📄 requirements.txt        # 基础依赖
├── 📁 frontend/               # 前端应用
│   ├── 📄 package.json        # 前端依赖配置
│   ├── 📄 vite.config.js      # Vite 配置
│   ├── 📄 index.html          # 主页面
│   └── 📁 src/                # 源代码
│       ├── 📄 App.vue         # 主应用组件
│       ├── 📄 main.js         # 应用入口
│       ├── 📁 api/            # API 接口
│       ├── 📁 styles/         # 样式文件
│       └── 📁 views/          # 页面组件
└── 📄 README.md               # 项目文档
```

## 🔧 API 接口

### 搜索论文
```http
POST /api/papers/search
Content-Type: application/json

{
  "query": "machine learning",
  "max_results": 10,
  "date_from": "2023-01-01",
  "date_to": "2023-12-31"
}
```

### 下载论文
```http
POST /api/papers/download
Content-Type: application/json

{
  "paper_id": "2301.12345v1",
  "title": "Paper Title",
  "download_path": "/path/to/download"
}
```

### 获取下载历史
```http
GET /api/downloads
```

### 获取推荐关键词
```http
GET /api/keywords/recommendations
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v2.0.0 (最新)
- ✨ 新增现代化 Web 界面
- ✨ 支持用户自定义下载路径
- ✨ 添加关键词推荐功能
- ✨ 完整的 RESTful API
- 🐛 修复论文 ID 版本号处理问题
- 🎨 优化用户界面和体验

### v1.0.0
- ✨ 基础命令行工具
- ✨ 异步下载支持
- ✨ 插件系统
- ✨ 智能文件命名

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [ArXiv](https://arxiv.org/) - 提供开放的学术论文数据
- [Vue.js](https://vuejs.org/) - 优秀的前端框架
- [Flask](https://flask.palletsprojects.com/) - 轻量级 Web 框架

---

如果这个项目对您有帮助，请给个 ⭐ Star！