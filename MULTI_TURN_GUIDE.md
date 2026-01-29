# Multi-Turn Scammer Engagement Guide

## How It Works

Your honeypot system maintains **conversation history per session** and gets progressively smarter at extracting intelligence through multi-turn conversations.

### Architecture

```
Request 1: Scammer Message 1
  ↓
Your API stores in session + Agent responds (tactical question)
  ↓
Request 2: Scammer Message 2 + Conversation History
  ↓
Your API updates session + Agent responds (more targeted)
  ↓
Request 3: Scammer Message 3 + Full History
  ↓
Your API extracts UPI/Phone/Links + Final Response
```

## Example: UPI Extraction Through Multi-Turn

### **Turn 1: Scammer initiates**
```bash
curl -X POST http://localhost:8000/inbound \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "sessionId": "scammer-001",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked. Send ₹500 immediately."
    },
    "conversationHistory": []
  }'
```

**Response:**
```json
{
  "status": "success",
  "scamDetected": true,
  "agentReply": "What's the payment for exactly? This seems like a scam.",
  "extractedIntelligence": {
    "upiIds": [],
    "phoneNumbers": [],
    "phishingLinks": [],
    "suspiciousKeywords": ["blocked", "send", "payment"]
  },
  "engagementComplete": false
}
```

---

### **Turn 2: Scammer provides UPI**
```bash
curl -X POST http://localhost:8000/inbound \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "sessionId": "scammer-001",
    "message": {
      "sender": "scammer",
      "text": "Send to helper@upi or call 9876543210"
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your account will be blocked. Send ₹500 immediately."
      },
      {
        "sender": "agent",
        "text": "What's the payment for exactly? This seems like a scam."
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "scamDetected": true,
  "agentReply": "Can you give me your bank's main phone number so I can verify?",
  "extractedIntelligence": {
    "upiIds": ["helper@upi"],
    "phoneNumbers": ["9876543210"],
    "phishingLinks": [],
    "suspiciousKeywords": ["blocked", "send", "payment", "call"]
  },
  "engagementComplete": false
}
```

✅ **UPI and Phone extracted!**

---

### **Turn 3: Scammer provides link**
```bash
curl -X POST http://localhost:8000/inbound \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "sessionId": "scammer-001",
    "message": {
      "sender": "scammer",
      "text": "Verify here: https://secure-bank-verify.bit.ly/sbi-verify"
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your account will be blocked. Send ₹500 immediately."
      },
      {
        "sender": "agent",
        "text": "What's the payment for exactly? This seems like a scam."
      },
      {
        "sender": "scammer",
        "text": "Send to helper@upi or call 9876543210"
      },
      {
        "sender": "agent",
        "text": "Can you give me your bank's main phone number so I can verify?"
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "scamDetected": true,
  "agentReply": "That URL doesn't look like my bank's website. Let me verify first.",
  "extractedIntelligence": {
    "upiIds": ["helper@upi"],
    "phoneNumbers": ["9876543210"],
    "phishingLinks": ["https://secure-bank-verify.bit.ly/sbi-verify"],
    "suspiciousKeywords": ["blocked", "send", "payment", "call", "verify", "link"]
  },
  "engagementComplete": false
}
```

✅ **All intelligence extracted: UPI + Phone + Phishing Link!**

---

## Key Points

### 1. **Session Persistence**
- Each `sessionId` maintains conversation state
- Agent remembers entire conversation history
- Not visible in output (internal tracking)

### 2. **Tactical Agent Behavior**
- **Turn 1**: Asks what payment is for
- **Turn 2**: Asks for verification details (triggers UPI/phone reveal)
- **Turn 3**: Questions link legitimacy (triggers phishing link reveal)
- **Turn 4+**: Continues engagement to extract more

### 3. **Hidden Conversation**
- You send previous messages in `conversationHistory`
- Agent's responses are tactical (not visible externally)
- Only **final extracted intelligence** is shown in output

### 4. **Intelligence Extraction**
- **UPI IDs**: `name@bank` format (helper@upi, user@upi, pay@hdfc)
- **Phone Numbers**: Indian format (9876543210, +919876543210)
- **Phishing Links**: Any URL (http://, https://, bit.ly, etc.)
- **Keywords**: Suspicious words (otp, blocked, verify, etc.)

---

## Real-World Scenario

**Typical Indian scam conversation:**

```
Scammer: "Your SBI account is blocked! Call 9876543210 immediately"
  ↓ [Your agent asks for details]
Scammer: "Send ₹1000 to helper@upi to unblock. Don't delay!"
  ↓ [Your agent questions legitimacy]
Scammer: "Verify on our website: https://sbisecure.bit.ly/verify"
  ↓ [Your agent extracts everything]
Result: UPI + Phone + Link captured
```

---

## Integration with Your Dashboard

When building the dashboard, show:

```
Session: scammer-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Turn 1 [Hidden]: "What's the payment for?"
Turn 2 [Hidden]: "Can you verify your ID?"
Turn 3 [Hidden]: "That link looks fake..."

EXTRACTED INTELLIGENCE:
✅ UPI IDs: helper@upi
✅ Phones: 9876543210
✅ Links: https://sbisecure.bit.ly/verify
✅ Keywords: blocked, payment, verify, urgent
```

---

## API Integration Tips

**For Frontend/Testing:**
1. Make first request with empty `conversationHistory`
2. Store the `agentReply` from response
3. On next message, include ALL previous messages in `conversationHistory`
4. Extract intelligence from the response
5. Repeat until `engagementComplete` is `true`

**Payload Structure:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Current message from scammer",
    "timestamp": "ISO-8601-timestamp (optional)"
  },
  "conversationHistory": [
    {"sender": "scammer", "text": "First message"},
    {"sender": "agent", "text": "Agent response"},
    {"sender": "scammer", "text": "Second message"},
    {"sender": "agent", "text": "Agent response"}
  ],
  "metadata": {
    "channel": "SMS",
    "locale": "IN",
    "language": "English"
  }
}
```

---

## Advanced Features

### Tactical Response Strategy

The agent follows a progression based on message count:

| Turn | Strategy | Goal |
|------|----------|------|
| 1-2 | Show concern | Keep conversation alive |
| 3-4 | Ask for details | Extract payment methods |
| 5-6 | Question legitimacy | Extract verification links |
| 7+ | Express doubt | Prolong engagement |

### Topics Automatically Detected

- ✅ Banking/KYC fraud
- ✅ Delivery/Refund scams
- ✅ Job offers
- ✅ Prize claims
- ✅ Loan approvals
- ✅ Investment pitches
- ✅ Threatening messages
- ✅ Romantic scams

---

## Testing

```bash
# Test complete multi-turn flow
./test_multi_turn.sh

# Or manually:
# 1. Send first message with empty history
# 2. Store response
# 3. Send second message with history from step 1
# 4. Observe intelligence extraction
```

---

**Your honeypot is now a tactical intelligence extraction system!** 🎯
