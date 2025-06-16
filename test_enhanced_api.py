#!/usr/bin/env python3
import sys
sys.path.append('.')

from enhanced_arxiv_api import EnhancedArxivAPI, DateRange
from datetime import datetime

# Test our enhanced API
api = EnhancedArxivAPI()

print("Testing Enhanced ArXiv API...")

# Create date range
date_range = DateRange("2025-06-01", "2025-06-15")
print(f"Date range query string: {date_range.to_query_string()}")

try:
    # Search with date range
    papers = api.search_papers(
        query="deep learning",
        date_range=date_range,
        max_results=10
    )
    
    print(f"\nNumber of papers found: {len(papers)}")
    
    # Print first few papers
    for i, paper in enumerate(papers[:3]):
        print(f"\nPaper {i+1}:")
        print(f"  ID: {paper.id}")
        print(f"  Title: {paper.title}")
        print(f"  Published: {paper.published}")
        print(f"  Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()

api.close()