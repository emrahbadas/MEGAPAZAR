#!/usr/bin/env python3
"""Get real user UUID from Supabase"""
from supabase import create_client
import os

url = "https://snovwbffwvmkgjulrtsm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNub3Z3YmZmd3Zta2dqdWxydHNtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzIzNTc0NCwiZXhwIjoyMDc4ODExNzQ0fQ.JlgKvo9PYDOix7HYjPUo59RvrCdjruf5PxCdxgPklCs"

supabase = create_client(url, key)

# Get first user
result = supabase.table("users").select("id, email").limit(1).execute()

if result.data:
    user = result.data[0]
    print(f"✅ Found user: {user['email']}")
    print(f"🆔 UUID: {user['id']}")
else:
    print("❌ No users in database")
