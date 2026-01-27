# GitHub Publishing & Security Guide for Agentic Honeypot

## 📋 Table of Contents
1. [Publishing to GitHub](#publishing-to-github)
2. [Security & IP Protection](#security--ip-protection)
3. [What to Share for Evaluation](#what-to-share-for-evaluation)
4. [GitHub Repository Setup](#github-repository-setup)

---

## 🚀 Publishing to GitHub

### Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and log in
2. Click "New Repository" (+ icon in top right)
3. **Repository name**: `agentic-honeypot`
4. **Description**: `AI-powered honeypot system for detecting and engaging with scammers using intelligent agent responses`
5. **Visibility**: Choose based on security needs (see below)
6. **Initialize with README**: No (we'll add custom one)
7. Click "Create Repository"

### Step 2: Initialize Git Locally

```bash
cd /Users/mohitsriv/Documents/Honeypot/agentic-honeypot

# Initialize git repository
git init

# Add all files (respecting .gitignore)
git add .

# Initial commit
git commit -m "Initial commit: Agentic honeypot with context-aware agent"

# Add GitHub as remote (replace YOUR_USERNAME and repo name)
git remote add origin https://github.com/YOUR_USERNAME/agentic-honeypot.git

# Rename branch to main (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 3: Verify Upload

```bash
# Verify remote was added
git remote -v

# Check what was pushed
git log --oneline -10
```

---

## 🔒 Security & IP Protection

### Option 1: Private Repository (RECOMMENDED)

**Best for: Protecting proprietary code and evaluation purposes**

```bash
# On GitHub:
1. Go to Settings → General
2. Find "Danger Zone" section
3. Change Repository visibility to PRIVATE
4. Confirm the change
```

**Pros:**
- ✅ Only authorized people can see your code
- ✅ Prevents others from copying
- ✅ Safe for evaluation with specific evaluators

**Cons:**
- ❌ Limited collaboration/community visibility

---

### Option 2: Public with License + Code Obfuscation

**Best for: Open source with legal protection**

```bash
# Add a restrictive license (e.g., AGPL-3.0)
# This legally prevents commercial use without sharing modifications
```

Create `LICENSE` file:

```
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007

[Full AGPL-3.0 license text]
```

Then compile Python to bytecode for distribution:

```bash
# Compile to bytecode (.pyc)
python3 -m py_compile *.py

# Remove source files and keep only .pyc
# Users can run .pyc but not easily read source
```

---

### Option 3: Fork-Friendly Public Repo with README Notice

Add this to README.md:

```markdown
## ⚠️ Important Notice

This project is provided for:
- Educational purposes
- Research and development
- Authorized security testing only

**UNAUTHORIZED ACCESS ATTEMPTS** to honeypot systems are illegal under:
- Computer Fraud and Abuse Act (CFAA) in US
- Information Technology Act, 2000 in India
- Similar laws in your jurisdiction

By using this code, you agree to use it only for:
✅ Personal learning
✅ Authorized penetration testing (with written permission)
✅ Research with proper institutional approval

Unauthorized use may result in legal action.
```

---

## 📦 What to Share for Evaluation

### For GUVI Evaluation (Most Important)

**Create an `EVALUATION.md` file** with:

```markdown
# Evaluation Submission

## Quick Start (5 minutes)

### 1. Setup
```bash
# Clone/receive the code
cd agentic-honeypot

# Create .env from .env.example
cp .env.example .env

# Add your OpenAI API key
# OR use MOCK_MODE=true (pre-configured for testing)
```

### 2. Start Server
```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Test the API
```bash
curl -X POST http://localhost:8000/inbound \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "sessionId": "eval-1",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify immediately at this link."
    }
  }'
```

Expected Response:
```json
{
  "status": "success",
  "scamDetected": true,
  "agentReply": "Is it safe to click that link? What's the actual website?"
}
```

### 4. Run Full Test Suite
```bash
python3 test_all_categories.py
```

## Core Features Demonstrated

✅ Detects 16+ scam categories
✅ Context-aware agent responses
✅ Multi-turn conversation support
✅ Intelligence extraction (URLs, UPIs, phone numbers)
✅ Callback integration for evaluation platform
✅ Dark-themed React dashboard
✅ Production-ready FastAPI backend

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/inbound` | POST | Main honeypot - receives scam, engages agent |
| `/health` | GET | Server health check |
| `/dashboard` | GET | Interactive React UI |

## File Structure

```
agentic-honeypot/
├── agent.py              # Context-aware LLM agent
├── detector.py           # Scam detection with 100+ keywords
├── main.py               # FastAPI server & endpoints
├── callback.py           # GUVI evaluation callback
├── session_store.py      # Session management
├── intel_store.py        # Intelligence extraction & storage
├── frontend/
│   └── index.html        # React dashboard (dark theme)
├── .env.example          # Environment template
├── README.md             # Documentation
├── test_all_categories.py # Comprehensive test suite
└── EVALUATION.md         # This file

## Evaluation Checklist

- [ ] Server starts without errors
- [ ] `/health` endpoint responds
- [ ] Scam messages detected correctly
- [ ] Agent replies are contextually appropriate
- [ ] Multi-turn conversations maintain context
- [ ] Intelligence extraction works
- [ ] Dashboard loads at http://localhost:8000
- [ ] GUVI callback sends successfully

## Performance Metrics

- Detection Speed: < 100ms per message
- Response Generation: < 500ms (mock mode) / 1-2s (LLM mode)
- Context Window: Last 8 messages (600 tokens)
- Concurrent Sessions: Unlimited (in-memory)

## Support for Evaluators

For any issues:
1. Check that .env is properly configured
2. Verify API key permissions (for OpenAI)
3. Check firewall rules (port 8000)
4. Run in MOCK_MODE=true for testing without API costs
```

---

### Minimum Files to Share

**ALWAYS Include:**
1. ✅ `agent.py` - Core agent logic
2. ✅ `main.py` - FastAPI server
3. ✅ `detector.py` - Scam detection
4. ✅ `callback.py` - Evaluation integration
5. ✅ `session_store.py` - Session management
6. ✅ `intel_store.py` - Intelligence storage
7. ✅ `frontend/index.html` - Dashboard
8. ✅ `README.md` - Setup instructions
9. ✅ `.env.example` - Configuration template
10. ✅ `requirements.txt` - Dependencies
11. ✅ `test_all_categories.py` - Test suite

**NEVER Share:**
1. ❌ `.env` (real API keys)
2. ❌ `__pycache__/`
3. ❌ `.pyc` files
4. ❌ Session/database files
5. ❌ API keys in any form

**Optional (for context):**
- `EVALUATION.md` - Evaluation guide
- `ARCHITECTURE.md` - System design
- `FINAL_STATUS.md` - Completion summary

---

### Create requirements.txt

```bash
# Generate from current environment
pip freeze > requirements.txt

# Or manually create:
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
openai==2.15.0
python-dotenv==1.0.0
requests==2.31.0
EOF
```

---

## 🔐 Repository Settings for Security

### On GitHub:

**Settings → Collaborators & Teams:**
- Add only authorized evaluators
- Set permissions: `Read` (for evaluation)

**Settings → Branches:**
- Require pull request reviews before merge
- Require status checks to pass

**Settings → Security & Analysis:**
- Enable Dependabot alerts
- Enable secret scanning

---

## 📝 Creating a Private Evaluation Submission

### For Direct Submission to GUVI:

1. **Create a private GitHub organization** (free):
   - Go to github.com/organizations/new
   - Name: `honeypot-eval-[timestamp]`
   - Make it private
   - Add only GUVI evaluators as collaborators

2. **Push code there:**
   ```bash
   git remote remove origin
   git remote add origin https://github.com/your-org/agentic-honeypot.git
   git push -u origin main
   ```

3. **Share access link with GUVI:**
   - Provide: GitHub organization URL
   - Credentials: Temporary evaluator account
   - Expiry: Set date for access revocation

---

## ⚡ Quick Reference Checklist

Before publishing:

- [ ] Created `.env.example` (no real API keys)
- [ ] Updated `.gitignore` (comprehensive)
- [ ] Created `requirements.txt`
- [ ] Created `README.md` with setup instructions
- [ ] Created `EVALUATION.md` with test procedures
- [ ] Verified `.env` is NOT in git (`git status`)
- [ ] Tested: `git clone` + setup works
- [ ] Added LICENSE (AGPL-3.0 or your choice)
- [ ] Set repository to PRIVATE (if needed)
- [ ] Added collaborators (evaluators only)
- [ ] Tested all endpoints work
- [ ] Ran test suite successfully

---

## 🎯 Summary

| Aspect | Recommendation |
|--------|---|
| **Repository Type** | PRIVATE (for evaluation) |
| **License** | AGPL-3.0 (to prevent commercial copying) |
| **Share With Evaluators** | GitHub access + `.env.example` template |
| **Secrets** | Use `.env.example` + environment variables |
| **Testing** | Include `test_all_categories.py` |
| **Documentation** | README.md + EVALUATION.md + ARCHITECTURE.md |

Your project is production-ready and evaluation-ready! 🚀
