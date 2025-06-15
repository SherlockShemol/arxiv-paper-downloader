#!/usr/bin/env python3
"""
Test script for the web API to verify the search functionality
"""

import requests
import json

def test_web_api():
    """Test the web API search functionality with enhanced API"""
    base_url = "http://localhost:5002"
    
    print("=== Testing Machine Learning Query via Web API ===")
    try:
        response1 = requests.post(
            f"{base_url}/api/papers/search",
            json={
                "query": "machine learning",
                "max_results": 3
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response1.status_code}")
        if response1.status_code == 200:
            data1 = response1.json()
            papers1 = data1.get('papers', [])
            print(f"Found {len(papers1)} papers for 'machine learning'")
            for i, paper in enumerate(papers1, 1):
                print(f"  {i}. {paper.get('title', 'No title')}")
        else:
            print(f"Error: {response1.text}")
            return
            
    except Exception as e:
        print(f"Error with machine learning query: {e}")
        return
    
    print("\n=== Testing Quantum Learning Query via Web API ===")
    try:
        response2 = requests.post(
            f"{base_url}/api/papers/search",
            json={
                "query": "quantum learning",
                "max_results": 3
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response2.status_code}")
        if response2.status_code == 200:
            data2 = response2.json()
            papers2 = data2.get('papers', [])
            print(f"Found {len(papers2)} papers for 'quantum learning'")
            for i, paper in enumerate(papers2, 1):
                print(f"  {i}. {paper.get('title', 'No title')}")
        else:
            print(f"Error: {response2.text}")
            return
            
    except Exception as e:
        print(f"Error with quantum learning query: {e}")
        return
    
    print("\n=== Comparing Web API Results ===")
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        papers1 = data1.get('papers', [])
        papers2 = data2.get('papers', [])
        
        if papers1 and papers2:
            titles1 = [p.get('title', '') for p in papers1]
            titles2 = [p.get('title', '') for p in papers2]
            
            identical = set(titles1) & set(titles2)
            print(f"Identical papers: {len(identical)}")
            
            if identical:
                print("Identical titles:")
                for title in identical:
                    print(f"  - {title}")
            else:
                print("✅ No identical papers - Web API is working correctly!")
        else:
            print("One or both queries returned no results")

if __name__ == "__main__":
    test_web_api()