#!/usr/bin/env python3
import requests
import json

try:
    response = requests.post(
        'http://localhost:5001/api/search',
        json={'query': 'machine learning', 'max_results': 5},
        timeout=10
    )
    print(f'Status Code: {response.status_code}')
    print(f'Response Headers: {dict(response.headers)}')
    print(f'Response Text: {response.text}')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            papers = data.get('papers', [])
            print(f'Found {len(papers)} papers')
            for i, paper in enumerate(papers[:3]):
                print(f'Paper {i+1}: {paper.get("title", "No title")}')
        else:
            print(f'Search failed: {data.get("error", "Unknown error")}')
    else:
        print(f'HTTP Error: {response.status_code}')
        
except requests.exceptions.ConnectionError:
    print('Connection Error: Backend server is not running')
except requests.exceptions.Timeout:
    print('Timeout Error: Request took too long')
except Exception as e:
    print(f'Error: {e}')