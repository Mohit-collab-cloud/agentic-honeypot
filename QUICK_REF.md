# QUICK REFERENCE CARD

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install fastapi uvicorn openai python-dotenv requests pydantic

# 2. Create .env file
echo "API_KEY=your-secret-key" > .env
echo "OPENAI_API_KEY=sk-..." >> .env

# 3. Start server
python main.py

# 4. Test in another terminal
curl -X POST http://localhost:8000/inbound \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test","message":{"sender":"scammer","text":"Verify now"},"conversationHistory":[],"metadata":{"channel":"SMS","locale":"IN"}}'
```

---

## 📁 File Structure

```
agentic-honeypot/
├── main.py                          ← FastAPI server
├── agent.py                         ← LLM agent
├── detector.py                      ← Scam detection
├── session_store.py                 ← Session mgmt
├── intel_store.py                   ← Intelligence extraction
├── callback.py                      ← GUVI integration ⭐ CRITICAL
├── test_integration.py              ← Tests
├── .env                             ← Config (create this)
└── Documentation
    ├── README.md                    ← Overview
    ├── QUICK_START.md               ← Setup guide
    ├── ARCHITECTURE.md              ← Diagrams
    ├── IMPLEMENTATION_SUMMARY.md    ← What was fixed
    ├── FIXES_DETAILED.md            ← Before/after analysis
    ├── CHECKLIST.md                 ← Pre-deployment
    └── COMPLETION_SUMMARY.md        ← Final status
```

---

## 🔑 What Changed (Before vs After)

| Aspect | BEFORE ❌ | AFTER ✅ |
|--------|----------|---------|
| GUVI Callback | Missing | Implemented |
| Response Format | Wrong | Spec-compliant |
| engagementDurationSeconds | Missing | Calculated |
| Agent Approach | JSON in reply | Natural replies |
| Termination Logic | None | Implemented |
| Intelligence Validation | None | Full validation |
| Session Duration | Not tracked | Start/end times |
| Callback Dedup | None | Flag-based |

---

## 📊 API Response Format

```json
{
  "status": "success",
  "scamDetected": true,
  "engagementMetrics": {
    "engagementDurationSeconds": 120,
    "totalMessagesExchanged": 5
  },
  "extractedIntelligence": {
    "bankAccounts": ["123456789"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://..."],
    "phoneNumbers": ["+91..."],
    "suspiciousKeywords": ["urgent", "verify"]
  },
  "agentNotes": "Scammer description",
  "agentReply": "Agent's reply",
  "engagementComplete": false,
  "callbackSent": false
}
```

---

## 🎯 Key Functions

### main.py
```python
@app.post("/inbound")
async def receive_message(payload, x_api_key)
    # Main endpoint - handles full flow
```

### agent.py
```python
generate_agent_reply(session, channel, locale)
extract_intelligence(session, message_text)
should_continue_engagement(session, max_turns=20)
```

### callback.py
```python
send_final_result_to_guvi(session_summary)
    # Sends to https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

### session_store.py
```python
get_session(session_id)
mark_session_complete(session_id)
get_engagement_duration(session_id)
mark_callback_sent(session_id)
get_session_summary(session_id)
```

### intel_store.py
```python
update_extracted_intelligence(session, agent_extract, message_text)
validate_upi(upi)
validate_phone(phone)
validate_url(url)
validate_account(account)
```

---

## 🔍 Testing Checklist

```bash
# Health check
curl http://localhost:8000/health

# Test 1: Auth failure (should be 401)
curl -X POST http://localhost:8000/inbound \
  -d '{"sessionId":"test","message":{"sender":"scammer","text":"test"}}'

# Test 2: First message (should detect scam)
curl -X POST http://localhost:8000/inbound \
  -H "x-api-key: your-key" \
  -H "Content-Type: application/json" \
  -d '{...}'  # See QUICK_START.md for full example

# Test 3: Follow-up (should extract intelligence)
curl -X POST http://localhost:8000/inbound \
  -H "x-api-key: your-key" \
  -H "Content-Type: application/json" \
  -d '{...}'  # With conversationHistory

# Test 4: Run full suite
python test_integration.py
```

---

## 🚨 Critical Checklist

- [ ] GUVI callback implemented in callback.py
- [ ] Response format matches spec (engagementMetrics with exact fields)
- [ ] engagementDurationSeconds is calculated
- [ ] totalMessagesExchanged is counted
- [ ] Session tracking has startTime/endTime
- [ ] Callback is sent when engagement_complete = True
- [ ] Callback is sent only ONCE per session (callbackSent flag)
- [ ] API key authentication works (returns 401 if invalid)
- [ ] Agent replies are natural (not JSON)
- [ ] Intelligence is validated before storing
- [ ] All errors are logged with context
- [ ] Server starts without errors
- [ ] Integration tests pass

---

## 🔄 Engagement Lifecycle

```
Message 1: Scam detected → Activate agent → Reply generated
Message 2: Intelligence extracted → Continue
Message 3: More intel extracted → Continue
...
Message N: Check termination → If YES:
           ├─ Mark complete
           ├─ Calculate duration
           ├─ Build summary
           ├─ Send GUVI callback
           └─ Return response
```

---

## 🔧 Configuration

### .env File
```
API_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

### Code Constants
```python
# agent.py
MAX_CONTEXT = 8 messages  # For cost control
REPLY_TEMP = 0.6          # For natural replies
EXTRACT_TEMP = 0.1        # For consistent extraction

# session_store.py
MAX_TURNS = 20            # Default engagement limit
MIN_MESSAGES = 6          # For termination

# main.py
HOST = "0.0.0.0"
PORT = 8000
```

---

## 📋 Deployment Steps

1. **Verify Locally**
   ```bash
   python main.py
   python test_integration.py
   ```

2. **Choose Platform**
   - Render (recommended)
   - Railway
   - Heroku

3. **Deploy**
   - Push to GitHub
   - Connect platform to repo
   - Set env vars (API_KEY, OPENAI_API_KEY)
   - Deploy

4. **Verify Prod**
   - Test /health
   - Send test message
   - Check logs for GUVI callback

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Run: `pip install fastapi uvicorn openai python-dotenv requests` |
| `OPENAI_API_KEY not set` | Add to .env: `OPENAI_API_KEY=sk-...` |
| `401 Unauthorized` | Check x-api-key header matches API_KEY in .env |
| Agent not responding | Check OpenAI API key is valid and has credits |
| GUVI callback failing | Check URL is correct, internet connection, payload format |
| Session not persisting | This is expected with in-memory storage (use Redis for prod) |

---

## 📊 Example Flow

```
User sends: "Your account blocked. Verify: http://fake.com"

1. Authentication: ✅ x-api-key valid
2. Scam Detection: ✅ Score=4 (keywords+URL), detected=true
3. Session Created: ✅ sessionId="abc123"
4. Agent Activated: ✅ Start conversation
5. Agent Replies: "Why is my account blocked?"
6. Extract Intel: ✅ Found URL: http://fake.com
7. Update State: ✅ Store in session
8. Continue? Yes (only 1 message, need more)
9. Return Response: ✅ With metrics and intel

User replies: "Send your UPI ID: scammer@bank"

10. Continue Agent: ✅ Still engaged
11. Extract Intel: ✅ Found UPI: scammer@bank
12. Update State: ✅ Store in session
13. Agent Replies: "That doesn't seem right..."
14. Continue? Check criteria...
    - Messages: 3 (< 20) ✓
    - Has data: YES ✓
    - >= 6 messages: NO ✗
    - Result: Continue

[Continue for a few more turns...]

Message 6: Termination criteria met!
15. Mark Complete: ✅ endTime = now
16. Calculate Duration: ✅ 120 seconds
17. Build Summary: ✅ All extracted data
18. Send GUVI: ✅ POST callback
19. Mark Sent: ✅ callbackSent = true
20. Return Response: ✅ engagementComplete=true
```

---

## 🎯 Success Metrics

```
For Evaluation:
✅ Scam Detection Accuracy: >80%
✅ Agent Engagement Quality: Natural, non-revealing
✅ Intelligence Extraction: All required fields
✅ API Response Time: <1 second
✅ Callback Submission: Every session
✅ Error Handling: Graceful degradation
✅ Spec Compliance: 100%
```

---

## 📚 Documentation Map

- **Setup?** → QUICK_START.md
- **How it works?** → ARCHITECTURE.md
- **What's wrong?** → FIXES_DETAILED.md
- **Before/After?** → IMPLEMENTATION_SUMMARY.md
- **Deploy ready?** → CHECKLIST.md
- **Final status?** → COMPLETION_SUMMARY.md

---

## ⭐ Most Important Files

1. **callback.py** ← MANDATORY (GUVI integration)
2. **main.py** ← Entry point (correct flow)
3. **agent.py** ← LLM logic (natural replies)
4. **session_store.py** ← Duration tracking

---

**Remember**: 
- Check logs for: `✅ GUVI callback sent successfully`
- This confirms the mandatory requirement works
- Without it, you cannot be evaluated

🚀 **Ready to deploy!**
