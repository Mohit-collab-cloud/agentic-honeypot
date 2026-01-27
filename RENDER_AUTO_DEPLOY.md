# 🚀 Automatic Render Deployment Guide

## ✅ What's Automatic

Once configured:
- ✅ Every `git push` to GitHub triggers deployment
- ✅ No manual deploys needed
- ✅ Automatic build + start
- ✅ Health checks every 30 seconds
- ✅ Auto-rollback on failure

---

## 🔧 Setup (One-Time Only)

### Step 1: Push to GitHub First

```bash
cd /Users/mohitsriv/Documents/Honeypot/agentic-honeypot

# Verify all files are committed
git status

# Push any remaining changes
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Connect to Render

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Click **"New +"** → **"Web Service"**
4. Select **"GitHub"** (connect account if needed)
5. Find and select `agentic-honeypot` repository
6. Click **"Connect"**

### Step 3: Configure Service

**Render should auto-detect from `render.yaml`, but verify:**

| Setting | Value |
|---------|-------|
| Name | agentic-honeypot |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free (or Starter) |

### Step 4: Set Environment Variables

In Render dashboard → **Settings** → **Environment**:

```
OPENAI_API_KEY = sk-proj-your-actual-key
API_KEY = your-strong-random-key
MOCK_MODE = true
```

**Important:** Mark API keys as **"Private"** so they're encrypted.

### Step 5: Deploy

Click **"Create Web Service"** → Render auto-deploys!

---

## ✨ After Setup: The Magic Happens Automatically

### Your Workflow Now:

```bash
# Make changes locally
nano agent.py  # edit something

# Commit & push
git add .
git commit -m "Improve scam detection"
git push origin main

# 🎉 AUTOMATIC!
# Render sees the push
# Render builds (installs requirements)
# Render starts (runs uvicorn)
# Render health checks (/health endpoint)
# 2-3 minutes later: Live! ✅
```

### Check Deployment Status:

1. Go to Render dashboard
2. Click on **agentic-honeypot** service
3. See **"Logs"** tab (real-time build output)
4. See **"Deploys"** tab (deployment history)

---

## 🔄 How Auto-Deploy Works

```
You push code
     ↓
GitHub notifies Render
     ↓
Render reads render.yaml
     ↓
Render builds (pip install)
     ↓
Render starts service
     ↓
Render pings /health endpoint
     ↓
Service is LIVE ✅
```

---

## 📊 Deployment Status

### View Live Service:

```bash
# Your API is live at:
# https://agentic-honeypot-xxxxx.onrender.com

# Test it:
curl https://agentic-honeypot-xxxxx.onrender.com/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}
```

### View Build Logs:

1. Render Dashboard → agentic-honeypot
2. Click **"Logs"** tab
3. See real-time build output
4. Errors show here if anything fails

---

## 🛠 Common Auto-Deploy Issues

### Issue: Build Fails

**Check logs for:**
- Missing Python packages (update `requirements.txt`)
- Wrong start command (should use `$PORT`)
- Missing environment variables (add in dashboard)

**Fix:**
```bash
# Update requirements.txt locally
pip freeze > requirements.txt

# Commit & push (auto-redeploy)
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

### Issue: Service Won't Start

**Check:**
- Is `.env` being committed? (It shouldn't - gitignore it)
- Are API keys in code? (Move to environment variables)
- Is port `$PORT` used? (Not hardcoded port number)

**Fix:**
```bash
# Verify .env is in .gitignore
cat .gitignore | grep "\.env"

# Remove .env from git if accidentally committed
git rm --cached .env
git commit -m "Remove .env from tracking"
git push origin main
```

### Issue: Service Crashes After Deployment

**Check logs:**
1. Render Dashboard → Logs tab
2. Look for error messages
3. Common causes:
   - Missing import
   - Database connection error
   - Invalid API key

**Fix locally & redeploy:**
```bash
# Test locally first
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# If it works locally, push
git push origin main
```

---

## 🚨 Automatic Rollback

If a deployment fails:
- Render automatically keeps previous version running
- No downtime
- View previous deploys in **"Deploys"** tab
- Manually rollback if needed

---

## 📈 Scaling (Future)

If you need more power:

```yaml
# In render.yaml, change:
plan: starter    # More resources
numInstances: 2  # Multiple replicas
```

Then push:
```bash
git add render.yaml
git commit -m "Scale to starter plan"
git push origin main
# Auto-deploys with new resources! ✅
```

---

## ✅ Verification Checklist

After initial setup:

- [ ] GitHub connected to Render
- [ ] `render.yaml` in repository
- [ ] Environment variables set in Render dashboard
- [ ] First deployment successful (check logs)
- [ ] `/health` endpoint responds
- [ ] Make a test change, commit & push
- [ ] Auto-deployment triggered (check logs)
- [ ] Changes live in 2-3 minutes

---

## 📝 What Gets Deployed

**Automatically deployed:**
- ✅ All `.py` files
- ✅ `requirements.txt`
- ✅ `frontend/` directory
- ✅ `LICENSE`, `README.md`, documentation

**NOT deployed (gitignored):**
- ❌ `.env` (kept secret)
- ❌ `__pycache__/`
- ❌ `.git/`
- ❌ Session files

---

## 🎯 Your Service is Now:

✅ **Automatically deployed** on every push
✅ **Health checked** every 30 seconds
✅ **Auto-rollback** on failure
✅ **Live URL** provided by Render
✅ **Public API** ready for evaluation

---

## 🔗 Public API Endpoint

After deployment, you have:

```
https://agentic-honeypot-xxxxx.onrender.com/inbound
```

Share this with evaluators! They can test:

```bash
curl -X POST https://agentic-honeypot-xxxxx.onrender.com/inbound \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "sessionId": "eval-1",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked..."
    }
  }'
```

---

## 📞 Monitoring

### Render Dashboard Shows:

1. **Status** - Is service running?
2. **Logs** - Real-time output
3. **Deploys** - Deployment history
4. **Metrics** - CPU, memory usage
5. **Events** - All auto-events

Check regularly to monitor health!

---

## 🎉 You're Done!

Your deployment is now:
- ✅ Fully automatic
- ✅ Zero downtime
- ✅ Publicly accessible
- ✅ Production-ready

**Just push code to GitHub, and Render handles the rest!** 🚀

---

## Next Steps:

1. ✅ Push code to GitHub
2. ✅ Connect GitHub to Render
3. ✅ Set environment variables
4. ✅ Watch auto-deployment in logs
5. ✅ Share public URL with evaluators
6. ✅ Every future push = auto-update

**Your agentic honeypot is now live!** 🎊
