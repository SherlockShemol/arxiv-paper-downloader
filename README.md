# ArXiv Paper Downloader

A powerful ArXiv paper search and download tool that provides **Web Interface**, **Command Line Tool**, and **Python API** with support for synchronous/asynchronous downloads, plugin system, and intelligent management features.

## 🌟 Project Highlights

### 🖥️ **Modern Web Interface**
- 🎨 **Intuitive & User-friendly**: Modern user interface based on Vue.js
- 🔍 **Real-time Search**: Support for keyword, date range, and category filtering
- 📱 **Responsive Design**: Perfect adaptation for desktop and mobile devices
- 📊 **Visual Management**: Download history, statistical charts, progress tracking
- 🎯 **Smart Recommendations**: Keyword recommendations based on search history
- 📁 **Custom Paths**: User-selectable download directories

### 🚀 Core Features
- 🔍 **Smart Search**: Support for multiple search methods including keywords, authors, categories
- 📁 **Smart File Naming**: Automatic filename cleaning to avoid special character issues
- ⏰ **Timestamp Anti-overwrite**: Automatic timestamp addition for duplicate files
- 🔄 **Batch Download**: Support for batch search and download of papers
- 📊 **Download Statistics**: Real-time display of download progress and statistics
- 🛡️ **Error Handling**: Comprehensive exception handling and retry mechanisms
- 💾 **Caching Mechanism**: Smart caching of search results for improved efficiency
- 📝 **Detailed Logging**: Complete operation log recording

### 🆕 Enhanced Features
- ⚡ **Async Download**: High-concurrency asynchronous downloads, 5-10x speed improvement
- 🔌 **Plugin System**: Extensible plugin architecture supporting custom functionality
- 💻 **Command Line Interface**: Feature-complete CLI tool
- 🎯 **Smart Filtering**: Filter by category, date, author, and other conditions
- 📈 **Performance Optimization**: Memory and network optimization
- 🔧 **Configuration Management**: Flexible configuration system
- 🌐 **RESTful API**: Complete backend API interface
- 🚀 **Enhanced ArXiv API**: Advanced search capabilities with structured queries, multi-field search, and date range filtering
- 🔍 **Structured Search**: Support for field-specific searches (title, author, abstract, categories)
- 📅 **Date Range Queries**: Flexible date filtering for recent papers or specific time periods
- 🏷️ **Category Filtering**: Filter papers by arXiv categories (cs.AI, cs.LG, etc.)
- 🔄 **Backward Compatibility**: Seamless integration with existing codebase

## 🛠️ Quick Start

### 📦 Install Dependencies

```bash
# Clone repository
git clone https://github.com/your-username/arxiv-paper-downloader.git
cd arxiv_paper_download

# Install backend dependencies
pip install -r requirements_backend.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 🚀 Launch Application

#### Method 1: Web Interface (Recommended)

```bash
# Start backend server
python app.py

# Start frontend server in new terminal
cd frontend
npm run dev
```

Then visit `http://localhost:3000` in your browser to use the Web interface.

#### Method 2: Command Line Tool

```bash
# Basic usage
python cli.py --query "machine learning" --max-results 10

# Async download (faster)
python cli.py --query "deep learning" --async --max-concurrent 5
```

#### Method 3: Python API

```python
from arxiv_downloader import ArxivDownloader
from enhanced_arxiv_api import EnhancedArxivAPI, SearchQuery, SearchField, DateRange
from datetime import datetime, timedelta

# Basic usage with original API
downloader = ArxivDownloader(download_dir="./papers")
papers = downloader.search_papers("machine learning", max_results=10)
downloader.download_papers(papers)

# Enhanced API usage
with EnhancedArxivAPI() as api:
    # Basic search
    papers = api.search_papers(query="deep learning", max_results=10)
    
    # Structured search with field-specific queries
    query = SearchQuery(terms=["transformer"], field=SearchField.TITLE)
    papers = api.search_papers(query=query, max_results=5)
    
    # Date range filtering
    date_range = DateRange(
        start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        end_date=datetime.now().strftime("%Y-%m-%d")
    )
    papers = api.search_papers(
        query="neural networks",
        date_range=date_range,
        categories=["cs.AI", "cs.LG"]
    )
```

## 📖 Detailed Usage Guide

### 🚀 Enhanced ArXiv API Features

#### Advanced Search Capabilities
- **🔍 Structured Queries**: Use `SearchQuery` objects for precise field-specific searches
- **📝 Multi-field Search**: Search across title, author, abstract, categories, and more
- **📅 Date Range Filtering**: Filter papers by submission or update date ranges
- **🏷️ Category Filtering**: Filter by single or multiple arXiv categories
- **🔄 Flexible Sorting**: Sort by relevance, submission date, or update date
- **📋 Batch ID Queries**: Retrieve multiple papers by arXiv ID list
- **⚡ Auto-retry**: Built-in retry mechanism with exponential backoff
- **🛡️ Error Handling**: Comprehensive error classification and handling

#### Enhanced API Examples

```python
from enhanced_arxiv_api import (
    EnhancedArxivAPI, SearchQuery, SearchField, 
    DateRange, SortBy, SortOrder
)

# Multi-field combination search
queries = [
    SearchQuery(terms=["neural"], field=SearchField.TITLE),
    SearchQuery(terms=["attention"], field=SearchField.ABSTRACT)
]
papers = api.search_papers(
    query=queries,
    categories=["cs.AI", "cs.LG"],
    sort_by=SortBy.SUBMITTED_DATE,
    sort_order=SortOrder.DESCENDING
)

# Convenience functions for common searches
papers = api.search_by_author("Yoshua Bengio", max_results=20)
papers = api.search_recent_papers("computer vision", days=7)
papers = api.search_by_category("cs.CV", max_results=50)
```

### 🌐 Web Interface Features

#### Main Features
- **📝 Paper Search**: Support keyword search with date range and max results settings
- **📊 Search Results**: Display paper title, authors, abstract, publication date and other details
- **⬇️ One-click Download**: Click download button to download PDF with custom download path support
- **📈 Download History**: View all download records including status and progress
- **🎯 Keyword Recommendations**: Smart keyword recommendations based on search history
- **📱 Responsive Design**: Perfect adaptation for various device screens
- **🚀 Enhanced Search**: Leverage enhanced API features through the web interface

#### Usage Steps
1. Enter keywords in the search box (e.g., "machine learning", "transformer", etc.)
2. Optionally set date range and maximum results
3. Click the "Search Papers" button
4. Click the "Download PDF" button in search results
5. Select download path (needs to be set on first use)
6. View download status in "Download History"

### 💻 Command Line Usage

```bash
# Basic search and download
python cli.py --query "machine learning" --max-results 10

# Async download (faster)
python cli.py --query "deep learning" --async --max-concurrent 5

# Filter by category and date
python cli.py --query "AI" --categories "cs.AI,cs.LG" --date-from 2023-01-01

# Custom download directory
python cli.py --query "neural networks" --download-dir "./my_papers"

# Enable plugins
python cli.py --query "computer vision" --enable-plugins "duplicate_check,metadata"
```

### 🐍 Python API Usage

#### Enhanced API (Recommended)
```python
from arxiv_downloader import ArxivDownloader
from enhanced_arxiv_api import DateRange

# Create downloader instance
downloader = ArxivDownloader(download_dir="./papers")

# Search using enhanced API with structured parameters
papers = downloader.search_papers_enhanced(
    query="machine learning",
    max_results=10,
    date_range=DateRange(
        start_date="2023-01-01",
        end_date="2023-12-31"
    ),
    categories=["cs.AI", "cs.LG"]
)

# Download papers
downloader.download_papers(papers)
```

#### Legacy API (Still Supported)
```python
from arxiv_downloader import ArxivDownloader

# Create downloader instance
downloader = ArxivDownloader(download_dir="./papers")

# Search using legacy API
papers = downloader.search_papers(
    query="machine learning",
    max_results=10,
    date_from="2023-01-01",
    date_to="2023-12-31"
)

# Download papers
downloader.download_papers(papers)
```

#### Asynchronous Download (Recommended)
```python
import asyncio
from async_downloader import download_papers_async
from arxiv_downloader import ArxivDownloader

async def main():
    # Search papers
    downloader = ArxivDownloader()
    papers = downloader.search_papers("deep learning", max_results=20)
    
    # Async download
    result = await download_papers_async(
        papers, 
        download_dir="./papers",
        max_concurrent=5
    )
    
    print(f"Successfully downloaded: {result['successful']} papers")
    print(f"Total time: {result['total_time']:.2f} seconds")

# Run
asyncio.run(main())
```

#### Using Plugin System
```python
from plugins import create_default_plugins, PluginManager
from arxiv_downloader import ArxivDownloader

# Create plugin manager
plugin_manager = create_default_plugins("./papers")

# Or manually configure plugins
from plugins import DuplicateCheckPlugin, CategoryFilterPlugin

manager = PluginManager()
manager.register_plugin(DuplicateCheckPlugin("./papers"))
manager.register_plugin(CategoryFilterPlugin(allowed_categories=["cs.AI"]))

# Use plugins during download process
downloader = ArxivDownloader(plugin_manager=manager)
```

### Basic Usage

```bash
# Download latest 10 AI papers
python3 arxiv_downloader.py

# Download latest 20 AI papers
python3 arxiv_downloader.py --max-results 20
```

### Specify Date Range

```bash
# Download papers from January 1 to January 31, 2024
python3 arxiv_downloader.py --date-from 2024-01-01 --date-to 2024-01-31

# Download papers after January 1, 2024
python3 arxiv_downloader.py --date-from 2024-01-01

# Download papers before January 31, 2024
python3 arxiv_downloader.py --date-to 2024-01-31
```

### Quick Date Options

```bash
# Download today's papers
python3 arxiv_downloader.py --today

# Download yesterday's papers
python3 arxiv_downloader.py --yesterday

# Download papers from the last week
python3 arxiv_downloader.py --last-week
```

### Custom Search and Directory

```bash
# Search machine learning related papers
python3 arxiv_downloader.py --query "cat:cs.LG"

# Search papers containing specific keywords
python3 arxiv_downloader.py --query "all:transformer AND cat:cs.AI"

# Specify download directory
python3 arxiv_downloader.py --download-dir "/path/to/your/directory"
```

## Parameter Description

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `--query` | Search query statement | `cat:cs.AI` |
| `--date-from` | Start date (YYYY-MM-DD) | None |
| `--date-to` | End date (YYYY-MM-DD) | None |
| `--max-results` | Maximum number of results | 10 |
| `--download-dir` | Download directory | `~/Downloads/arxiv_papers` |
| `--today` | Download today's papers | - |
| `--yesterday` | Download yesterday's papers | - |
| `--last-week` | Download papers from the last week | - |

## Search Query Syntax

ArXiv supports various search syntaxes:

### Search by Category
- `cat:cs.AI` - Artificial Intelligence
- `cat:cs.LG` - Machine Learning
- `cat:cs.CV` - Computer Vision
- `cat:cs.CL` - Computational Linguistics
- `cat:cs.NE` - Neural Networks

### Search by Keywords
- `all:transformer` - Papers containing "transformer"
- `ti:"deep learning"` - Papers with "deep learning" in title
- `au:"Yoshua Bengio"` - Papers by author "Yoshua Bengio"

### Combined Search
- `cat:cs.AI AND all:transformer` - AI category papers containing transformer
- `cat:cs.LG OR cat:cs.AI` - Machine learning or artificial intelligence category papers

## Scheduled Execution

### Using cron Jobs

```bash
# Edit crontab
crontab -e

# Add the following line to download yesterday's papers at 9 AM daily
0 9 * * * cd /path/to/arxiv_paper_download && python3 arxiv_downloader.py --yesterday

# Download last week's papers at 9 AM every Monday
0 9 * * 1 cd /path/to/arxiv_paper_download && python3 arxiv_downloader.py --last-week
```

### Create Shell Script

```bash
# Create daily_download.sh
#!/bin/bash
cd /path/to/arxiv_paper_download
python3 arxiv_downloader.py --yesterday --max-results 20

# Give script execution permission
chmod +x daily_download.sh

# Run script
./daily_download.sh
```

## Output Files

Downloaded files will be saved in the specified directory:
- `{Paper Title}.pdf` - Paper PDF file (named using cleaned paper title)
- `{Paper Title}_{Paper ID}.pdf` - If title duplicates, ID suffix will be added
- `Download Summary_{YYYYMMDD_HHMM}.md` - Download summary document (with timestamp to avoid overwriting)

### File Naming Rules

- Use paper title as primary filename
- Automatically remove illegal characters from filename (`<>:"/\|?*`)
- Replace multiple spaces with single space
- Limit filename length to no more than 100 characters
- If filename conflicts, automatically add paper ID suffix
- If title cannot be obtained, use "Unknown_Title" as default name

## Example Output

```
Search query: cat:cs.AI+AND+submittedDate:[20240101+TO+20240131]
Searching ArXiv papers...

Found 15 papers, starting download...

[1/15] Downloading: Attention Is All You Need: A Comprehensive Survey...
✓ Download completed: 2401.12345v1.pdf

[2/15] Downloading: Large Language Models for Code Generation...
✓ Download completed: 2401.12346v1.pdf

...

Download completed! Successfully downloaded 15/15 papers
Files saved in: ~/Downloads/arxiv_papers
Summary document generated: ~/Downloads/arxiv_papers/Download Summary.md
```

## Batch Rename Existing Files

If you already have files named with paper IDs, you can use the provided rename script:

```bash
# Rename existing ID-named files to title-based names
python3 rename_existing_papers.py
```

This script will:
- Automatically identify PDF files named with paper IDs
- Fetch corresponding paper titles from ArXiv API
- Rename files to title-based filenames
- Process corresponding Markdown files (if they exist)
- Avoid filename conflicts

## Important Notes

1. **Network Connection**: Ensure stable network connection, downloading large files may take considerable time
2. **Storage Space**: Ensure sufficient disk space to store PDF files
3. **Request Frequency**: Script has built-in request delays to avoid excessive pressure on ArXiv servers
4. **File Overwriting**: If files already exist, script will skip download
5. **Rename Operations**: Rename operations are irreversible, recommend backing up important files first

## Troubleshooting

### Common Issues

1. **Network Timeout**: Increase timeout duration or check network connection
2. **Permission Error**: Ensure write permissions for download directory
3. **Missing Dependencies**: Run `pip3 install requests` to install dependencies

### Debug Mode

If you encounter issues, you can modify the script to add more detailed log output.

## 🏗️ Tech Stack

### Backend
- **Python 3.7+**: Main programming language
- **Flask**: Web framework providing RESTful API
- **Requests**: HTTP request library for ArXiv API interaction
- **Flask-CORS**: Cross-origin resource sharing support

### Frontend
- **Vue.js 3**: Modern frontend framework
- **Vite**: Fast build tool
- **CSS3**: Responsive style design
- **JavaScript ES6+**: Modern JavaScript features

### Core Dependencies
- **ArXiv API**: Paper data source
- **PDF Processing**: Automatic PDF file download and management
- **Async Processing**: Support for high-concurrency downloads

## 📁 Project Structure

```
arxiv_paper_download/
├── 📄 app.py                 # Flask backend server
├── 📄 arxiv_downloader.py     # Core downloader class
├── 📄 async_downloader.py     # Async downloader
├── 📄 cli.py                  # Command line interface
├── 📄 plugins.py              # Plugin system
├── 📄 models.py               # Data models
├── 📄 config.py               # Configuration management
├── 📄 utils.py                # Utility functions
├── 📄 logger.py               # Logging system
├── 📄 cache.py                # Caching mechanism
├── 📄 requirements_backend.txt # Backend dependencies
├── 📄 requirements.txt        # Basic dependencies
├── 📁 frontend/               # Frontend application
│   ├── 📄 package.json        # Frontend dependency configuration
│   ├── 📄 vite.config.js      # Vite configuration
│   ├── 📄 index.html          # Main page
│   └── 📁 src/                # Source code
│       ├── 📄 App.vue         # Main application component
│       ├── 📄 main.js         # Application entry point
│       ├── 📁 api/            # API interfaces
│       ├── 📁 styles/         # Style files
│       └── 📁 views/          # Page components
└── 📄 README.md               # Project documentation
```

## 🔧 API Endpoints

### Search Papers
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

### Download Papers
```http
POST /api/papers/download
Content-Type: application/json

{
  "paper_id": "2301.12345v1",
  "title": "Paper Title",
  "download_path": "/path/to/download"
}
```

### Get Download History
```http
GET /api/downloads
```

### Get Keyword Recommendations
```http
GET /api/keywords/recommendations
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Changelog

### v2.0.0 (Latest)
- ✨ Added modern Web interface
- ✨ Support for user-defined download paths
- ✨ Added keyword recommendation feature
- ✨ Complete RESTful API
- 🐛 Fixed paper ID version number handling issues
- 🎨 Optimized user interface and experience

### v1.0.0
- ✨ Basic command line tool
- ✨ Async download support
- ✨ Plugin system
- ✨ Smart file naming

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ArXiv](https://arxiv.org/) - Providing open academic paper data
- [Vue.js](https://vuejs.org/) - Excellent frontend framework
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework

---

If this project helps you, please give it a ⭐ Star!