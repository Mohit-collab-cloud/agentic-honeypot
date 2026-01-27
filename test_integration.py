#!/usr/bin/env python3
"""
Integration test script to verify the complete honeypot flow.
Simulates conversations and validates the response structure.
"""

import requests
import json
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key"  # Change to your actual API_KEY
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def test_health_check():
    """Test the health check endpoint."""
    print("\n🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_first_message():
    """Test the first message (scam detection)."""
    print("\n🔍 Testing first scam message...")
    
    payload = {
        "sessionId": "test-session-001",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately by clicking this link http://malicious-link.example",
            "timestamp": datetime.utcnow().isoformat()
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/inbound", json=payload, headers=HEADERS)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ First message response:")
        print(json.dumps(result, indent=2))
        
        # Validate response structure
        assert "status" in result
        assert result["status"] == "success"
        assert "scamDetected" in result
        assert "engagementMetrics" in result
        assert "extractedIntelligence" in result
        assert "agentNotes" in result
        
        return True, result
    except Exception as e:
        print(f"❌ First message failed: {e}")
        return False, None

def test_follow_up_message(session_id, agent_reply):
    """Test a follow-up message."""
    print("\n🔍 Testing follow-up scam message...")
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid account suspension. My UPI is scammer@upi",
            "timestamp": datetime.utcnow().isoformat()
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately by clicking this link http://malicious-link.example",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "sender": "user",
                "text": agent_reply,
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/inbound", json=payload, headers=HEADERS)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Follow-up message response:")
        print(json.dumps(result, indent=2))
        
        # Check if UPI was extracted
        if result.get("extractedIntelligence", {}).get("upiIds"):
            print(f"✅ UPI extracted: {result['extractedIntelligence']['upiIds']}")
        
        return True, result
    except Exception as e:
        print(f"❌ Follow-up message failed: {e}")
        return False, None

def test_authentication():
    """Test API key authentication."""
    print("\n🔍 Testing authentication...")
    
    payload = {
        "sessionId": "test-auth",
        "message": {
            "sender": "scammer",
            "text": "Test message",
            "timestamp": datetime.utcnow().isoformat()
        },
        "conversationHistory": [],
        "metadata": {}
    }
    
    # Test without API key
    try:
        response = requests.post(f"{API_BASE_URL}/inbound", json=payload)
        if response.status_code == 401:
            print("✅ Correctly rejected request without API key")
            return True
        else:
            print(f"❌ Should have rejected request without API key, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("AGENTIC HONEYPOT - INTEGRATION TESTS")
    print("=" * 60)
    
    # Test health
    if not test_health_check():
        print("\n❌ Server not running. Start it with: python main.py")
        return
    
    # Test authentication
    if not test_authentication():
        print("\n⚠️ Authentication test failed")
    
    # Test first message
    success1, result1 = test_first_message()
    if not success1:
        return
    
    session_id = result1.get("sessionId", "test-session-001") if result1 else "test-session-001"
    agent_reply = result1.get("agentReply", "Why would my account be blocked?") if result1 else "Why would my account be blocked?"
    
    # Give LLM a moment
    print("\n⏳ Waiting 2 seconds before follow-up message...")
    time.sleep(2)
    
    # Test follow-up message
    success2, result2 = test_follow_up_message(session_id, agent_reply)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")

if __name__ == "__main__":
    main()
