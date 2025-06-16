#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET

# Test ArXiv API query with date range
url = "http://export.arxiv.org/api/query"
params = {
    "search_query": "deep learning AND submittedDate:[202506010000 TO 202506152359]",
    "start": 0,
    "max_results": 10,
    "sortBy": "relevance",
    "sortOrder": "descending"
}

print(f"Testing ArXiv API query...")
print(f"URL: {url}")
print(f"Params: {params}")

try:
    response = requests.get(url, params=params)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response URL: {response.url}")
    
    if response.status_code == 200:
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Count entries
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        print(f"\nNumber of entries found: {len(entries)}")
        
        # Print first few entries if any
        for i, entry in enumerate(entries[:3]):
            title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
            published_elem = entry.find('.//{http://www.w3.org/2005/Atom}published')
            
            title = title_elem.text if title_elem is not None else "No title"
            published = published_elem.text if published_elem is not None else "No date"
            
            print(f"\nEntry {i+1}:")
            print(f"  Title: {title}")
            print(f"  Published: {published}")
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Exception occurred: {e}")