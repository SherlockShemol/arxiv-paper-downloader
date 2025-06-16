#!/usr/bin/env python3

import requests
import json

def test_enhanced_search():
    """Test enhanced search API endpoint"""
    url = "http://localhost:5002/api/search/enhanced"
    
    data = {
        "query": "machine learning",
        "max_results": 5
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Testing API endpoint: {url}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response JSON: {json.dumps(result, indent=2)}")
            print(f"Success! Found {len(result.get('papers', []))} papers")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_enhanced_search()