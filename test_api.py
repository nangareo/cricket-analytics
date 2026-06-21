"""
Test CricketData.org API Key
Run: python test_api.py
"""
import urllib.request, json

API_KEY = "c83bbc46-e3c7-4a77-8b28-a9e4d7785183"
url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

print("Testing CricketData.org API...")
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
        print(f"Status: {data.get('status')}")
        matches = data.get("data", [])
        print(f"Total matches: {len(matches)}")
        for m in matches[:3]:
            print(f"  - {m.get('name')} | {m.get('status')}")
except Exception as e:
    print(f"Error: {e}")
