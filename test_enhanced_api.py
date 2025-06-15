#!/usr/bin/env python3
"""
Test script for Enhanced ArXiv API

This script demonstrates the usage of the enhanced arXiv API client
and validates its functionality with various query types.
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
from models import ValidationError, NetworkError, ParseError


def test_basic_search():
    """Test basic keyword search"""
    print("\n=== Testing Basic Search ===")
    try:
        with EnhancedArxivAPI() as api:
            papers = api.search_papers(
                query="machine learning",
                max_results=5
            )
            print(f"Found {len(papers)} papers for 'machine learning'")
            for i, paper in enumerate(papers[:3], 1):
                print(f"{i}. {paper.title[:80]}...")
                print(f"   Authors: {', '.join(paper.authors[:3])}")
                print(f"   Categories: {', '.join(paper.categories[:3])}")
                print()
    except Exception as e:
        print(f"Error in basic search: {e}")


def test_structured_query():
    """Test structured query with SearchQuery objects"""
    print("\n=== Testing Structured Query ===")
    try:
        with EnhancedArxivAPI() as api:
            # Search for papers with "neural network" in title
            query = SearchQuery(
                terms=["neural network"],
                field=SearchField.TITLE
            )
            papers = api.search_papers(
                query=query,
                max_results=3,
                sort_by=SortBy.SUBMITTED_DATE,
                sort_order=SortOrder.DESCENDING
            )
            print(f"Found {len(papers)} papers with 'neural network' in title")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.title}")
                print(f"   Published: {paper.published}")
                print()
    except Exception as e:
        print(f"Error in structured query: {e}")


def test_multiple_queries():
    """Test combining multiple search queries"""
    print("\n=== Testing Multiple Queries ===")
    try:
        with EnhancedArxivAPI() as api:
            # Search for papers with specific terms in different fields
            queries = [
                SearchQuery(terms=["transformer"], field=SearchField.TITLE),
                SearchQuery(terms=["attention"], field=SearchField.ABSTRACT)
            ]
            papers = api.search_papers(
                query=queries,
                max_results=3
            )
            print(f"Found {len(papers)} papers matching multiple criteria")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.title[:80]}...")
                print()
    except Exception as e:
        print(f"Error in multiple queries: {e}")


def test_date_range_search():
    """Test search with date range filter"""
    print("\n=== Testing Date Range Search ===")
    try:
        with EnhancedArxivAPI() as api:
            # Search for papers from the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            date_range = DateRange(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            papers = api.search_papers(
                query="deep learning",
                date_range=date_range,
                max_results=5,
                sort_by=SortBy.SUBMITTED_DATE,
                sort_order=SortOrder.DESCENDING
            )
            print(f"Found {len(papers)} recent papers on 'deep learning'")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.title[:80]}...")
                print(f"   Published: {paper.published}")
                print()
    except Exception as e:
        print(f"Error in date range search: {e}")


def test_category_search():
    """Test search by category"""
    print("\n=== Testing Category Search ===")
    try:
        with EnhancedArxivAPI() as api:
            papers = api.search_papers(
                categories=["cs.AI", "cs.LG"],
                max_results=5,
                sort_by=SortBy.SUBMITTED_DATE,
                sort_order=SortOrder.DESCENDING
            )
            print(f"Found {len(papers)} papers in AI/ML categories")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.title[:80]}...")
                print(f"   Categories: {', '.join(paper.categories)}")
                print()
    except Exception as e:
        print(f"Error in category search: {e}")


def test_id_search():
    """Test search by arXiv ID"""
    print("\n=== Testing ID Search ===")
    try:
        with EnhancedArxivAPI() as api:
            # Search for specific papers by ID
            papers = api.search_papers(
                id_list=["1706.03762", "1810.04805"],  # Transformer and BERT papers
                max_results=10
            )
            print(f"Found {len(papers)} papers by ID")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.title}")
                print(f"   ID: {paper.id}")
                print(f"   Authors: {', '.join(paper.authors[:3])}")
                print()
    except Exception as e:
        print(f"Error in ID search: {e}")


def test_convenience_functions():
    """Test convenience functions"""
    print("\n=== Testing Convenience Functions ===")
    
    # Test search by keyword
    try:
        papers = search_by_keyword("quantum computing", max_results=3)
        print(f"search_by_keyword found {len(papers)} papers")
    except Exception as e:
        print(f"Error in search_by_keyword: {e}")
    
    # Test search by author
    try:
        papers = search_by_author("Geoffrey Hinton", max_results=3)
        print(f"search_by_author found {len(papers)} papers")
    except Exception as e:
        print(f"Error in search_by_author: {e}")
    
    # Test search by category
    try:
        papers = search_by_category("cs.CV", max_results=3)
        print(f"search_by_category found {len(papers)} papers")
    except Exception as e:
        print(f"Error in search_by_category: {e}")
    
    # Test get recent papers
    try:
        papers = get_recent_papers("cs.AI", days=7, max_results=3)
        print(f"get_recent_papers found {len(papers)} papers")
    except Exception as e:
        print(f"Error in get_recent_papers: {e}")


def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    
    # Test validation errors
    try:
        with EnhancedArxivAPI() as api:
            api.search_papers(max_results=-1)
    except ValidationError as e:
        print(f"✓ Caught expected ValidationError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test invalid arXiv ID
    try:
        with EnhancedArxivAPI() as api:
            api.search_papers(id_list=["invalid-id"])
    except ValidationError as e:
        print(f"✓ Caught expected ValidationError for invalid ID: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test empty query
    try:
        with EnhancedArxivAPI() as api:
            api.search_papers()
    except ValidationError as e:
        print(f"✓ Caught expected ValidationError for empty query: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def test_get_paper_by_id():
    """Test getting a specific paper by ID"""
    print("\n=== Testing Get Paper by ID ===")
    try:
        with EnhancedArxivAPI() as api:
            # Get the famous "Attention Is All You Need" paper
            paper = api.get_paper_by_id("1706.03762")
            if paper:
                print(f"Found paper: {paper.title}")
                print(f"Authors: {', '.join(paper.authors)}")
                print(f"Abstract: {paper.abstract[:200]}...")
            else:
                print("Paper not found")
    except Exception as e:
        print(f"Error getting paper by ID: {e}")


def main():
    """Run all tests"""
    print("Enhanced ArXiv API Test Suite")
    print("=" * 50)
    
    # Run all test functions
    test_functions = [
        test_basic_search,
        test_structured_query,
        test_multiple_queries,
        test_date_range_search,
        test_category_search,
        test_id_search,
        test_get_paper_by_id,
        test_convenience_functions,
        test_error_handling
    ]
    
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print(f"Test {test_func.__name__} failed with error: {e}")
    
    print("\n=== Test Suite Complete ===")


if __name__ == "__main__":
    main()