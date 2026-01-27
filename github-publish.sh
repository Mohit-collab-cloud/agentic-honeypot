#!/bin/bash

# Agentic Honeypot - GitHub Publishing Helper Script
# This script helps you safely publish to GitHub

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Agentic Honeypot - GitHub Publishing Helper               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Verify current directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found in current directory"
    echo "Please run this script from the agentic-honeypot directory"
    exit 1
fi

echo "✅ Found agentic-honeypot directory"
echo ""

# Step 2: Check .env is not in git
if git ls-files --cached --others --exclude-standard | grep -q "^\.env$"; then
    echo "⚠️  WARNING: .env file is tracked in git!"
    echo "Removing .env from git tracking (it will remain locally)..."
    git rm --cached .env 2>/dev/null || true
    echo "✅ .env removed from git tracking"
fi

# Step 3: Verify .env is gitignored
if ! grep -q "^\.env" .gitignore; then
    echo "⚠️  .env not in .gitignore, adding it..."
    echo ".env" >> .gitignore
fi

echo "✅ .env is properly gitignored"
echo ""

# Step 4: Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""

# Step 5: Check status
echo "📋 Current git status:"
git status --short | head -20
echo ""

# Step 6: Show what will be committed
echo "📦 Files that will be committed:"
git add --dry-run . 2>/dev/null | head -20
echo ""

# Step 7: Instructions
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    NEXT STEPS                                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "1️⃣  Commit changes locally:"
echo "   git add ."
echo "   git commit -m 'Initial commit: Agentic honeypot with context-aware agent'"
echo ""

echo "2️⃣  Create a repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Name: agentic-honeypot"
echo "   - Visibility: PRIVATE (recommended for protection)"
echo "   - DO NOT initialize with README"
echo ""

echo "3️⃣  Add GitHub as remote:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/agentic-honeypot.git"
echo ""

echo "4️⃣  Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

echo "5️⃣  Share for evaluation:"
echo "   - Go to Settings → Collaborators"
echo "   - Add evaluator GitHub username"
echo "   - Share this: EVALUATION.md"
echo ""

echo "📖 For detailed guide, see: GITHUB_SECURITY_GUIDE.md"
echo ""

echo "🔒 Security Checklist:"
echo "   [ ] Using PRIVATE repository"
echo "   [ ] .env not committed to git"
echo "   [ ] .env.example has placeholder values only"
echo "   [ ] requirements.txt is up to date"
echo "   [ ] README.md has setup instructions"
echo "   [ ] Added LICENSE file (AGPL-3.0 recommended)"
echo ""

echo "✨ You're ready to publish!"
