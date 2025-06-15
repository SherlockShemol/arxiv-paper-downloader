#!/usr/bin/env python3
"""
Debug script to examine the actual HTTP requests sent to ArXiv API
"""

import requests
from urllib.parse import urlencode

def test_arxiv_api_directly():
    """Test ArXiv API directly using enhanced API"""
    from enhanced_arxiv_api import EnhancedArxivAPI
    
    print("=== Testing Machine Learning Query with Enhanced API ===")
    
    try:
        with EnhancedArxivAPI() as api:
            papers = api.search_papers(
                query="machine learning",
                max_results=3
            )
            
            print(f"Found {len(papers)} papers")
            for i, paper in enumerate(papers, 1):
                print(f"  {i}. {paper.title}")
                print(f"     Authors: {', '.join(paper.authors)}")
                print(f"     Categories: {', '.join(paper.categories)}")
                print(f"     Published: {paper.published}")
                print()
                
    except Exception as e:
        print(f"Error: {e}")
        return
    
    print("\n=== Testing Quantum Learning Query with Enhanced API ===")
    try:
        with EnhancedArxivAPI() as api:
            papers2 = api.search_papers(
                query="quantum learning",
                max_results=3
            )
            
            print(f"Found {len(papers2)} papers")
            titles2 = []
            for i, paper in enumerate(papers2, 1):
                titles2.append(paper.title)
                print(f"  {i}. {paper.title}")
                print(f"     Authors: {', '.join(paper.authors)}")
                print(f"     Categories: {', '.join(paper.categories)}")
                print()
                
    except Exception as e:
        print(f"Error: {e}")
        return
    
    print("\n=== Comparison ===")
    titles1 = [paper.title for paper in papers]
    if titles1 and titles2:
        identical = set(titles1) & set(titles2)
        print(f"Identical titles: {len(identical)}")
        if identical:
            print("Identical papers:")
            for title in identical:
                print(f"  - {title}")
        else:
            print("No identical papers found!")
    
    print("\n=== Testing with Different Sort Order (Enhanced API) ===")
    try:
        from enhanced_arxiv_api import SortBy, SortOrder
        with EnhancedArxivAPI() as api:
            papers3 = api.search_papers(
                query="machine learning",
                max_results=3,
                sort_by=SortBy.RELEVANCE,
                sort_order=SortOrder.DESCENDING
            )
            
            print(f"Found {len(papers3)} papers (relevance sort)")
            for i, paper in enumerate(papers3, 1):
                print(f"  {i}. {paper.title}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_arxiv_api_directly()