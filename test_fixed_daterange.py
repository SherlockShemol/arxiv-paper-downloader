#!/usr/bin/env python3

from enhanced_arxiv_api import EnhancedArxivAPI, DateRange, SearchField
from datetime import datetime, timedelta

def test_daterange_with_real_dates():
    """Test DateRange with actual dates that exist in ArXiv"""
    print("Testing DateRange with real dates...")
    
    api = EnhancedArxivAPI()
    
    # Test with December 2024 (we know this has papers)
    print("\n=== Test 1: December 1, 2024 ====")
    date_range = DateRange(
        start_date="2024-12-01",
        end_date="2024-12-01",
        field=SearchField.SUBMITTED_DATE
    )
    
    print(f"Date range query string: {date_range.to_query_string()}")
    
    try:
        papers = api.search_papers(
            query="machine learning",
            date_range=date_range,
            max_results=5
        )
        
        print(f"Number of papers found: {len(papers)}")
        
        for i, paper in enumerate(papers[:3], 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Published: {paper.published}")
            print(f"   Categories: {', '.join(paper.categories)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with a range in December 2024
    print("\n=== Test 2: December 1-3, 2024 ====")
    date_range = DateRange(
        start_date="2024-12-01",
        end_date="2024-12-03",
        field=SearchField.SUBMITTED_DATE
    )
    
    print(f"Date range query string: {date_range.to_query_string()}")
    
    try:
        papers = api.search_papers(
            query="deep learning",
            date_range=date_range,
            max_results=10
        )
        
        print(f"Number of papers found: {len(papers)}")
        
        for i, paper in enumerate(papers[:3], 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Published: {paper.published}")
            print(f"   Categories: {', '.join(paper.categories)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with November 2024
    print("\n=== Test 3: November 2024 ====")
    date_range = DateRange(
        start_date="2024-11-01",
        end_date="2024-11-30",
        field=SearchField.SUBMITTED_DATE
    )
    
    print(f"Date range query string: {date_range.to_query_string()}")
    
    try:
        papers = api.search_papers(
            query="neural network",
            date_range=date_range,
            max_results=5
        )
        
        print(f"Number of papers found: {len(papers)}")
        
        for i, paper in enumerate(papers[:2], 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Published: {paper.published}")
            print(f"   Categories: {', '.join(paper.categories)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_daterange_with_real_dates()