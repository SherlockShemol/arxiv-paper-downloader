#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

def test_query(search_query, description):
    """Test a specific search query"""
    base_url = "http://export.arxiv.org/api/query"
    
    params = {
        'search_query': search_query,
        'start': 0,
        'max_results': 5,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = f"{base_url}?" + "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
    print(f"\n--- {description} ---")
    print(f"Query: {search_query}")
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
    print("Testing topic vs date filtering...")
    
    # Test different combinations
    test_queries = [
        ("submittedDate:202506*", "Date only - June 2025"),
        ("deep learning", "Topic only - deep learning"),
        ("machine learning", "Topic only - machine learning"),
        ("neural network", "Topic only - neural network"),
        ("deep learning AND submittedDate:202506*", "Both - deep learning + June 2025"),
        ("machine learning AND submittedDate:202506*", "Both - machine learning + June 2025"),
        ("neural network AND submittedDate:202506*", "Both - neural network + June 2025"),
        ("cat:cs.AI AND submittedDate:202506*", "Category cs.AI + June 2025"),
        ("cat:cs.LG AND submittedDate:202506*", "Category cs.LG + June 2025"),
        ("submittedDate:20250613", "Exact date - June 13, 2025"),
        ("all:deep AND submittedDate:202506*", "All fields deep + June 2025"),
        ("ti:deep AND submittedDate:202506*", "Title deep + June 2025"),
        ("abs:learning AND submittedDate:202506*", "Abstract learning + June 2025"),
    ]
    
    for query, description in test_queries:
        test_query(query, description)