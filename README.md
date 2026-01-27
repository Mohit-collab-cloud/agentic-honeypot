# Agentic Honeypot for Scam Detection & Intelligence Extraction

A complete AI-powered honeypot system that detects scam messages and autonomously engages scammers to extract actionable intelligence.

## Architecture Overview

### System Components

1. **Detector** (`detector.py`) - Rule-based scam intent detection
2. **Agent** (`agent.py`) - LLM-powered conversation and extraction
3. **Session Store** (`session_store.py`) - Multi-turn conversation state management
4. **Intel Store** (`intel_store.py`) - Intelligence extraction and validation
5. **Callback** (`callback.py`) - GUVI endpoint integration
6. **Main API** (`main.py`) - FastAPI REST endpoint

### Processing Flow

```
Incoming Message
       ↓
Authentication (x-api-key)
       ↓
Scam Detection
       ↓
Session Management
       ├─→ First detection: Activate Agent
       └─→ Subsequent messages: Continue Agent
       ↓
Agent Engagement
├─→ Generate Natural Reply
├─→ Extract Intelligence
└─→ Update Session State
       ↓
Check Termination Criteria
├─→ Max messages reached?
├─→ Key intel extracted?
└─→ Pattern matched?
       ↓
If Complete: Send GUVI Callback
       ↓
Return Response to Client
```

## Key Improvements Over Initial Version

### 1. **Separated Concerns**
- **agent.py**: Conversation generation (natural replies) + Intelligence extraction
  - `generate_agent_reply()` - Creates believable responses without JSON
  - `extract_intelligence()` - Combined LLM + regex extraction
  - `should_continue_engagement()` - Termination logic

- **intel_store.py**: Validation and enrichment
  - Validates UPI IDs, phone numbers, URLs, account numbers
  - Prevents hallucinated intelligence from being stored

- **callback.py**: GUVI integration
  - Handles final result submission
  - Prevents duplicate callbacks
  - Proper error handling

### 2. **Mandatory GUVI Callback Implementation**
```
When engagement ends:
1. Build session summary
2. Send to: https://hackathon.guvi.in/api/updateHoneyPotFinalResult
3. Mark callback as sent (prevent duplicates)
4. Log success/failure
```

### 3. **Correct Response Format**
Per specification, API returns:
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
    "phishingLinks": ["http://malicious.com"],
    "phoneNumbers": ["+91XXXXXXXXXX"],
    "suspiciousKeywords": ["urgent", "verify", "blocked"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

### 4. **Engagement Termination Logic**
Conversation ends when ANY condition is met:
- Total messages ≥ 20 (configurable)
- Extracted high-value intel (UPI or account) + ≥ 6 messages
- Scammer's response indicates unwillingness to continue

### 5. **Intelligence Extraction Strategy**
```
For each incoming message:
1. LLM extraction (find candidate data)
2. Regex validation (ensure correct format)
3. Duplicate prevention (merge_unique)
4. Store in session

Patterns validated:
- UPI: name@bank format
- Phone: +91 or 0 prefix, 10 digits, starting with 6-9
- URL: http/https protocol
- Account: 9-18 digits (excluding phone-like patterns)
```

### 6. **Adaptive Agent Persona**
```python
Based on:
- Channel (SMS, WhatsApp, Email, Chat)
- Locale (IN, US, etc.)
- Language (English, Hindi, etc.)

Default: "Suman" - 35-year-old Indian office manager
Behavior: Curious, skeptical, but not accusatory
```

### 7. **Cost & Latency Optimization**
- Limited context to last 8 messages
- Temperature: 0.6 for replies, 0.1 for extraction
- Max tokens: 100 for replies, 200 for extraction
- Separate LLM calls for conversation and extraction

### 8. **Comprehensive Logging**
Every request is logged with:
- Session ID
- Message preview
- Scam detection result
- Extracted intelligence
- Agent engagement status
- GUVI callback status

## Setup & Configuration

### Environment Variables (.env)
```
API_KEY=your-secret-api-key
OPENAI_API_KEY=sk-...
```

### Installation
```bash
pip install fastapi uvicorn openai python-dotenv requests pydantic
```

### Running the Server
```bash
python main.py
# Server starts at http://0.0.0.0:8000
```

### Health Check
```bash
curl http://localhost:8000/health
```

## API Usage

### Request Format
```bash
curl -X POST http://localhost:8000/inbound \
  -H "x-api-key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session-123",
    "message": {
      "sender": "scammer",
      "text": "Your account is blocked. Verify now.",
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

### Response Example
```json
{
  "status": "success",
  "scamDetected": true,
  "engagementMetrics": {
    "engagementDurationSeconds": 45,
    "totalMessagesExchanged": 3
  },
  "extractedIntelligence": {
    "upiIds": ["scammer@upi"],
    "bankAccounts": [],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["verify", "account", "blocked"]
  },
  "agentNotes": "Scammer requested verification link",
  "agentReply": "Why would my account be blocked? What should I do?",
  "engagementComplete": false,
  "callbackSent": false
}
```

## Testing

### Unit Tests
```bash
python -m pytest test_detector.py
python -m pytest test_extraction.py
```

### Integration Test
```bash
python test_integration.py
```

This tests:
- Health check endpoint
- API key authentication
- First message (scam detection)
- Follow-up message (intelligence extraction)
- Response format compliance

## Compliance with Problem Statement

✅ **Phase 0**: Environment setup
- FastAPI + Python
- OpenAI API integration
- Environment variables configured

✅ **Phase 1**: API skeleton & security
- `/inbound` endpoint with x-api-key authentication
- Proper HTTP status codes

✅ **Phase 2**: Scam detection
- Rule-based keyword detection
- Pattern matching for UPI, URLs, phone numbers, accounts
- Configurable threshold

✅ **Phase 3**: Session management
- Multi-turn conversation history
- Session state persistence
- Agent engagement tracking

✅ **Phase 4**: LLM agent
- Natural language replies
- Believable persona (Suman)
- Adaptive to locale/channel
- No detection revelation

✅ **Phase 5**: Intelligence extraction
- LLM + regex combined approach
- Validation of all extracted data
- Suspicious keyword tracking

✅ **Phase 6**: Multi-turn control
- Conversation continues until termination
- Agent engagement logic
- Proper state transitions

✅ **Phase 7**: GUVI callback
- **MANDATORY** final result submission
- Correct payload format
- Single submission per session
- Error handling & retries

✅ **Phase 8-10**: Testing & deployment ready
- Logging for debugging
- Health check endpoint
- Production-ready error handling

## Known Limitations & Future Improvements

### Current Limitations
1. In-memory session storage (no persistence across restarts)
2. Single worker (no horizontal scaling)
3. Basic regex patterns (could use more sophisticated NER)
4. Fixed termination criteria (could be dynamic)

### Future Enhancements
1. **Redis Backend** - Persistent session storage
2. **Named Entity Recognition** - Better intelligence extraction
3. **ML Classifier** - Improved scam detection
4. **Dashboard** - Real-time conversation monitoring
5. **Multi-language Support** - Hindi, Tamil, etc.
6. **Rate Limiting** - Prevent abuse
7. **IP Blocking** - Track malicious origins

## Troubleshooting

### Agent not responding
- Check OPENAI_API_KEY is set
- Verify API key has access to gpt-3.5-turbo
- Check OpenAI account has available credits

### GUVI callback not working
- Check internet connectivity
- Verify GUVI endpoint is accessible
- Check payload format matches spec
- Monitor logs for error details

### Intelligence not extracted
- Verify message contains patterns (UPI@format, +91XXXXXXXXXX, etc.)
- Check regex patterns are matching
- LLM may not recognize obfuscated data

### Session not persisting across restarts
- This is expected with in-memory storage
- Deploy Redis for production persistence

## Deployment

### Render (Recommended)
1. Push to GitHub
2. Connect to Render
3. Set environment variables
4. Deploy from `main.py`

### Railway
```bash
railway link
railway up
```

### Heroku
```bash
heroku create your-app-name
heroku config:set API_KEY=xxx OPENAI_API_KEY=xxx
git push heroku main
```

## Contact & Support

For issues or questions about the implementation, refer to the inline code comments and logging output. Each request logs details useful for debugging.

---

**Status**: Phase 7 Complete ✅ - Ready for evaluation
