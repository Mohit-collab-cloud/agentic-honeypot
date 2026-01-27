#!/usr/bin/env python3
import requests
import json
import time

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'test-key-123'
}
base = 'http://localhost:8000/inbound'

def test_scam(title, message, session_id, history=None):
    """Test a scam message"""
    payload = {
        'sessionId': session_id,
        'message': {'sender': 'scammer', 'text': message}
    }
    if history:
        payload['conversationHistory'] = history
    
    try:
        resp = requests.post(base, headers=headers, json=payload).json()
        print(f"✅ {title}")
        print(f"   Message: {message}")
        print(f"   Detected: {resp['scamDetected']}")
        print(f"   Agent: {resp['agentReply']}")
        print()
        return resp
    except Exception as e:
        print(f"❌ {title}: {e}")
        return None

print("=" * 70)
print("COMPREHENSIVE SCAM DETECTION TESTS")
print("=" * 70)
print()

# Banking/KYC
test_scam(
    "Banking: Account Blocked",
    "Your bank account will be blocked today. Verify immediately at this link.",
    "test-banking-1"
)

test_scam(
    "Banking: KYC Verification",
    "KYC incomplete: Update now to avoid suspension. Click here.",
    "test-banking-2"
)

test_scam(
    "Banking: OTP Request",
    "We have detected unusual activity on your account. Please share your OTP to verify.",
    "test-banking-3"
)

test_scam(
    "Banking: Card Disabled",
    "SBI ALERT: Your card has been disabled. Send PAN and Aadhaar to 98888XXXXX.",
    "test-banking-4"
)

# Delivery/Refund
test_scam(
    "Delivery: Package Customs",
    "Your package is held at customs. Pay ₹50 using UPI to release it.",
    "test-delivery-1"
)

test_scam(
    "Refund: Amazon Refund",
    "Amazon refund initiated. Please verify UPI to receive funds.",
    "test-refund-1"
)

# Job/Prize/Loan
test_scam(
    "Prize: KBC Contest",
    "Congratulations! You've won ₹5,00,000 in the Kaun Banega Crorepati contest!",
    "test-prize-1"
)

test_scam(
    "Job: Work From Home",
    "Part-time job offer: earn ₹50,000/week. No skills needed. DM now.",
    "test-job-1"
)

test_scam(
    "Loan: Instant Credit",
    "Loan approved for ₹2,00,000. Pay ₹499 processing fee to get instant credit.",
    "test-loan-1"
)

# Investment/Crypto
test_scam(
    "Investment: Double Money",
    "Double your money in 48 hours! Send ₹500 to trader@upi to join now.",
    "test-invest-1"
)

test_scam(
    "Crypto: Govt Scheme",
    "Govt crypto scheme offering 30% monthly return. Limited slots!",
    "test-crypto-1"
)

# Romance/Social Engineering
test_scam(
    "Romance: Friend Request",
    "Hi, I'm Priya. Want to be friends? Let's talk on WhatsApp 😊",
    "test-romance-1"
)

test_scam(
    "SE: Money Transfer",
    "I'm stuck abroad and need urgent help. Can you send ₹2000 to my UPI?",
    "test-se-1"
)

# Threatening/Urgent
test_scam(
    "Threat: SIM Deactivation",
    "Your SIM will be deactivated in 24 hrs. Urgent KYC needed.",
    "test-threat-1"
)

test_scam(
    "Threat: Tax Raid",
    "Income Tax raid scheduled. Clear dues by paying ₹1500 via UPI immediately.",
    "test-threat-2"
)

test_scam(
    "Threat: Cyber Cell",
    "Cyber Cell complaint filed against your number. Resolve it here: [link]",
    "test-threat-3"
)

print("=" * 70)
print("MULTI-TURN CONVERSATION TEST")
print("=" * 70)
print()

# Message 1
resp1 = test_scam(
    "Turn 1: KYC Verification Request",
    "Your KYC is incomplete. Verify your identity now.",
    "test-multiturn-1"
)

if resp1:
    time.sleep(0.5)
    # Message 2 - Payment request
    resp2 = test_scam(
        "Turn 2: Now asking for Payment (Agent should remember KYC context)",
        "Now you need to send ₹500 to complete the process.",
        "test-multiturn-1",
        history=[
            {"sender": "scammer", "text": "Your KYC is incomplete. Verify your identity now."},
            {"sender": "agent", "text": resp1['agentReply']}
        ]
    )
    
    if resp2:
        time.sleep(0.5)
        # Message 3 - Urgency
        resp3 = test_scam(
            "Turn 3: Now adding Urgency (Agent should remember KYC + PAYMENT + URGENCY)",
            "Do this immediately or your account will be blocked!",
            "test-multiturn-1",
            history=[
                {"sender": "scammer", "text": "Your KYC is incomplete. Verify your identity now."},
                {"sender": "agent", "text": resp1['agentReply']},
                {"sender": "scammer", "text": "Now you need to send ₹500 to complete the process."},
                {"sender": "agent", "text": resp2['agentReply']}
            ]
        )

print("=" * 70)
print("✅ ALL TESTS COMPLETED")
print("=" * 70)
