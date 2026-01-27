# 🚀 How to Run the Server

## Option 1: Direct Python Execution (Recommended)

```bash
cd /Users/mohitsriv/Documents/Honeypot/agentic-honeypot
/opt/homebrew/bin/python3.11 main.py
```

Server will start on: `http://0.0.0.0:8000`

## Option 2: Using uvicorn directly

```bash
cd /Users/mohitsriv/Documents/Honeypot/agentic-honeypot
/opt/homebrew/bin/python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Important Note ⚠️

Make sure to use the full Python path: `/opt/homebrew/bin/python3.11`

This is because your `python` command-line tool might be pointing to a different Python installation than where the packages are installed.

---

## 🧪 Testing the Server

Once the server is running, open a NEW terminal and run:

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Full Integration Test
```bash
cd /Users/mohitsriv/Documents/Honeypot/agentic-honeypot
/opt/homebrew/bin/python3.11 test_integration.py
```

### Test 3: Quick Test
```bash
cd /Users/mohitsriv/Documents/Honeypot/agentic-honeypot
/opt/homebrew/bin/python3.11 quick_test.py
```

---

## ✅ Expected Output

When you start the server, you should see:

```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:__main__:✅ Agentic Honeypot started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 📝 Deprecation Warning (Safe to Ignore)

You may see this deprecation warning - it's safe and doesn't affect functionality:

```
DeprecationWarning: on_event is deprecated, use lifespan event handlers instead.
```

This is a FastAPI upgrade notice. The server works fine.

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"
→ Make sure you use the full path: `/opt/homebrew/bin/python3.11`

### "Address already in use"
→ The port 8000 is already taken. Either:
   - Kill the existing process: `pkill -f "python.*main.py"`
   - Or use a different port: `/opt/homebrew/bin/python3.11 main.py --port 8001`

### Can't import main
→ Make sure you're in the correct directory:
   ```bash
   cd /Users/mohitsriv/Documents/Honeypot/agentic-honeypot
   ```

---

## 💻 Example API Call

```bash
curl -X POST http://localhost:8000/inbound \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify now at http://malicious-link.com",
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

---

## 📊 What to Expect

The API should:
1. ✅ Detect the scam message
2. ✅ Activate the agent
3. ✅ Generate a reply
4. ✅ Extract intelligence (links, patterns, etc.)
5. ✅ Return spec-compliant JSON response

---

**Your server is ready to go!** 🎉
