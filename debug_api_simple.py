#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET

def test_arxiv_api():
    """Test ArXiv API connection and response"""
    
    # Test with paper ID
    print("Testing ArXiv API with paper ID: 1811.04422")
    
    params = {
        'search_query': 'id:1811.04422',
        'start': 0,
        'max_results': 1
    }
    
    try:
        response = requests.get('http://export.arxiv.org/api/query', params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        
        if response.status_code == 200:
            print("\nFirst 500 characters of response:")
            print(response.text[:500])
            
            # Try to parse XML
            try:
                root = ET.fromstring(response.text)
                entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
                print(f"\nFound {len(entries)} entries in XML")
                
                if entries:
                    entry = entries[0]
                    title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
                    if title_elem is not None:
                        print(f"Title: {title_elem.text.strip()}")
                    
                    id_elem = entry.find('.//{http://www.w3.org/2005/Atom}id')
                    if id_elem is not None:
                        print(f"ID: {id_elem.text}")
                        
            except ET.ParseError as e:
                print(f"XML Parse Error: {e}")
                
        else:
            print(f"Request failed with status {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_arxiv_api()