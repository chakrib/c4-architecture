#!/usr/bin/env python3
import requests
import json

# Test the suggestion endpoint
url = "http://localhost:8000/api/diagrams/suggest-improvements"

test_input = """Solution Overview: As part of AWS 2.0 account vending happens at the App Family level. Which means each App Family gets one set of SDLC accounts, with corresponding VPCs, and roles associated. These SDLC accounts are shared by multiple Application which fall into the App Family. Which also means, each application deployed is these accounts could potentially share the data. Data could be in databases, S3 buckets of file systems, Cache etc. At this time, only data sharing is the concern, not the network, or other resources."""

payload = {
    "input_text": test_input,
    "diagram_type": "context"
}

print("Testing suggestion endpoint...")
print(f"Input: {test_input[:100]}...")
print()

try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success! Got suggestions:")
        print()
        for i, suggestion in enumerate(data['suggestions'], 1):
            print(f"Option {i}: {suggestion['title']}")
            print(f"Description: {suggestion['description']}")
            print(f"Improved text: {suggestion['improved_text'][:100]}...")
            print()
    else:
        print(f"❌ Error {response.status_code}:")
        print(response.json())
        
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    print("Make sure the backend is running on port 8000")
