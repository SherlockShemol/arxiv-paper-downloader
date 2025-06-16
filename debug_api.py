#!/usr/bin/env python3
import sys
sys.path.append('.')

import requests
from urllib.parse import urlencode
from enhanced_arxiv_api import EnhancedArxivAPI, DateRange

# Test direct API call first
print("=== Testing Direct ArXiv API Call ===")
base_url = "http://export.arxiv.org/api/query"
params = {
    'search_query': 'deep learning AND submittedDate:[202506010000+TO+202506152359]',
    'start': 0,
    'max_results': 10,
    'sortBy': 'relevance',
    'sortOrder': 'descending'
}

url = f"{base_url}?{urlencode(params)}"
print(f"Direct URL: {url}")

try:
    response = requests.get(base_url, params=params, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response length: {len(response.text)}")
    
    # Parse XML to count entries
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response.text)
    namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = root.findall('atom:entry', namespaces)
    print(f"Number of entries found: {len(entries)}")
    
    # Print first entry if exists
    if entries:
        first_entry = entries[0]
        title_elem = first_entry.find('atom:title', namespaces)
        published_elem = first_entry.find('atom:published', namespaces)
        if title_elem is not None:
            print(f"First paper title: {title_elem.text}")
        if published_elem is not None:
            print(f"First paper published: {published_elem.text}")
    
    # Save response for inspection
    with open('debug_response.xml', 'w') as f:
        f.write(response.text)
    print("Response saved to debug_response.xml")
    
except Exception as e:
    print(f"Direct API call failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Testing Enhanced API ===")
api = EnhancedArxivAPI()

# Enable debug logging
api.debug = True

date_range = DateRange("2025-06-01", "2025-06-15")
print(f"Date range query string: {date_range.to_query_string()}")

try:
    papers = api.search_papers(
        query="deep learning",
        date_range=date_range,
        max_results=10
    )
    print(f"Enhanced API found {len(papers)} papers")
except Exception as e:
    print(f"Enhanced API failed: {e}")
    import traceback
    traceback.print_exc()

api.close()