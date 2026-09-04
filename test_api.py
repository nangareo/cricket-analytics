"""
Test CricketData.org API Key

Run: CRICAPI_KEY=your-key python test_api.py
"""
import json
import sys
import urllib.request

import config

API_KEY = config.get_cricapi_key()
if not API_KEY:
    print("No API key found.")
    print("Set CRICAPI_KEY in the environment, or add it to "
          ".streamlit/secrets.toml (see .streamlit/secrets.toml.example).")
    sys.exit(1)

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
