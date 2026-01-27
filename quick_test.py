#!/usr/bin/env python3
"""
Quick test of the honeypot API
"""
import requests
import json
import time
import subprocess
import sys
import os

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    api_key = "test-key-123"
    
    # Test 1: Health Check
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: First Scam Message
    print("\n" + "="*60)
    print("TEST 2: First Scam Message (Detection)")
    print("="*60)
    payload = {
        "sessionId": "test-session-001",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately at http://malicious-link.example",
            "timestamp": "2026-01-27T10:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        resp = requests.post(
            f"{base_url}/inbound",
            json=payload,
            headers={"x-api-key": api_key},
            timeout=15
        )
        print(f"✅ Status: {resp.status_code}")
        result = resp.json()
        print(f"Scam Detected: {result.get('scamDetected')}")
        print(f"Agent Reply: {result.get('agentReply', 'N/A')[:60]}...")
        if result.get('scamDetected'):
            print("✅ Scam detection working!")
        else:
            print("❌ Should have detected scam")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: API Key Auth
    print("\n" + "="*60)
    print("TEST 3: API Key Authentication")
    print("="*60)
    try:
        resp = requests.post(
            f"{base_url}/inbound",
            json=payload,
            headers={"x-api-key": "wrong-key"},
            timeout=5
        )
        if resp.status_code == 401:
            print("✅ Correctly rejected invalid API key (401)")
        else:
            print(f"❌ Should return 401, got {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    return True

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    success = test_api()
    sys.exit(0 if success else 1)
