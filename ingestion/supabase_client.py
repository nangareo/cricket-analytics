"""
Supabase Data Client for Cricket Analytics Dashboard
Replaces CSV file reads with Supabase REST API calls
File: ingestion/supabase_client.py
"""

import json
import urllib.request
import urllib.error
import pandas as pd
import streamlit as st

SUPABASE_URL = "https://gruiqljiokngvxscjlkj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdydWlxbGppb2tuZ3Z4c2NqbGtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzczNzI0MDEsImV4cCI6MjA5Mjk0ODQwMX0.T8tAfP3mQlBUS4g662I85KpJZk8tWeIUT3CQ5Z_zTr0"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def fetch_table(table, limit=1000):
    """Fetch all rows from a Supabase table, returns DataFrame"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?limit={limit}&order=id.asc"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode("utf-8"))
            return pd.DataFrame(data)
    except urllib.error.HTTPError as e:
        st.error(f"Supabase error fetching {table}: {e.code}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Connection error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # cache for 5 minutes
def load_batting():
    df = fetch_table("batting_scores")
    if df.empty: return df
    # Rename back to match dashboard expectations
    return df.rename(columns={"player": "batter"})

@st.cache_data(ttl=300)
def load_bowling():
    df = fetch_table("bowling_scores")
    if df.empty: return df
    return df.rename(columns={"player": "bowler"})

@st.cache_data(ttl=300)
def load_fielding():
    df = fetch_table("fielding_scores")
    if df.empty: return df
    return df.rename(columns={"player": "fielder"})

@st.cache_data(ttl=300)
def load_allrounder():
    return fetch_table("allrounder_scores")

def check_connection():
    """Test Supabase connection — returns True/False"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/batting_scores?limit=1"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as r:
            return r.status == 200
    except:
        return False
