#!/usr/bin/env python3
import sys
sys.path.append('.')

import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

# Test with a much wider date range to see if we can find any papers
print("=== Testing ArXiv API with Wider Date Range ===")
base_url = "http://export.arxiv.org/api/query"

# Test different date ranges
test_cases = [
    {
        'name': 'Last 30 days',
        'query': 'deep learning AND submittedDate:[202505150000+TO+202506152359]'
    },
    {
        'name': 'Last 3 months', 
        'query': 'deep learning AND submittedDate:[202503150000+TO+202506152359]'
    },
    {
        'name': 'All of 2025',
        'query': 'deep learning AND submittedDate:[202501010000+TO+202512312359]'
    },
    {
        'name': 'Without date filter',
        'query': 'deep learning'
    },
    {
        'name': 'Recent papers in cs.AI',
        'query': 'cat:cs.AI AND submittedDate:[202506010000+TO+202506152359]'
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
                first_entry = entries[0]
                title_elem = first_entry.find('atom:title', namespaces)
                published_elem = first_entry.find('atom:published', namespaces)
                if title_elem is not None:
                    print(f"First paper: {title_elem.text[:100]}...")
                if published_elem is not None:
                    print(f"Published: {published_elem.text}")
        else:
            print(f"Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n=== Summary ===")
print("If 'Without date filter' returns results but date-filtered queries don't,")
print("it suggests that there might be no papers in the specified date range,")
print("or there could be an issue with the date format or ArXiv's indexing.")