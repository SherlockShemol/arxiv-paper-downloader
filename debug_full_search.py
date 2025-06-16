#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from arxiv_downloader import ArxivDownloader
import requests
import xml.etree.ElementTree as ET

def test_direct_api():
    """Test direct API call"""
    print("=== Testing Direct API Call ===")
    
    params = {
        'search_query': 'id:1811.04422',
        'start': 0,
        'max_results': 1
    }
    
    response = requests.get('http://export.arxiv.org/api/query', params=params, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        print(f"Found {len(entries)} entries")
        return len(entries) > 0
    return False

def test_arxiv_downloader():
    """Test ArxivDownloader class"""
    print("\n=== Testing ArxivDownloader Class ===")
    
    try:
        downloader = ArxivDownloader()
        print(f"Base URL: {downloader.base_url}")
        
        # Test search by ID
        print("\nTesting search by ID...")
        papers = downloader.search_papers(query="id:1811.04422", max_results=1)
        print(f"Found {len(papers)} papers")
        
        if papers:
            paper = papers[0]
            print(f"Paper title: {paper.title}")
            print(f"Paper ID: {paper.id}")
            print(f"PDF URL: {paper.pdf_url}")
        
        return len(papers) > 0
        
    except Exception as e:
        print(f"Error in ArxivDownloader: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_build_search_query():
    """Test search query building"""
    print("\n=== Testing Search Query Building ===")
    
    try:
        downloader = ArxivDownloader()
        
        # Test simple query
        query1 = downloader._build_search_query("id:1811.04422")
        print(f"Query 1: {query1}")
        
        # Test with date range
        query2 = downloader._build_search_query("adversarial machine learning", "2018-01-01", "2018-12-31")
        print(f"Query 2: {query2}")
        
        return True
        
    except Exception as e:
        print(f"Error building query: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_request_with_retry():
    """Test request with retry mechanism"""
    print("\n=== Testing Request with Retry ===")
    
    try:
        downloader = ArxivDownloader()
        
        params = {
            'search_query': 'id:1811.04422',
            'start': 0,
            'max_results': 1,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        print(f"Making request to: {downloader.base_url}")
        print(f"With params: {params}")
        
        response = downloader._make_request_with_retry(downloader.base_url, params)
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error in request: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Starting comprehensive ArXiv downloader tests...\n")
    
    tests = [
        ("Direct API", test_direct_api),
        ("Search Query Building", test_build_search_query),
        ("Request with Retry", test_request_with_retry),
        ("ArxivDownloader", test_arxiv_downloader),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\n{test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n{test_name}: FAIL - {e}")
        
        print("-" * 50)
    
    print("\n=== Test Summary ===")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()