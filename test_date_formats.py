#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

def test_date_format(query_part, description):
    """Test a specific date format"""
    base_url = "http://export.arxiv.org/api/query"
    full_query = f"deep learning AND {query_part}"
    
    params = {
        'search_query': full_query,
        'start': 0,
        'max_results': 5,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = f"{base_url}?" + "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
    print(f"\n--- {description} ---")
    print(f"Query: {full_query}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            total_results = root.find('.//{http://a9.com/-/spec/opensearch/1.1/}totalResults')
            total = int(total_results.text) if total_results is not None else 0
            print(f"Total results: {total}")
            
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            print(f"Entries returned: {len(entries)}")
            
            for i, entry in enumerate(entries[:3], 1):
                title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
                published_elem = entry.find('.//{http://www.w3.org/2005/Atom}published')
                title = title_elem.text.strip() if title_elem is not None else "No title"
                published = published_elem.text if published_elem is not None else "No date"
                print(f"  {i}. {title[:80]}...")
                print(f"     Published: {published}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing different date formats for ArXiv API...")
    
    # Test various date formats
    test_formats = [
        ("submittedDate:[20250601* TO 20250615*]", "Wildcard range with spaces"),
        ("submittedDate:[20250601*+TO+20250615*]", "Wildcard range with plus"),
        ("submittedDate:[202506* TO 202506*]", "Month wildcard range"),
        ("submittedDate:202506*", "Simple month wildcard"),
        ("submittedDate:[20250601 TO 20250615]", "Simple date range"),
        ("submittedDate:[202506010000 TO 202506152359]", "Full timestamp range"),
        ("submittedDate:20250613", "Exact date"),
        ("submittedDate:2025*", "Year wildcard"),
    ]
    
    for query_part, description in test_formats:
        test_date_format(query_part, description)
    
    print("\n=== Testing without 'deep learning' constraint ===")
    # Test without the 'deep learning' constraint
    test_date_format("submittedDate:202506*", "Month wildcard only (no topic filter)")