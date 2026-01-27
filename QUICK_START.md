# Quick Start & Testing Guide

## 🚀 Run the Server

```bash
# Install dependencies (if not already done)
pip install fastapi uvicorn openai python-dotenv requests pydantic

# Make sure .env file has:
# API_KEY=your-secret-key
# OPENAI_API_KEY=sk-...

# Start the server
python main.py
```

Server will be available at: `http://localhost:8000`

---

## ✅ Test with curl

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

Expected:
```json
{"status": "healthy", "timestamp": "2026-01-27T..."}
```

---

### Test 2: First Scam Message (Detection)

```bash
curl -X POST http://localhost:8000/inbound \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately by sending your UPI ID",
      "timestamp": "2026-01-27T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

Expected: `"scamDetected": true`, agent reply generated

---

### Test 3: Follow-up Message (Intelligence Extraction)

```bash
curl -X POST http://localhost:8000/inbound \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "You can send your UPI to scammer@upi or call +919876543210",
      "timestamp": "2026-01-27T10:01:00Z"
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately by sending your UPI ID",
        "timestamp": "2026-01-27T10:00:00Z"
      },
      {
        "sender": "user",
        "text": "Why will my account be blocked?",
        "timestamp": "2026-01-27T10:00:30Z"
      }
    ],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

Expected: UPI and phone number extracted and visible in response

---

### Test 4: API Key Authentication

```bash
# Without API key - should be rejected
curl -X POST http://localhost:8000/inbound \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "test", "message": {"sender": "scammer", "text": "test"}}'
```

Expected: `401 Unauthorized`

---

## 🧪 Run Integration Tests

```bash
# Make sure server is running first
python test_integration.py
```

This will:
1. Test health check
2. Test API authentication
3. Send first scam message
4. Send follow-up message
5. Validate all response fields

---

## 🔍 Monitor Logs

Watch server logs to see:
- Session creation: `[session-id] Received message...`
- Scam detection: `[session-id] Scam detected: true`
- Agent activation: `[session-id] Activating agent...`
- Intelligence extraction: `[session-id] Extracted intelligence: {...}`
- GUVI callback: `[session-id] Sending GUVI callback...`

---

## 🎯 Key Differences from Old Code

### Old (Non-Compliant)
```python
return {
    "scamDetected": true,
    "totalMessages": 5,
    "agentReply": "...",
    "conversationSoFar": [...]  # ❌ Extra fields
}
```

### New (Compliant)
```python
return {
    "status": "success",
    "scamDetected": true,
    "engagementMetrics": {  # ✅ Correct structure
        "engagementDurationSeconds": 120,
        "totalMessagesExchanged": 5
    },
    "extractedIntelligence": {...},
    "agentNotes": "...",
    "agentReply": "..."  # ✅ For client to respond
}
```

---

## 🔐 Important: GUVI Callback

The system automatically sends the final result to GUVI when:
1. Scam is detected (`scamDetected: true`)
2. Engagement is complete (termination criteria met)
3. Callback hasn't been sent yet (prevent duplicates)

**Check logs for**: `✅ GUVI callback sent successfully`

If callback fails, you'll see: `❌ GUVI callback failed with status...`

---

## 🚨 Troubleshooting

### Server won't start
```
Error: ModuleNotFoundError: No module named 'fastapi'
→ Run: pip install fastapi uvicorn openai python-dotenv requests pydantic
```

### OPENAI_API_KEY error
```
Error: OPENAI_API_KEY not set
→ Add to .env: OPENAI_API_KEY=sk-your-key-here
```

### API key rejected
```
Status: 401 Unauthorized
→ Check x-api-key header matches API_KEY in .env
```

### Agent not responding
```
Agent processing error: ...
→ Check OpenAI API key is valid and has credits
→ Check internet connection
```

### GUVI callback failing
```
❌ GUVI callback failed with status 404
→ Endpoint URL might be wrong (verify in callback.py)
→ Check payload format matches spec
→ Check internet connectivity
```

---

## 📊 Expected Response Structure

Every response from `/inbound` should have this exact structure:

```json
{
  "status": "success",
  "scamDetected": boolean,
  "engagementMetrics": {
    "engagementDurationSeconds": integer,
    "totalMessagesExchanged": integer
  },
  "extractedIntelligence": {
    "bankAccounts": [strings],
    "upiIds": [strings],
    "phishingLinks": [strings],
    "phoneNumbers": [strings],
    "suspiciousKeywords": [strings]
  },
  "agentNotes": "string",
  "agentReply": "string or null",
  "engagementComplete": boolean,
  "callbackSent": boolean
}
```

---

## 🎯 Testing Checklist

Before deployment:
- [ ] Server starts without errors
- [ ] Health check works
- [ ] API key authentication works
- [ ] First message triggers scam detection
- [ ] Agent generates replies
- [ ] Intelligence is extracted
- [ ] Response format matches spec
- [ ] GUVI callback is sent (check logs)
- [ ] Integration tests pass
- [ ] Logs show expected flow

---

## 📝 Sample Scam Messages for Testing

### Bank Account Threat
```
"Your bank account will be blocked today. Verify immediately at https://fake-bank.com/verify"
```

### UPI Fraud
```
"For KYC update, share your UPI ID: payment@upi or call +919876543210"
```

### OTP Scam
```
"Your Amazon account shows suspicious activity. Enter OTP at https://amz-verify.net/otp"
```

### Fake Loan Offer
```
"You're approved for ₹5,00,000 loan! Verify your Aadhar and bank account number to proceed urgently"
```

---

## 🚀 Deployment Checklist

Before deploying to production:
1. [ ] All files have been updated
2. [ ] Environment variables are set
3. [ ] Integration tests pass
4. [ ] GUVI callback is working
5. [ ] Logs show expected behavior
6. [ ] README is complete
7. [ ] No hardcoded secrets
8. [ ] Error handling is in place

Then deploy to:
- Render: `render.com`
- Railway: `railway.app`
- Heroku: `heroku.com`

---

**You're ready to test and deploy!** 🎉
