"""
Live Scores Tab — Cricket Analytics Dashboard
File: ingestion/live_scores.py
"""

import json
import urllib.request
import urllib.error

API_KEY = "c83bbc46-e3c7-4a77-8b28-a9e4d7785183"
BASE_URL = "https://api.cricapi.com/v1"

def get_current_matches():
    """Fetch all live/current matches"""
    url = f"{BASE_URL}/currentMatches?apikey={API_KEY}&offset=0"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            if data.get("status") == "success":
                return data.get("data", [])
            return []
    except Exception as e:
        return []

def get_match_info(match_id):
    """Fetch detailed scorecard for a match"""
    url = f"{BASE_URL}/match_info?apikey={API_KEY}&id={match_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            if data.get("status") == "success":
                return data.get("data", {})
            return {}
    except Exception as e:
        return {}

def format_score(score_list):
    """Format score array into readable string"""
    if not score_list:
        return "Yet to bat"
    parts = []
    for s in score_list:
        inning = s.get("inning", "")
        r = s.get("r", 0)
        w = s.get("w", 0)
        o = s.get("o", 0)
        parts.append(f"{r}/{w} ({o} ov)")
    return " | ".join(parts)
