# Enhanced ArXiv API Client

基于 [arXiv API 官方文档](https://info.arxiv.org/help/api/index.html) 重新构建的增强版 arXiv API 客户端。

## 主要特性

### 🚀 增强功能
- **结构化查询支持**: 使用 `SearchQuery` 对象进行精确的字段搜索
- **多字段搜索**: 支持标题、作者、摘要、类别等多个字段的组合搜索
- **日期范围过滤**: 灵活的日期范围查询功能
- **多种排序选项**: 按相关性、提交日期、更新日期排序
- **类别过滤**: 支持单个或多个 arXiv 类别过滤
- **ID 批量查询**: 通过 arXiv ID 列表批量获取论文
- **便利函数**: 提供常用搜索模式的快捷函数

### 🛡️ 可靠性改进
- **完整的错误处理**: 网络错误、解析错误、验证错误的分类处理
- **自动重试机制**: 指数退避的请求重试策略
- **参数验证**: 严格的输入参数验证
- **会话管理**: 自动的 HTTP 会话管理和资源清理

### 🔧 向后兼容
- **无缝集成**: 与现有 `ArxivDownloader` 类完全兼容
- **渐进式升级**: 可以逐步迁移到新 API
- **保持接口**: 原有接口继续可用

## 快速开始

### 基本使用

```python
from enhanced_arxiv_api import EnhancedArxivAPI

# 创建 API 客户端
with EnhancedArxivAPI() as api:
    # 基本关键词搜索
    papers = api.search_papers(
        query="machine learning",
        max_results=10
    )
    
    for paper in papers:
        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"Categories: {', '.join(paper.categories)}")
        print()
```

### 结构化查询

```python
from enhanced_arxiv_api import (
    EnhancedArxivAPI, 
    SearchQuery, 
    SearchField, 
    SortBy, 
    SortOrder
)

with EnhancedArxivAPI() as api:
    # 在标题中搜索 "transformer"
    query = SearchQuery(
        terms=["transformer"],
        field=SearchField.TITLE
    )
    
    papers = api.search_papers(
        query=query,
        max_results=5,
        sort_by=SortBy.SUBMITTED_DATE,
        sort_order=SortOrder.DESCENDING
    )
```

### 多字段组合查询

```python
# 组合多个搜索条件
queries = [
    SearchQuery(terms=["neural"], field=SearchField.TITLE),
    SearchQuery(terms=["attention"], field=SearchField.ABSTRACT)
]

papers = api.search_papers(
    query=queries,
    categories=["cs.AI", "cs.LG"],
    max_results=10
)
```

### 日期范围过滤

```python
from enhanced_arxiv_api import DateRange
from datetime import datetime, timedelta

# 搜索最近 30 天的论文
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

date_range = DateRange(
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)

papers = api.search_papers(
    query="deep learning",
    date_range=date_range,
    max_results=20
)
```

### 按 ID 获取特定论文

```python
# 获取特定论文
famous_papers = [
    "1706.03762",  # Attention Is All You Need
    "1810.04805",  # BERT
    "2005.14165",  # GPT-3
]

papers = api.search_papers(
    id_list=famous_papers,
    max_results=10
)
```

## 便利函数

为常见的搜索模式提供了便利函数：

```python
from enhanced_arxiv_api import (
    search_by_keyword,
    search_by_author,
    search_by_category,
    get_recent_papers
)

# 关键词搜索
papers = search_by_keyword("quantum computing", max_results=10)

# 作者搜索
papers = search_by_author("Geoffrey Hinton", max_results=10)

# 类别搜索
papers = search_by_category("cs.CV", max_results=10)

# 获取最近论文
papers = get_recent_papers("cs.AI", days=7, max_results=20)
```

## 与现有代码集成

### 在 ArxivDownloader 中使用

```python
from arxiv_downloader import ArxivDownloader
from enhanced_arxiv_api import SearchField, SortBy, SortOrder

downloader = ArxivDownloader()

# 使用增强搜索功能
papers = downloader.search_papers_enhanced(
    query="deep learning",
    search_field=SearchField.TITLE,
    categories=["cs.LG"],
    max_results=10,
    sort_by=SortBy.SUBMITTED_DATE,
    sort_order=SortOrder.DESCENDING
)

# 下载论文
for paper in papers:
    downloader.download_paper(paper)
```

## 搜索字段说明

| 字段 | 枚举值 | 描述 |
|------|--------|------|
| 全部字段 | `SearchField.ALL` | 在所有字段中搜索 |
| 标题 | `SearchField.TITLE` | 仅在论文标题中搜索 |
| 作者 | `SearchField.AUTHOR` | 仅在作者信息中搜索 |
| 摘要 | `SearchField.ABSTRACT` | 仅在论文摘要中搜索 |
| 评论 | `SearchField.COMMENT` | 仅在论文评论中搜索 |
| 期刊引用 | `SearchField.JOURNAL_REF` | 仅在期刊引用中搜索 |
| 类别 | `SearchField.CATEGORY` | 仅在主题类别中搜索 |
| 报告编号 | `SearchField.REPORT_NUM` | 仅在报告编号中搜索 |
| arXiv ID | `SearchField.ID` | 仅在 arXiv ID 中搜索 |
| 提交日期 | `SearchField.SUBMITTED_DATE` | 按提交日期搜索 |
| 更新日期 | `SearchField.LAST_UPDATED_DATE` | 按最后更新日期搜索 |

## 排序选项

### 排序标准 (SortBy)
- `SortBy.RELEVANCE`: 按相关性排序（默认）
- `SortBy.LAST_UPDATED_DATE`: 按最后更新日期排序
- `SortBy.SUBMITTED_DATE`: 按提交日期排序

### 排序顺序 (SortOrder)
- `SortOrder.DESCENDING`: 降序排列（默认）
- `SortOrder.ASCENDING`: 升序排列

## 常用 arXiv 类别

### 计算机科学
- `cs.AI`: 人工智能
- `cs.LG`: 机器学习
- `cs.CV`: 计算机视觉
- `cs.CL`: 计算语言学
- `cs.NE`: 神经与进化计算
- `cs.RO`: 机器人学

### 数学
- `math.ST`: 统计学
- `math.OC`: 优化与控制
- `math.PR`: 概率论

### 物理学
- `physics.data-an`: 数据分析
- `quant-ph`: 量子物理

### 统计学
- `stat.ML`: 机器学习统计
- `stat.TH`: 统计理论

## 错误处理

```python
from models import ValidationError, NetworkError, ParseError

try:
    with EnhancedArxivAPI() as api:
        papers = api.search_papers(
            query="machine learning",
            max_results=10
        )
except ValidationError as e:
    print(f"参数验证错误: {e}")
except NetworkError as e:
    print(f"网络请求错误: {e}")
except ParseError as e:
    print(f"响应解析错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 高级用法

### 自定义 API 客户端

```python
api = EnhancedArxivAPI(
    timeout=30,           # 请求超时时间
    max_retries=5,        # 最大重试次数
    retry_delay=2.0,      # 重试延迟
    user_agent="MyApp/1.0" # 自定义 User-Agent
)
```

### 复杂查询示例

```python
# 搜索最近一年内，在 AI 或 ML 类别中，
# 标题包含 "transformer" 或 "attention" 的论文
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

date_range = DateRange(
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)

query = SearchQuery(
    terms=["transformer", "attention"],
    field=SearchField.TITLE,
    operator="OR"
)

papers = api.search_papers(
    query=query,
    categories=["cs.AI", "cs.LG"],
    date_range=date_range,
    max_results=50,
    sort_by=SortBy.SUBMITTED_DATE,
    sort_order=SortOrder.DESCENDING
)
```

## 性能优化

### 缓存机制
- 搜索结果自动缓存，避免重复请求
- 缓存键基于查询参数生成
- 支持增强搜索的缓存

### 请求优化
- 自动会话管理
- 连接池复用
- 指数退避重试
- 合理的超时设置

## 测试和示例

### 运行测试
```bash
# 运行基本功能测试
python3 test_enhanced_api.py

# 运行详细示例
python3 enhanced_api_examples.py
```

### 示例文件
- `test_enhanced_api.py`: 基本功能测试
- `enhanced_api_examples.py`: 详细使用示例
- `ENHANCED_API_README.md`: 本文档

## API 参考

### EnhancedArxivAPI 类

#### 构造函数
```python
EnhancedArxivAPI(
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    user_agent: str = "Enhanced-ArXiv-Client/1.0"
)
```

#### 主要方法

##### search_papers
```python
search_papers(
    query: Union[str, SearchQuery, List[SearchQuery]] = None,
    id_list: Optional[List[str]] = None,
    date_range: Optional[DateRange] = None,
    categories: Optional[List[str]] = None,
    max_results: int = 10,
    start: int = 0,
    sort_by: SortBy = SortBy.RELEVANCE,
    sort_order: SortOrder = SortOrder.DESCENDING
) -> List[Paper]
```

##### get_paper_by_id
```python
get_paper_by_id(
    arxiv_id: str, 
    version: Optional[int] = None
) -> Optional[Paper]
```

### 数据类

#### SearchQuery
```python
@dataclass
class SearchQuery:
    terms: List[str]
    field: SearchField = SearchField.ALL
    operator: str = "AND"  # AND, OR, ANDNOT
```

#### DateRange
```python
@dataclass
class DateRange:
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD
    field: SearchField = SearchField.SUBMITTED_DATE
```

#### Paper (增强版)
```python
@dataclass
class Paper:
    id: str
    title: str
    authors: List[str]
    abstract: str
    pdf_url: str
    published: str
    categories: List[str]
    comment: Optional[str] = None      # 新增
    journal_ref: Optional[str] = None  # 新增
    doi: Optional[str] = None          # 新增
```

## 迁移指南

### 从旧 API 迁移

#### 基本搜索
```python
# 旧方式
downloader = ArxivDownloader()
papers = downloader.search_papers("machine learning", max_results=10)

# 新方式（向后兼容）
papers = downloader.search_papers("machine learning", max_results=10)

# 新方式（增强功能）
papers = downloader.search_papers_enhanced(
    query="machine learning",
    max_results=10
)
```

#### 类别搜索
```python
# 旧方式
papers = downloader.search_papers(
    "machine learning", 
    categories=["cs.LG"]
)

# 新方式
papers = downloader.search_papers_enhanced(
    categories=["cs.LG"]
)
```

## 最佳实践

### 1. 使用上下文管理器
```python
# 推荐
with EnhancedArxivAPI() as api:
    papers = api.search_papers(query="machine learning")

# 或者手动管理
api = EnhancedArxivAPI()
try:
    papers = api.search_papers(query="machine learning")
finally:
    api.close()
```

### 2. 合理设置搜索参数
```python
# 避免过大的 max_results
papers = api.search_papers(
    query="machine learning",
    max_results=100  # 考虑分页
)

# 使用具体的搜索字段
query = SearchQuery(
    terms=["transformer"],
    field=SearchField.TITLE  # 比 ALL 更精确
)
```

### 3. 错误处理
```python
from models import ValidationError, NetworkError, ParseError

try:
    papers = api.search_papers(query="machine learning")
except ValidationError:
    # 处理参数错误
    pass
except NetworkError:
    # 处理网络错误，可能需要重试
    pass
except ParseError:
    # 处理解析错误
    pass
```

### 4. 性能优化
```python
# 利用缓存
api = EnhancedArxivAPI()

# 第一次请求
papers1 = api.search_papers(query="machine learning")

# 第二次相同请求会使用缓存
papers2 = api.search_papers(query="machine learning")
```

## 常见问题

### Q: 如何搜索特定作者的所有论文？
A: 使用作者字段搜索：
```python
query = SearchQuery(
    terms=["Geoffrey Hinton"],
    field=SearchField.AUTHOR
)
papers = api.search_papers(query=query, max_results=100)
```

### Q: 如何获取最新的论文？
A: 按提交日期降序排序：
```python
papers = api.search_papers(
    categories=["cs.AI"],
    sort_by=SortBy.SUBMITTED_DATE,
    sort_order=SortOrder.DESCENDING,
    max_results=20
)
```

### Q: 如何搜索多个关键词？
A: 使用多个术语：
```python
query = SearchQuery(
    terms=["neural network", "deep learning"],
    operator="OR"
)
```

### Q: 如何限制搜索的时间范围？
A: 使用日期范围：
```python
date_range = DateRange(
    start_date="2023-01-01",
    end_date="2023-12-31"
)
papers = api.search_papers(
    query="machine learning",
    date_range=date_range
)
```

## 更新日志

### v1.0.0 (当前版本)
- 基于 arXiv API 官方文档重新构建
- 添加结构化查询支持
- 增强错误处理和重试机制
- 支持多字段搜索和复杂查询
- 添加便利函数
- 完整的向后兼容性
- 增强的 Paper 模型（添加 comment、journal_ref、doi 字段）

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

本项目遵循原项目的许可证。