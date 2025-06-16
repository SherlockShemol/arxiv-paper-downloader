#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

def test_direct_api(search_query, description):
    """Test ArXiv API directly with different formats"""
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
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            total_results = root.find('.//{http://a9.com/-/spec/opensearch/1.1/}totalResults')
            total = int(total_results.text) if total_results is not None else 0
            print(f"Total results: {total}")
            
            if total > 0:
                entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
                print(f"Entries returned: {len(entries)}")
                
                for i, entry in enumerate(entries[:2], 1):
                    title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
                    published_elem = entry.find('.//{http://www.w3.org/2005/Atom}published')
                    title = title_elem.text.strip() if title_elem is not None else "No title"
                    published = published_elem.text if published_elem is not None else "No date"
                    print(f"  {i}. {title[:60]}...")
                    print(f"     Published: {published}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing different date query formats...")
    
    # Test formats that we know work
    test_queries = [
        # First, test what we know works
        ("submittedDate:20241201*", "Single date wildcard (known to work)"),
        
        # Test with topic + date combinations
        ("machine learning AND submittedDate:20241201*", "Topic + single date wildcard"),
        ("deep learning AND submittedDate:20241201*", "Deep learning + single date wildcard"),
        
        # Test range formats
        ("submittedDate:[20241201* TO 20241203*]", "Range with wildcards and spaces"),
        ("submittedDate:[20241201*+TO+20241203*]", "Range with wildcards and plus"),
        ("submittedDate:[20241201 TO 20241203]", "Range without wildcards"),
        ("submittedDate:[202412010000 TO 202412032359]", "Range with full timestamps"),
        
        # Test with topics
        ("machine learning AND submittedDate:[20241201* TO 20241203*]", "Topic + range wildcards spaces"),
        ("machine learning AND submittedDate:[20241201*+TO+20241203*]", "Topic + range wildcards plus"),
        ("machine learning AND submittedDate:[20241201 TO 20241203]", "Topic + range no wildcards"),
        
        # Test month ranges
        ("submittedDate:[202412* TO 202412*]", "Month range with wildcards"),
        ("machine learning AND submittedDate:[202412* TO 202412*]", "Topic + month range"),
    ]
    
    for query, description in test_queries:
        test_direct_api(query, description)