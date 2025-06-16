#!/usr/bin/env python3
import sys
sys.path.append('.')

import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

# Test with correct ArXiv date format based on official documentation
print("=== Testing ArXiv API with Correct Date Format ===")
base_url = "http://export.arxiv.org/api/query"

# According to ArXiv API documentation, date format should be YYYYMMDDHHMMSS
# and we can use wildcards like 20250613* for all papers on 2025-06-13
test_cases = [
    {
        'name': 'June 13, 2025 (wildcard)',
        'query': 'deep learning AND submittedDate:20250613*'
    },
    {
        'name': 'June 2025 (wildcard)',
        'query': 'deep learning AND submittedDate:202506*'
    },
    {
        'name': 'All of 2025 (wildcard)',
        'query': 'deep learning AND submittedDate:2025*'
    },
    {
        'name': 'Range format June 1-15, 2025',
        'query': 'deep learning AND submittedDate:[20250601* TO 20250615*]'
    },
    {
        'name': 'Any category June 13, 2025',
        'query': 'submittedDate:20250613*'
    },
    {
        'name': 'cs.AI June 2025',
        'query': 'cat:cs.AI AND submittedDate:202506*'
    }
]

namespaces = {'atom': 'http://www.w3.org/2005/Atom'}

for test_case in test_cases:
    print(f"\n--- {test_case['name']} ---")
    params = {
        'search_query': test_case['query'],
        'start': 0,
        'max_results': 5,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = f"{base_url}?{urlencode(params)}"
    print(f"Query URL: {url}")
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            entries = root.findall('atom:entry', namespaces)
            total_results = root.find('.//opensearch:totalResults', {'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'})
            
            total = total_results.text if total_results is not None else 'Unknown'
            print(f"Total results: {total}")
            print(f"Entries returned: {len(entries)}")
            
            if entries:
                for i, entry in enumerate(entries[:2]):
                    title_elem = entry.find('atom:title', namespaces)
                    published_elem = entry.find('atom:published', namespaces)
                    if title_elem is not None:
                        print(f"  {i+1}. {title_elem.text[:80]}...")
                    if published_elem is not None:
                        print(f"     Published: {published_elem.text}")
        else:
            print(f"Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n=== Testing our current DateRange implementation ===")
from enhanced_arxiv_api import DateRange

date_range = DateRange("2025-06-01", "2025-06-15")
print(f"Our current format: {date_range.to_query_string()}")
print("Expected format should be: submittedDate:[20250601* TO 20250615*]")
print("Or: submittedDate:[202506010000 TO 202506152359]")