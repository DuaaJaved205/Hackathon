# AI Employee - Gmail Silver Tier

**Autonomous Gmail Processing with Human-in-the-Loop Approval**

A fully automated AI employee system that processes Gmail emails, drafts replies, and sends them with human approval.

---

## 🎯 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Silver-Tier-Final
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r AI_Employee_Vault/scripts/requirements.txt

# Playwright (for browser automation)
playwright install chromium
```

### 3. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`
6. Place in project root: `Silver-Tier-Final/credentials.json`

### 4. Start Automation

```bash
cd AI_Employee_Vault
python scripts/auto_orchestrator.py
```

---

## 🔄 Workflow

```
Email Arrives → Auto-Detected (120s) → Qwen Processes → 
Creates Approval Request → YOU Approve → Auto-Send (120s)
```

### What's Automatic:
- ✅ Gmail monitoring (every 120 seconds)
- ✅ Email detection and action file creation
- ✅ Qwen processing with -y flag
- ✅ Plan.md creation
- ✅ Approval request creation
- ✅ Email sending (after approval)
- ✅ File cleanup (deletes processed files)
- ✅ Dashboard updates

### What's Manual:
- ⚠️ Review approval requests in Obsidian
- ⚠️ Move from `Pending_Approval/` to `Approved/`

---

## 📁 Project Structure

```
Silver-Tier-Final/
├── AI_Employee_Vault/
│   ├── scripts/
│   │   ├── auto_orchestrator.py    # Main automation
│   │   ├── gmail_watcher.py        # Gmail monitoring
│   │   ├── gmail_sender.py         # Email sending
│   │   └── ...
│   ├── Needs_Action/               # New emails
│   ├── Pending_Approval/           # Awaiting approval
│   ├── Approved/                   # Ready to send
│   ├── Done/                       # Completed
│   ├── Plans/                      # Qwen plans
│   └── Logs/                       # Audit logs
├── credentials.json                # Gmail OAuth (YOU ADD THIS)
├── workflow.md                     # Complete guide
├── fix-gmail-quick.bat             # Quick fix script
└── README.md                       # This file
```

---

## 🛠️ Troubleshooting

### "No New Emails" But Email Exists

**Quick Fix:**
```bash
# Run in NEW terminal (doesn't stop orchestrator)
fix-gmail-quick.bat

# Or manually:
del scripts\token.json
del .cache\GmailWatcher_processed.txt
python scripts/gmail_watcher.py . 10
```

### Permission Errors

```
Error: 403 Insufficient Permissions
```

**Fix:** Delete token and re-authenticate
```bash
del scripts\token.json
python scripts/gmail_watcher.py . 10
```

---

## 📋 Commands Reference

| Command | Purpose |
|---------|---------|
| `python scripts/auto_orchestrator.py` | Start full automation |
| `fix-gmail-quick.bat` | Re-authenticate Gmail |
| `python scripts/gmail_sender.py . --process-approved` | Send approved emails |
| `python scripts/test_orchestrator.py` | Run test suite |

---

## 🔒 Security

**NEVER commit these files:**
- `credentials.json` - OAuth credentials
- `scripts/token.json` - OAuth token
- `.cache/` - Session cache
- `Logs/` - May contain sensitive data

All sensitive files are in `.gitignore`.

---

## 📚 Documentation

- **workflow.md** - Complete workflow guide
- **AI_Employee_Vault/README.md** - Vault-specific docs
- **Personal AI Employee Hackathon 0_...md** - Full architectural blueprint

---

## 🤝 Contributing

This is a hackathon project. Feel free to:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🆘 Support

- **Documentation:** See `workflow.md`
- **Issues:** Open a GitHub issue
- **Hackathon Meetings:** Wednesdays 10:00 PM PKT

---

*Created: 2026-03-20*
*AI Employee v0.9 (Silver Tier - Production Ready)*
