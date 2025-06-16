#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from collections import Counter
import re

def get_june_papers(max_results=50):
    """Get papers from June 2025 to analyze their content"""
    base_url = "http://export.arxiv.org/api/query"
    
    params = {
        'search_query': 'submittedDate:202506*',
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = f"{base_url}?" + "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
    print(f"Fetching June 2025 papers...")
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
            
            papers = []
            for entry in entries:
                title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
                summary_elem = entry.find('.//{http://www.w3.org/2005/Atom}summary')
                published_elem = entry.find('.//{http://www.w3.org/2005/Atom}published')
                category_elems = entry.findall('.//{http://arxiv.org/schemas/atom}primary_category')
                
                title = title_elem.text.strip() if title_elem is not None else "No title"
                summary = summary_elem.text.strip() if summary_elem is not None else "No summary"
                published = published_elem.text if published_elem is not None else "No date"
                
                # Get primary category
                category = "Unknown"
                if category_elems:
                    category = category_elems[0].get('term', 'Unknown')
                
                papers.append({
                    'title': title,
                    'summary': summary,
                    'published': published,
                    'category': category
                })
            
            return papers
        else:
            print(f"Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_papers(papers):
    """Analyze the content of papers"""
    print(f"\n=== Analysis of {len(papers)} papers ===")
    
    # Analyze categories
    categories = Counter(paper['category'] for paper in papers)
    print("\n--- Categories ---")
    for category, count in categories.most_common():
        print(f"{category}: {count}")
    
    # Analyze keywords in titles and abstracts
    all_text = ""
    for paper in papers:
        all_text += f" {paper['title']} {paper['summary']}"
    
    # Convert to lowercase and find common terms
    all_text = all_text.lower()
    
    # Check for specific terms
    terms_to_check = [
        'deep learning', 'machine learning', 'neural network', 'artificial intelligence',
        'transformer', 'attention', 'classification', 'regression', 'optimization',
        'computer vision', 'natural language', 'reinforcement learning', 'generative',
        'diffusion', 'llm', 'large language model', 'bert', 'gpt'
    ]
    
    print("\n--- Keyword Analysis ---")
    for term in terms_to_check:
        count = all_text.count(term)
        if count > 0:
            print(f"'{term}': {count} occurrences")
    
    # Show first few papers
    print("\n--- Sample Papers ---")
    for i, paper in enumerate(papers[:10], 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Category: {paper['category']}")
        print(f"   Published: {paper['published']}")
        print(f"   Abstract: {paper['summary'][:200]}...")

if __name__ == "__main__":
    papers = get_june_papers(100)  # Get more papers for better analysis
    if papers:
        analyze_papers(papers)
    else:
        print("No papers found or error occurred.")