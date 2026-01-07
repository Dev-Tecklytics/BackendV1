# GitHub Repository Setup Guide

## Issue: "Repository not found" Error

The error occurs because the repository `https://github.com/Dev-Tecklytics/New_Backend.git` doesn't exist on GitHub yet.

---

## Solution Steps

### Step 1: Create Repository on GitHub

1. Go to: https://github.com/Dev-Tecklytics
2. Click the green "New" button (or go to https://github.com/new)
3. Fill in:
   - **Repository name**: `New_Backend`
   - **Description**: "IAAP Backend API - FastAPI application"
   - **Visibility**: Choose Private or Public
   - **DO NOT check**: "Initialize this repository with a README"
4. Click "Create repository"

### Step 2: Push Your Code

After creating the repository on GitHub, run:

```powershell
cd C:\Users\Prasanna\Downloads\backend\backend

# Verify remote is set
git remote -v

# Push to GitHub
git push -u origin main
```

---

## Alternative: Use GitHub CLI

If you have GitHub CLI installed:

```powershell
# Login (if not already logged in)
gh auth login

# Create and push in one command
gh repo create Dev-Tecklytics/New_Backend --private --source=. --push
```

---

## If Repository Already Exists

If the repository exists but you're getting the error:

### Check 1: Verify Repository URL
Visit: https://github.com/Dev-Tecklytics/New_Backend

If it doesn't exist, create it (see Step 1 above).

### Check 2: Authentication
You might need to authenticate with a Personal Access Token:

1. Create token: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scope: `repo`
4. Copy the token

Then update your remote:
```powershell
git remote set-url origin https://YOUR_TOKEN@github.com/Dev-Tecklytics/New_Backend.git
git push -u origin main
```

### Check 3: Use SSH Instead of HTTPS

```powershell
# Change to SSH
git remote set-url origin git@github.com:Dev-Tecklytics/New_Backend.git

# Push
git push -u origin main
```

---

## Verify Your Setup

```powershell
# Check current branch
git branch

# Check remote
git remote -v

# Check git status
git status

# View commit history
git log --oneline -5
```

---

## Common Issues

### "Support for password authentication was removed"
**Solution**: Use Personal Access Token instead of password

### "Permission denied (publickey)"
**Solution**: Set up SSH keys or use HTTPS with token

### "Failed to push some refs"
**Solution**: Pull first, then push:
```powershell
git pull origin main --rebase
git push -u origin main
```

---

## Quick Reference

```powershell
# Create repo on GitHub first, then:
git push -u origin main

# Or use GitHub CLI:
gh repo create Dev-Tecklytics/New_Backend --private --source=. --push

# Check status:
git status
git remote -v
git log --oneline
```

---

**Next Steps After Successful Push:**
1. ✅ Repository created on GitHub
2. ✅ Code pushed successfully
3. ✅ Set up branch protection rules (optional)
4. ✅ Add collaborators (optional)
5. ✅ Configure GitHub Actions (optional)
