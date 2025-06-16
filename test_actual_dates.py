#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from datetime import datetime, timedelta

def test_date(date_query, description):
    """Test a specific date query"""
    base_url = "http://export.arxiv.org/api/query"
    
    params = {
        'search_query': date_query,
        'start': 0,
        'max_results': 5,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = f"{base_url}?" + "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
    print(f"\n--- {description} ---")
    print(f"Query: {date_query}")
    
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
                
                for i, entry in enumerate(entries[:3], 1):
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

def get_recent_papers_dates():
    """Get some recent papers to see what dates are actually available"""
    base_url = "http://export.arxiv.org/api/query"
    
    params = {
        'search_query': 'all:*',  # Get any papers
        'start': 0,
        'max_results': 20,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = f"{base_url}?" + "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
    print(f"\n=== Getting recent papers to check available dates ===")
    
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
            
            dates = set()
            for entry in entries:
                published_elem = entry.find('.//{http://www.w3.org/2005/Atom}published')
                if published_elem is not None:
                    date_str = published_elem.text[:10]  # Get YYYY-MM-DD part
                    dates.add(date_str)
            
            print(f"\nUnique dates found: {sorted(dates)}")
            return sorted(dates)
        else:
            print(f"Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("Testing actual available dates in ArXiv...")
    
    # First, get some recent papers to see what dates are available
    recent_dates = get_recent_papers_dates()
    
    if recent_dates:
        # Test with the most recent date found
        most_recent = recent_dates[-1]
        date_formatted = most_recent.replace('-', '')
        
        print(f"\n=== Testing with most recent date: {most_recent} ===")
        test_date(f"submittedDate:{date_formatted}*", f"Most recent date wildcard: {most_recent}")
        test_date(f"submittedDate:{date_formatted}", f"Most recent date exact: {most_recent}")
        
        # Test with month wildcard
        month_formatted = date_formatted[:6]  # YYYYMM
        test_date(f"submittedDate:{month_formatted}*", f"Month wildcard: {most_recent[:7]}")
        
        # Test with year wildcard
        year_formatted = date_formatted[:4]  # YYYY
        test_date(f"submittedDate:{year_formatted}*", f"Year wildcard: {most_recent[:4]}")
    
    # Test some other formats
    print("\n=== Testing various date formats ===")
    test_date("submittedDate:2024*", "Year 2024 wildcard")
    test_date("submittedDate:202412*", "December 2024 wildcard")
    test_date("submittedDate:20241201*", "Dec 1, 2024 wildcard")