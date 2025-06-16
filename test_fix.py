#!/usr/bin/env python3

from arxiv_downloader import ArxivDownloader

def test_search():
    """Test the search functionality"""
    try:
        downloader = ArxivDownloader()
        
        # Test 1: Search by ID
        print("Testing search by ID: 1811.04422")
        papers = downloader.search_papers(query='1811.04422', max_results=1)
        print(f"Found {len(papers)} papers")
        
        if papers:
            paper = papers[0]
            print(f"Title: {paper.title}")
            print(f"ID: {paper.id}")
            print(f"Authors: {', '.join(paper.authors)}")
            print(f"URL: {paper.url}")
        else:
            print("No papers found")
        
        # Test 2: Search by keyword
        print("\nTesting search by keyword: adversarial machine learning")
        papers2 = downloader.search_papers(query='adversarial machine learning', max_results=3)
        print(f"Found {len(papers2)} papers")
        
        for i, paper in enumerate(papers2[:2], 1):
            print(f"{i}. {paper.title} ({paper.id})")
        
        print("\nSearch tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()