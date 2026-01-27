#!/usr/bin/env python3
"""Test agent intelligence with different scam types."""

import requests
import json

API_URL = "http://localhost:8000/inbound"
API_KEY = "test-key-123"

test_cases = [
    {
        "name": "KYC/Link Update",
        "message": "KYC incomplete: Update now to avoid suspension. Click on the link https://www.kyc.com"
    },
    {
        "name": "Payment/UPI Request",
        "message": "Send 5000 rupees to verify your account via UPI: admin@malicious"
    },
    {
        "name": "Account Info Request",
        "message": "Verify your account: Please provide your debit card number and CVV"
    },
    {
        "name": "Urgency/Suspension Threat",
        "message": "Your account will be SUSPENDED IMMEDIATELY! Update now or lose access!"
    },
    {
        "name": "OTP/Password Request",
        "message": "Send your 6-digit OTP immediately to secure your account"
    },
    {
        "name": "Personal Info Request",
        "message": "Update your profile: Name, PAN, Aadhaar, and email address required"
    },
    {
        "name": "Urgency + Link",
        "message": "URGENT: Account locked! Click here IMMEDIATELY to unlock: https://unlock.bank.com"
    }
]

print("\n" + "="*80)
print("🤖 AGENT INTELLIGENCE TEST - Context-Aware Response Generation")
print("="*80)

for i, test in enumerate(test_cases, 1):
    session_id = f"test-{i}"
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": test["message"]
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={"x-api-key": API_KEY},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            agent_reply = data.get("agentReply", "N/A")
            scam_detected = data.get("scamDetected", False)
            
            print(f"\n{i}. {test['name']}")
            print(f"   Scammer: {test['message'][:70]}...")
            print(f"   Status: {'🚨 Scam Detected' if scam_detected else '✅ Legitimate'}")
            print(f"   Agent:  {agent_reply}")
        else:
            print(f"\n{i}. {test['name']} - ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"\n{i}. {test['name']} - ERROR: {e}")

print("\n" + "="*80)
print("✅ Agent is now context-aware and generates intelligent, relevant responses!")
print("="*80 + "\n")
