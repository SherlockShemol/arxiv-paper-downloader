#!/usr/bin/env python3
"""
Direct test script for ArxivDownloader to debug search query issues
"""

from arxiv_downloader import ArxivDownloader

def test_search_queries():
    """Test different search queries directly"""
    downloader = ArxivDownloader()
    
    print("=== Testing Machine Learning Query ===")
    try:
        papers1 = downloader.search_papers(
            query="machine learning",
            max_results=3
        )
        print(f"Found {len(papers1)} papers for 'machine learning'")
        for i, paper in enumerate(papers1, 1):
            print(f"{i}. {paper.title}")
    except Exception as e:
        print(f"Error with machine learning query: {e}")
    
    print("\n=== Testing Quantum Learning Query ===")
    try:
        papers2 = downloader.search_papers(
            query="quantum learning",
            max_results=3
        )
        print(f"Found {len(papers2)} papers for 'quantum learning'")
        for i, paper in enumerate(papers2, 1):
            print(f"{i}. {paper.title}")
    except Exception as e:
        print(f"Error with quantum learning query: {e}")
    
    print("\n=== Comparing Results ===")
    if 'papers1' in locals() and 'papers2' in locals():
        if len(papers1) > 0 and len(papers2) > 0:
            same_titles = [p1.title for p1 in papers1 if p1.title in [p2.title for p2 in papers2]]
            print(f"Identical papers found: {len(same_titles)}")
            if same_titles:
                print("Identical titles:")
                for title in same_titles:
                    print(f"  - {title}")
            else:
                print("No identical papers - this would be the expected behavior!")
        else:
            print("One or both queries returned no results")

if __name__ == "__main__":
    test_search_queries()