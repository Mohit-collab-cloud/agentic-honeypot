# System Architecture & Data Flow

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENTIC HONEYPOT SYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

                         FastAPI Server
                       (main.py - /inbound)
                              │
                ┌─────────────┼─────────────┐
                │             │             │
           Auth Check     Scam Detection   Session
           (x-api-key)     (detector.py)   Mgmt
              │             │             (session_store)
              │             │             │
         401 if fail    Score >= 2    Create/Update
                        return bool   conversation
                            │             │
                            ▼             ▼
                      ┌──────────────────────────┐
                      │  Agent Engagement Logic  │
                      │    (if scam detected)    │
                      └──────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
            Reply Gen              Intelligence
          (agent.py)               Extraction
                │                  (agent.py)
    ┌───────────┴───────────┐         │
    │ LLM Call (GPT-3.5)    │    ┌────┴─────┐
    │ - Natural reply       │    │ LLM Call  │
    │ - No JSON in reply    │    │ + Regex   │
    │ - Adaptive persona    │    │ Validation│
    └───────────┬───────────┘    └────┬─────┘
                │                      │
                ▼                      ▼
        ┌────────────────┐    ┌─────────────────┐
        │ Agent Reply    │    │ Extracted Data  │
        │ (natural text) │    │ (intel_store)   │
        └────────────────┘    └────────┬────────┘
                │                      │
                └──────────┬───────────┘
                           │
                    ┌──────▼──────┐
                    │ Update      │
                    │ Session &   │
                    │ History     │
                    └──────┬──────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
     Check Termination              Build Response
     Criteria                        (spec compliant)
            │                             │
            ▼                             ▼
     ┌─────────────────┐      ┌────────────────────┐
     │ Should Continue?│      │ Return JSON with:  │
     │                 │      │ - status           │
     │ - Max messages? │      │ - scamDetected     │
     │ - High-value    │      │ - engagementMetrics│
     │   intel?        │      │ - extractedIntel   │
     │ - Timeout?      │      │ - agentNotes       │
     └────────┬────────┘      └────────┬───────────┘
              │                        │
          YES │ Continue              │ Send to
          conversation              Client
              │
              NO
              │
              ▼
     ┌─────────────────────┐
     │ Mark Complete       │
     │ Send GUVI Callback  │  ◄─── MANDATORY!
     │ (callback.py)       │
     └──────────┬──────────┘
                │
                ▼
     ┌──────────────────────────────────┐
     │ POST to evaluation endpoint:      │
     │ /api/updateHoneyPotFinalResult    │
     │                                   │
     │ Payload:                          │
     │ - sessionId                       │
     │ - scamDetected                    │
     │ - totalMessagesExchanged          │
     │ - extractedIntelligence           │
     │ - agentNotes                      │
     └──────────────────────────────────┘
```

---

## Request/Response Flow

### Incoming Request
```json
{
  "sessionId": "unique-id",
  "message": {
    "sender": "scammer",
    "text": "Your account blocked...",
    "timestamp": "ISO-8601"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Processing Steps

```
1. AUTHENTICATION
   ├─ Check x-api-key header
   └─ Return 401 if missing/invalid

2. SCAM DETECTION
   ├─ Run keyword matching
   ├─ Run pattern detection
   ├─ Score: keywords + patterns
   └─ Result: scamDetected (bool)

3. SESSION MANAGEMENT
   ├─ Load existing session or create new
   ├─ Append incoming message
   ├─ Increment message counter
   └─ Track timestamps

4. AGENT ENGAGEMENT (if scam detected)
   ├─ Mark session as agentEngaged
   ├─ Generate natural reply
   ├─ Extract intelligence
   └─ Update session state

5. TERMINATION CHECK
   ├─ Evaluate termination criteria
   ├─ If complete: mark endTime
   └─ Prepare final summary

6. GUVI CALLBACK (if complete)
   ├─ Build payload
   ├─ POST to evaluation endpoint
   └─ Mark callback sent (prevent duplicates)

7. RESPONSE BUILD
   ├─ Calculate engagement duration
   ├─ Format per specification
   └─ Return to client
```

### Outgoing Response
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
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "verify", "account"]
  },
  "agentNotes": "Scammer used urgency tactics",
  "agentReply": "Why would my account be blocked?",
  "engagementComplete": false,
  "callbackSent": false
}
```

---

## Session Lifecycle

```
┌──────────┐
│  Start   │
└────┬─────┘
     │
     ▼
┌─────────────────────┐
│ NEW SESSION CREATED │
│                     │
│ - sessionId         │
│ - startTime         │
│ - endTime: None     │
│ - totalMessages: 0  │
│ - agentEngaged: F   │
│ - callbackSent: F   │
└────────────────────┬─
                     │
                     ▼
            ┌─────────────────┐
            │ MESSAGE 1       │
            │ - Detect scam   │
            │ - If YES:       │
            │   agentEngaged◄─┼─→ TRUE
            │   callLLM       │
            │ - append history│
            │ - counter: 1    │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ MESSAGE 2       │
            │ - Extract intel │
            │ - Update state  │
            │ - append reply  │
            │ - counter: 2    │
            │ - Check term.   │
            └────────┬────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
      Continue?            YES: End
          │                    │
         NO                    ▼
          │          ┌──────────────────┐
          │          │ MARK COMPLETE    │
          │          │ - endTime = now  │
          │          │ - duration calc  │
          │          └────────┬─────────┘
          │                   │
          │                   ▼
          │          ┌──────────────────┐
          │          │ SEND CALLBACK    │
          │          │ - POST to GUVI   │
          │          │ - Mark sent      │
          │          └────────┬─────────┘
          │                   │
          └─────────┬─────────┘
                    │
                    ▼
            ┌──────────────────┐
            │ RETURN RESPONSE  │
            │ (engagement data)│
            └────────┬─────────┘
                     │
                     ▼
                  ┌─────────┐
                  │   END   │
                  └─────────┘
```

---

## Data Extraction Pipeline

```
Incoming Message Text
        │
        ▼
┌──────────────────────────────┐
│ LLM EXTRACTION (Low Temp)    │
│ - Ask model to find UPI/etc  │
│ - Get JSON response          │
│ - Parse candidates           │
└──────────┬───────────────────┘
           │
           ▼
   ┌───────────────────┐
   │ CANDIDATE DATA    │
   ├───────────────────┤
   │ UPI: [...]        │
   │ Accounts: [...]   │
   │ URLs: [...]       │
   │ Phones: [...]     │
   └────────┬──────────┘
            │
            ▼
┌───────────────────────────────┐
│ REGEX VALIDATION & ENRICHMENT │
├───────────────────────────────┤
│ UPI:       [a-z0-9]+@[a-z]+   │
│ Phone:     +91|0[6-9]\d{9}    │
│ URL:       https?://          │
│ Account:   \d{9,18} (no phone)│
└──────────┬────────────────────┘
           │
           ▼
   ┌───────────────────┐
   │ VALIDATED DATA    │
   ├───────────────────┤
   │ UPI: [valid]      │
   │ Accounts: [valid] │
   │ URLs: [valid]     │
   │ Phones: [valid]   │
   └────────┬──────────┘
            │
            ▼
┌──────────────────────────┐
│ DUPLICATE PREVENTION     │
│ (merge_unique)           │
├──────────────────────────┤
│ ∪ Existing + New         │
│ → Set (remove duplicates)│
│ → List                   │
└──────────┬───────────────┘
           │
           ▼
   ┌──────────────────────┐
   │ STORE IN SESSION     │
   ├──────────────────────┤
   │ extractedIntelligence│
   │ └─ upiIds            │
   │ └─ bankAccounts      │
   │ └─ phishingLinks     │
   │ └─ phoneNumbers      │
   │ └─ suspiciousKeywords│
   └──────────────────────┘
```

---

## Engagement Termination Criteria

```
Should Continue Engagement?
        │
        ├─────────────────────────────────────┐
        │                                     │
        ▼                                     ▼
    Check Counters                    Check Intelligence
        │                                     │
    ┌───┴───┐                          ┌──────┴──────┐
    │       │                          │      │      │
  Max?  More?                       UPI?  Account? URL?
    │     │                          │      │      │
   YES   NO                          Y      Y      Y
    │     │                          └──────┬──────┘
    │     └─→ Continue                      │
    │                                   Has Data
    │        ┌────────────────────────────┬─┘
    │        │                            │
    │        │                        MORE THAN
    │        │                        6 MESSAGES
    │        │                            │
    │        │                        ┌───┴────┐
    │        │                        │         │
    │        │                       YES        NO
    │        │                        │         │
    │        │                     STOP      CONTINUE
    │        │
    │        ▼
    │     ┌──────────┐
    │     │ CONTINUE │
    │     └──────────┘
    │
    ▼
 ┌─────┐
 │ END │ → Send Callback → Return Response
 └─────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────────┐
│ Incoming Request                │
└────────────┬────────────────────┘
             │
             ▼
    ┌────────────────┐
    │ Try...Except   │
    │ Validation     │
    └────────┬───────┘
             │
    ┌────────┴──────────────────┐
    │                           │
    ▼                           ▼
 Valid                      Invalid
    │                           │
    │                           ▼
    │                    ┌──────────────┐
    │                    │ Log Error    │
    │                    │ Return 422   │
    │                    └──────────────┘
    │
    ▼
┌──────────────────────────┐
│ Try Auth Check           │
└────────┬─────────────────┘
         │
    ┌────┴─────────────┐
    │                  │
 VALID              INVALID
    │                  │
    │                  ▼
    │           ┌──────────────┐
    │           │ Raise 401    │
    │           └──────────────┘
    │
    ▼
┌──────────────────────────┐
│ Try Detector              │
└────────┬─────────────────┘
         │
    ┌────┴─────┐
    │           │
 SUCCESS    FAILURE
    │           │
    │           ▼
    │    ┌──────────────────┐
    │    │ Log Error        │
    │    │ scamDetected=F   │
    │    └──────────────────┘
    │
    ▼
┌──────────────────────────┐
│ Try LLM Call             │
└────────┬─────────────────┘
         │
    ┌────┴──────────────┐
    │                   │
 SUCCESS            FAILURE
    │                   │
    │                   ▼
    │           ┌──────────────────┐
    │           │ Log Error        │
    │           │ Fallback Reply   │
    │           │ Continue         │
    │           └──────────────────┘
    │
    ▼
┌──────────────────────────┐
│ Try GUVI Callback        │
└────────┬─────────────────┘
         │
    ┌────┴──────────────────┐
    │                       │
 SUCCESS               FAILURE
    │                       │
    │                       ▼
    │               ┌──────────────────┐
    │               │ Log Error        │
    │               │ Mark Failed      │
    │               │ Can Retry Later  │
    │               └──────────────────┘
    │
    ▼
 Return Response
   (always)
```

---

## Multi-Turn Conversation Example

```
Turn 1:
┌────────────────────────────────────────────┐
│ Scammer: "Account blocked. Verify now."    │
├────────────────────────────────────────────┤
│ Detection: Score = 3 (keywords)            │
│ scamDetected: TRUE                         │
│ → Activate Agent                           │
│                                            │
│ Agent Reply: "Why is my account blocked?"  │
│ Extracted: [] (no data yet)                │
└────────────────────────────────────────────┘

Turn 2:
┌────────────────────────────────────────────┐
│ Scammer: "Click link: http://verify-me.x   │
│          or send UPI: hacker@bank"         │
├────────────────────────────────────────────┤
│ Detection: Score = 5 (link + UPI keyword)  │
│ scamDetected: TRUE                         │
│ → Continue Agent                           │
│                                            │
│ Agent Reply: "I'm confused. What's this?"  │
│ Extracted: {                               │
│   "urls": ["http://verify-me.x"],          │
│   "upi": ["hacker@bank"]                   │
│ }                                          │
└────────────────────────────────────────────┘

Turn 3:
┌────────────────────────────────────────────┐
│ Scammer: "Send ₹5000 to verify account"    │
├────────────────────────────────────────────┤
│ Detection: Score = 4 (money + verify)      │
│ scamDetected: TRUE                         │
│ → Continue Agent                           │
│                                            │
│ Agent Reply: "That seems wrong. I'm not    │
│              sending money."               │
│ Extracted: [] (no new data)                │
│                                            │
│ Check Termination:                         │
│ - Messages: 3 (< max 20)                   │
│ - Has UPI + Account: YES                   │
│ - Messages ≥ 6: NO                         │
│ - Continue? YES                            │
└────────────────────────────────────────────┘

Turn 4:
┌────────────────────────────────────────────┐
│ Scammer: "Your account 9876543210 blocked" │
├────────────────────────────────────────────┤
│ Detection: Score = 4 (keywords + account)  │
│ scamDetected: TRUE                         │
│ → Continue Agent                           │
│                                            │
│ Agent Reply: "Ok I'm getting off this."    │
│ Extracted: {                               │
│   "accounts": ["9876543210"]                │
│ }                                          │
│                                            │
│ Check Termination:                         │
│ - Messages: 4 (< max 20)                   │
│ - Has UPI + Account: YES                   │
│ - Messages ≥ 6: NO                         │
│ - Continue? YES                            │
└────────────────────────────────────────────┘

Turn 5-6: (2 more messages)

Turn 7:
┌────────────────────────────────────────────┐
│ Check Termination:                         │
│ - Messages: 7 (< max 20)                   │
│ - Has UPI + Account: YES ✓                 │
│ - Messages ≥ 6: YES ✓                      │
│ → TERMINATION CRITERIA MET!                │
│                                            │
│ ENGAGEMENT COMPLETE = TRUE                 │
│ → Send GUVI Callback                       │
│ → Mark callbackSent = TRUE                 │
└────────────────────────────────────────────┘
```

---

## File Dependencies

```
main.py (FastAPI server)
├── detector.py
│   └── Uses: regex patterns
├── session_store.py
│   └── Manages: session state
├── intel_store.py
│   └── Manages: extracted intelligence
├── agent.py
│   └── Uses: OpenAI API (GPT-3.5)
└── callback.py
    └── Uses: requests library

Dependencies:
- fastapi
- uvicorn
- openai
- python-dotenv
- requests
- pydantic
```

---

This architecture ensures:
✅ Clean separation of concerns
✅ Easy to test and debug
✅ Scalable design
✅ Spec-compliant responses
✅ Mandatory GUVI integration
