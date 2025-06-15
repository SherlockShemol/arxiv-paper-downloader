#!/usr/bin/env python3
"""
Enhanced ArXiv API Usage Examples

This file demonstrates various ways to use the enhanced arXiv API client
with different search patterns and configurations.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_arxiv_api import (
    EnhancedArxivAPI,
    SearchQuery,
    SearchField,
    DateRange,
    SortBy,
    SortOrder,
    search_by_keyword,
    search_by_author,
    search_by_category,
    get_recent_papers
)
from arxiv_downloader import ArxivDownloader


def example_1_basic_search():
    """Example 1: Basic keyword search"""
    print("\n=== Example 1: Basic Keyword Search ===")
    
    with EnhancedArxivAPI() as api:
        papers = api.search_papers(
            query="machine learning",
            max_results=5,
            sort_by=SortBy.RELEVANCE
        )
        
        print(f"Found {len(papers)} papers for 'machine learning'")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:2])}{'...' if len(paper.authors) > 2 else ''}")
            print(f"   Categories: {', '.join(paper.categories[:3])}")
            print()


def example_2_field_specific_search():
    """Example 2: Search in specific fields"""
    print("\n=== Example 2: Field-Specific Search ===")
    
    with EnhancedArxivAPI() as api:
        # Search for "transformer" in titles only
        title_query = SearchQuery(
            terms=["transformer"],
            field=SearchField.TITLE
        )
        
        papers = api.search_papers(
            query=title_query,
            max_results=3,
            sort_by=SortBy.SUBMITTED_DATE,
            sort_order=SortOrder.DESCENDING
        )
        
        print(f"Found {len(papers)} papers with 'transformer' in title")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Published: {paper.published}")
            print()


def example_3_author_search():
    """Example 3: Search by author"""
    print("\n=== Example 3: Author Search ===")
    
    with EnhancedArxivAPI() as api:
        author_query = SearchQuery(
            terms=["Yoshua Bengio"],
            field=SearchField.AUTHOR
        )
        
        papers = api.search_papers(
            query=author_query,
            max_results=5,
            sort_by=SortBy.SUBMITTED_DATE,
            sort_order=SortOrder.DESCENDING
        )
        
        print(f"Found {len(papers)} papers by Yoshua Bengio")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Published: {paper.published}")
            print()


def example_4_category_and_date_filter():
    """Example 4: Category search with date filtering"""
    print("\n=== Example 4: Category + Date Filter ===")
    
    # Get papers from the last 30 days in AI category
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    date_range = DateRange(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    with EnhancedArxivAPI() as api:
        papers = api.search_papers(
            categories=["cs.AI"],
            date_range=date_range,
            max_results=5,
            sort_by=SortBy.SUBMITTED_DATE,
            sort_order=SortOrder.DESCENDING
        )
        
        print(f"Found {len(papers)} recent AI papers (last 30 days)")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Published: {paper.published}")
            print(f"   Categories: {', '.join(paper.categories)}")
            print()


def example_5_multiple_categories():
    """Example 5: Search across multiple categories"""
    print("\n=== Example 5: Multiple Categories ===")
    
    with EnhancedArxivAPI() as api:
        papers = api.search_papers(
            categories=["cs.AI", "cs.LG", "cs.CV"],
            max_results=5,
            sort_by=SortBy.SUBMITTED_DATE,
            sort_order=SortOrder.DESCENDING
        )
        
        print(f"Found {len(papers)} papers in AI/ML/CV categories")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Categories: {', '.join(paper.categories)}")
            print()


def example_6_complex_query():
    """Example 6: Complex multi-field query"""
    print("\n=== Example 6: Complex Query ===")
    
    with EnhancedArxivAPI() as api:
        # Search for papers with "neural" in title AND "attention" in abstract
        queries = [
            SearchQuery(terms=["neural"], field=SearchField.TITLE),
            SearchQuery(terms=["attention"], field=SearchField.ABSTRACT)
        ]
        
        papers = api.search_papers(
            query=queries,
            categories=["cs.AI", "cs.LG"],
            max_results=3
        )
        
        print(f"Found {len(papers)} papers matching complex criteria")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Abstract: {paper.abstract[:150]}...")
            print()


def example_7_specific_papers():
    """Example 7: Get specific papers by arXiv ID"""
    print("\n=== Example 7: Specific Papers by ID ===")
    
    famous_paper_ids = [
        "1706.03762",  # Attention Is All You Need (Transformer)
        "1810.04805",  # BERT
        "2005.14165",  # GPT-3
    ]
    
    with EnhancedArxivAPI() as api:
        papers = api.search_papers(
            id_list=famous_paper_ids,
            max_results=10
        )
        
        print(f"Retrieved {len(papers)} famous papers")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   ID: {paper.id}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            if paper.journal_ref:
                print(f"   Journal: {paper.journal_ref}")
            if paper.doi:
                print(f"   DOI: {paper.doi}")
            print()


def example_8_convenience_functions():
    """Example 8: Using convenience functions"""
    print("\n=== Example 8: Convenience Functions ===")
    
    # Search by keyword
    papers = search_by_keyword("quantum computing", max_results=3)
    print(f"search_by_keyword: {len(papers)} papers on quantum computing")
    
    # Search by author
    papers = search_by_author("Ian Goodfellow", max_results=3)
    print(f"search_by_author: {len(papers)} papers by Ian Goodfellow")
    
    # Search by category
    papers = search_by_category("cs.CV", max_results=3)
    print(f"search_by_category: {len(papers)} papers in computer vision")
    
    # Get recent papers
    papers = get_recent_papers("cs.AI", days=7, max_results=3)
    print(f"get_recent_papers: {len(papers)} recent AI papers")


def example_9_integration_with_downloader():
    """Example 9: Integration with ArxivDownloader"""
    print("\n=== Example 9: Integration with Downloader ===")
    
    downloader = ArxivDownloader()
    
    # Use enhanced search
    papers = downloader.search_papers_enhanced(
        query="deep learning",
        search_field=SearchField.TITLE,
        categories=["cs.LG"],
        max_results=3,
        sort_by=SortBy.SUBMITTED_DATE,
        sort_order=SortOrder.DESCENDING
    )
    
    print(f"Enhanced search found {len(papers)} papers")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.title}")
        print(f"   Categories: {', '.join(paper.categories)}")
        print()


def example_10_error_handling():
    """Example 10: Proper error handling"""
    print("\n=== Example 10: Error Handling ===")
    
    from models import ValidationError, NetworkError, ParseError
    
    try:
        with EnhancedArxivAPI() as api:
            # This should raise a ValidationError
            papers = api.search_papers(max_results=-1)
    except ValidationError as e:
        print(f"✓ Caught ValidationError: {e}")
    
    try:
        with EnhancedArxivAPI() as api:
            # This should raise a ValidationError for invalid ID
            papers = api.search_papers(id_list=["invalid-id"])
    except ValidationError as e:
        print(f"✓ Caught ValidationError for invalid ID: {e}")
    
    try:
        with EnhancedArxivAPI() as api:
            # This should raise a ValidationError for empty parameters
            papers = api.search_papers()
    except ValidationError as e:
        print(f"✓ Caught ValidationError for empty query: {e}")


def main():
    """Run all examples"""
    print("Enhanced ArXiv API Usage Examples")
    print("=" * 50)
    
    examples = [
        example_1_basic_search,
        example_2_field_specific_search,
        example_3_author_search,
        example_4_category_and_date_filter,
        example_5_multiple_categories,
        example_6_complex_query,
        example_7_specific_papers,
        example_8_convenience_functions,
        example_9_integration_with_downloader,
        example_10_error_handling
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")
    
    print("\n=== All Examples Complete ===")


if __name__ == "__main__":
    main()