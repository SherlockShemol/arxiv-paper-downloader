#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

def debug_parse_entry(entry, namespaces: Dict[str, str]):
    """Debug version of _parse_entry method"""
    print("\n=== Parsing Entry ===")
    
    try:
        # Extract basic information
        title = entry.find('atom:title', namespaces)
        title_text = title.text.strip().replace('\n', ' ') if title is not None else "Unknown Title"
        print(f"Title: {title_text}")
        
        summary = entry.find('atom:summary', namespaces)
        summary_text = summary.text.strip().replace('\n', ' ') if summary is not None else ""
        print(f"Summary length: {len(summary_text)}")
        
        # Extract ArXiv ID from URL
        id_elem = entry.find('atom:id', namespaces)
        if id_elem is None:
            print("ERROR: No ID element found")
            return None
        
        arxiv_id = id_elem.text.split('/')[-1]
        print(f"ArXiv ID: {arxiv_id}")
        
        # Extract authors
        authors = []
        author_elements = entry.findall('atom:author', namespaces)
        print(f"Found {len(author_elements)} authors")
        for author_elem in author_elements:
            name_elem = author_elem.find('atom:name', namespaces)
            if name_elem is not None:
                authors.append(name_elem.text.strip())
        print(f"Authors: {authors}")
        
        # Extract categories
        categories = []
        category_elements = entry.findall('atom:category', namespaces)
        print(f"Found {len(category_elements)} categories")
        for cat_elem in category_elements:
            term = cat_elem.get('term')
            if term:
                categories.append(term)
        print(f"Categories: {categories}")
        
        # Extract publication date
        published = entry.find('atom:published', namespaces)
        published_text = published.text if published is not None else ""
        print(f"Published: {published_text}")
        
        # Extract PDF URL
        pdf_url = ""
        link_elements = entry.findall('atom:link', namespaces)
        print(f"Found {len(link_elements)} links")
        for link in link_elements:
            link_type = link.get('type')
            href = link.get('href')
            print(f"  Link: type={link_type}, href={href}")
            if link.get('type') == 'application/pdf':
                pdf_url = link.get('href', '')
                break
        
        print(f"PDF URL: {pdf_url}")
        
        # Create paper data
        paper_data = {
            'id': arxiv_id,
            'title': title_text,
            'authors': authors,
            'abstract': summary_text,
            'categories': categories,
            'published': published_text,
            'pdf_url': pdf_url
        }
        
        print(f"Paper data created successfully: {paper_data['title']}")
        return paper_data
        
    except Exception as e:
        print(f"ERROR parsing entry: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_parsing():
    """Test parsing with actual ArXiv response"""
    
    print("Testing ArXiv parsing with paper ID: 1811.04422")
    
    params = {
        'search_query': 'id:1811.04422',
        'start': 0,
        'max_results': 1
    }
    
    try:
        response = requests.get('http://export.arxiv.org/api/query', params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Parse XML
            root = ET.fromstring(response.text)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entries = root.findall('atom:entry', namespaces)
            print(f"Found {len(entries)} entries")
            
            for i, entry in enumerate(entries):
                print(f"\n--- Entry {i+1} ---")
                paper_data = debug_parse_entry(entry, namespaces)
                if paper_data:
                    print("SUCCESS: Paper parsed successfully")
                else:
                    print("FAILED: Could not parse paper")
                    
        else:
            print(f"Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parsing()