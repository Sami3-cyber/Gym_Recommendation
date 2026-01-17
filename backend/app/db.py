"""
Supabase Client Initialization
"""
import os
from supabase import create_client, Client
from app.mock_db import MockClient

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    # Check if URL/Key are set and not just placeholders
    if not url or not key or "your-project" in url:
        return MockClient()
        
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return MockClient()

# Create a singleton instance
supabase = get_supabase()
