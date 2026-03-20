# Silver Tier Setup Guide - AI Employee

> **Tagline:** Multiple watchers, MCP server, approval workflow, and scheduling

This guide walks you through setting up the complete Silver Tier AI Employee system.

---

## 📋 Silver Tier Deliverables

| Requirement | Status | Script/Skill |
|-------------|--------|--------------|
| Two or more Watcher scripts | ✅ | Gmail, LinkedIn, File System |
| Auto-post on LinkedIn | ✅ | `linkedin_poster.py` |
| Plan.md creation | ✅ | Plan Manager Skill |
| MCP server for emails | ✅ | Email MCP Skill |
| HITL approval workflow | ✅ | HITL Approval Skill |
| Basic scheduling | ✅ | Scheduler Skill |

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd AI_Employee_Vault/scripts

# Install all Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 2: Verify Credentials

**Gmail:** Ensure `credentials.json` exists in project root:
```
C:\Users\Haya Javed\Downloads\Hackathon0\credentials.json
```

**LinkedIn:** No setup needed - you'll login manually on first run.

### Step 3: First Run - Authorize Gmail

```bash
cd C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault
python scripts/gmail_watcher.py .
```

On first run:
1. Browser opens automatically
2. Login to your Google account
3. Grant Gmail API permissions
4. Token saved for future runs

Press `Ctrl+C` to stop after authorization.

### Step 4: Start All Watchers

```bash
# Option A: Start all watchers via orchestrator
python scripts/orchestrator.py . all

# Option B: Start individual watchers
python scripts/filesystem_watcher.py .
python scripts/gmail_watcher.py . 120
python scripts/linkedin_watcher.py . 300
```

### Step 5: Test the System

**Test File Watcher:**
1. Drop any file into `Inbox/Drop/`
2. Check `Needs_Action/` for action file

**Test Gmail Watcher:**
1. Send yourself an email with subject "Test"
2. Wait up to 2 minutes
3. Check `Needs_Action/` for action file

**Test LinkedIn Watcher:**
1. Wait for LinkedIn notifications
2. Check `Needs_Action/` for LinkedIn action files

---

## 📁 Script Overview

### Watchers

| Script | Purpose | Interval | Auth Required |
|--------|---------|----------|---------------|
| `filesystem_watcher.py` | Monitor file drops | Event-driven | None |
| `gmail_watcher.py` | Monitor Gmail | 120 seconds | OAuth2 |
| `linkedin_watcher.py` | Monitor LinkedIn | 300 seconds | Session |

### Actions

| Script | Purpose | Approval Required |
|--------|---------|-------------------|
| `linkedin_poster.py` | Post to LinkedIn | **Yes** (HITL) |
| `orchestrator.py` | Manage all watchers | N/A |

---

## 🔧 Gmail Setup (Detailed)

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable **Gmail API**:
   - APIs & Services → Library
   - Search "Gmail API"
   - Click Enable

### 2. Create OAuth Credentials

1. APIs & Services → Credentials
2. Create Credentials → OAuth 2.0 Client ID
3. Application type: **Desktop app**
4. Download `credentials.json`
5. Place in project root:
   ```
   C:\Users\Haya Javed\Downloads\Hackathon0\credentials.json
   ```

### 3. Authorize (First Run)

```bash
python scripts/gmail_watcher.py .
```

Browser opens → Login → Grant permissions → Token saved

### 4. Test

Send email to yourself with subject containing:
- "urgent", "asap", "invoice", "payment" → High priority
- Other subjects → Medium/Low priority

Check `Needs_Action/` folder for action file.

---

## 🔧 LinkedIn Setup (Detailed)

### 1. Install Playwright

```bash
pip install playwright
playwright install chromium
```

### 2. First Run - Login

```bash
python scripts/linkedin_watcher.py . 300
```

On first run:
1. Browser opens to LinkedIn login
2. Login manually (takes up to 2 minutes)
3. Session saved to `.cache/linkedin_session/`
4. Watcher starts monitoring

### 3. Configure Keywords

Edit `linkedin_watcher.py` to customize keywords:

```python
self.keywords = {
    'high': ['hiring', 'opportunity', 'interview'],  # High priority
    'medium': ['connection', 'message', 'comment'],   # Medium priority
    'low': ['like', 'view', 'follower']               # Low priority (ignored)
}
```

---

## 📝 LinkedIn Auto-Posting (HITL Workflow)

### Create Post (Generates Approval Request)

```bash
# Generate post from topic
python scripts/linkedin_poster.py . --topic "AI Employee launch" --tone professional

# Or post custom content
python scripts/linkedin_poster.py . --post "🚀 Exciting news! We've launched our AI Employee..."
```

### Approve Post

1. Check `Pending_Approval/` for approval file
2. Review content
3. **To Approve:** Move file to `Approved/`
4. **To Reject:** Move file to `Rejected/`

### Process Approved Posts

```bash
# Process all approved posts
python scripts/linkedin_poster.py . --process-approved
```

Post is published → Logged → Moved to `Done/`

---

## ⏰ Scheduling Tasks

### Windows Task Scheduler

**Daily Briefing (8:00 AM):**
```powershell
schtasks /Create /TN "AI Employee - Daily Briefing" `
  /TR "qwen 'Generate daily briefing'" `
  /SC DAILY /ST 08:00 `
  /SD C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault
```

**Gmail Check (Every 5 minutes):**
```powershell
schtasks /Create /TN "AI Employee - Gmail Check" `
  /TR "python scripts/gmail_watcher.py ." `
  /SC MINUTE /MO 5 `
  /SD C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault
```

### Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add entries
0 8 * * * cd /path/to/vault && qwen "Generate daily briefing"
*/5 * * * * cd /path/to/vault && python scripts/gmail_watcher.py .
*/5 * * * * cd /path/to/vault && python scripts/linkedin_watcher.py .
0 22 * * 0 cd /path/to/vault && qwen "Generate weekly CEO briefing"
```

---

## 🔄 Complete Workflow Example

### Scenario: Client Email → Invoice → LinkedIn Post

1. **Gmail Watcher detects** email: "Can you send invoice for January?"
2. **Creates action file** in `Needs_Action/EMAIL_...md`
3. **Qwen reads** email, checks `Company_Handbook.md`
4. **Creates Plan.md** in `Plans/`
5. **Generates invoice** PDF
6. **Creates approval request** in `Pending_Approval/`
7. **Human approves** → moves to `Approved/`
8. **Email MCP sends** invoice
9. **Qwen creates LinkedIn post**: "Just sent invoices for January! Great month!"
10. **Human approves post** → moves to `Approved/`
11. **LinkedIn Poster publishes** → logs → moves to `Done/`

---

## 🛠️ Troubleshooting

### Gmail Watcher Issues

**"Credentials file not found"**
```bash
# Verify location
dir C:\Users\Haya Javed\Downloads\Hackathon0\credentials.json

# Or set environment variable
set GMAIL_CREDENTIALS_PATH=C:\path\to\credentials.json
```

**"Token expired"**
```bash
# Delete old token
del scripts\token.json

# Re-run authorization
python scripts/gmail_watcher.py .
```

### LinkedIn Watcher Issues

**"Not logged in"**
```bash
# Clear session
rmdir /s /q .cache\linkedin_session

# Re-run and login manually
python scripts/linkedin_watcher.py . 300
```

**Rate limiting**
- Increase check interval (minimum 300 seconds)
- Don't run too frequently

### General Issues

**Watcher not creating files**
1. Check watcher is running (log output)
2. Verify folder permissions
3. Check `Needs_Action/` exists

**Qwen not processing**
1. Ensure `qwen` command works: `qwen --version`
2. Run in vault directory
3. Check for files in `Needs_Action/`

---

## 📊 Monitoring

### Check Watcher Status

```bash
# Windows: Check running processes
tasklist | findstr python

# Or check logs
type scripts\*.log
```

### Dashboard Updates

Check `Dashboard.md` regularly:
- Pending Actions count
- Pending Approvals count
- Recent activity

### Logs

```
AI_Employee_Vault/
├── Logs/
│   ├── gmail_2026-03-18.log
│   ├── linkedin_2026-03-18.log
│   └── orchestrator_2026-03-18.log
└── .cache/
    └── [processed items cache]
```

---

## ✅ Silver Tier Checklist

Track your progress:

- [x] **Dependencies installed**
  - [x] `pip install -r requirements.txt`
  - [x] `playwright install chromium`

- [x] **Gmail Watcher working**
  - [x] Credentials.json in place
  - [x] OAuth completed
  - [x] Test email received

- [x] **LinkedIn Watcher working**
  - [x] Playwright installed
  - [x] Session saved
  - [x] Monitoring notifications

- [x] **File System Watcher working**
  - [x] Test file dropped
  - [x] Action file created

- [x] **LinkedIn Poster working**
  - [x] Test post created
  - [x] Approval workflow tested
  - [x] Post published

- [x] **Orchestrator working**
  - [x] All watchers start together
  - [x] Logs show activity

- [ ] **Scheduling configured** (optional)
  - [ ] Daily briefing scheduled
  - [ ] Weekly audit scheduled

---

## 📚 Next Steps (Gold Tier)

After mastering Silver:

1. **Odoo Accounting Integration** - Self-hosted ERP
2. **WhatsApp Watcher** - Playwright-based monitoring
3. **Facebook/Instagram Integration** - Social posting
4. **Twitter (X) Integration** - Auto-posting
5. **Ralph Wiggum Loop** - Autonomous multi-step completion
6. **Weekly CEO Briefing** - Automated business audit

---

## 🆘 Support

- **Hackathon Meetings:** Wednesdays 10:00 PM PKT
- **Zoom:** [Link in main document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- **YouTube:** https://www.youtube.com/@panaversity

---

*AI Employee v0.2 (Silver Tier) | Created: 2026-03-18*
