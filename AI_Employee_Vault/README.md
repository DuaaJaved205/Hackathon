# AI Employee Vault - Bronze Tier

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

This is your **Personal AI Employee** Obsidian vault - a complete system for automating personal and business tasks using Qwen Code as the reasoning engine.

---

## 📋 Quick Start

### 1. Open in Obsidian

```bash
# Open this vault in Obsidian
# File → Open Folder → Select AI_Employee_Vault
```

### 2. Install Python Dependencies

```bash
cd scripts
pip install watchdog
# Optional (for Gmail watcher):
# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. Start the File Watcher

```bash
# Start the file system watcher (watches for dropped files)
python filesystem_watcher.py /path/to/AI_Employee_Vault
```

### 4. Open Qwen Code

```bash
# Navigate to vault and start Qwen
cd /path/to/AI_Employee_Vault
qwen
```

### 5. Test the System

1. Drop a file into `Inbox/Drop/` folder
2. Watcher creates action file in `Needs_Action/`
3. Qwen processes the file and creates plans
4. Move completed items to `Done/`

---

## 📁 Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Main dashboard - start here!
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1 2026 objectives
├── Inbox/
│   └── Drop/                 # Drop files here for processing
├── Needs_Action/             # Pending tasks (auto-created by watchers)
├── In_Progress/              # Tasks being worked on
├── Pending_Approval/         # Awaiting human decision
├── Approved/                 # Approved actions
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Plans/                    # Multi-step task plans
├── Briefings/                # CEO briefings
├── Logs/                     # Action logs
├── Updates/                  # Sync updates (for cloud tier)
├── Signals/                  # Cross-agent signals
├── Accounting/               # Financial records
└── scripts/
    ├── base_watcher.py       # Base watcher class
    ├── filesystem_watcher.py # File system watcher
    ├── gmail_watcher.py      # Gmail watcher (requires API setup)
    ├── orchestrator.py       # Master process
    └── requirements.txt      # Python dependencies
```

---

## 🤖 Available Watchers

### File System Watcher (✅ Ready to Use)

Monitors `Inbox/Drop/` folder for new files.

```bash
# Start watcher
python scripts/filesystem_watcher.py /path/to/AI_Employee_Vault

# Drop any file into Inbox/Drop/ and an action file is created automatically
```

**Use cases:**
- Process PDFs, documents, spreadsheets
- Monitor downloads folder
- Batch file processing

### Gmail Watcher (⚙️ Requires Setup)

Monitors Gmail for new unread messages.

**Setup Steps:**

1. **Enable Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Gmail API

2. **Create OAuth Credentials:**
   - APIs & Services → Credentials
   - Create Credentials → OAuth 2.0 Client ID
   - Application type: Desktop app
   - Download `credentials.json`

3. **Place Credentials:**
   ```bash
   # Move credentials.json to project root
   mv ~/Downloads/credentials.json /path/to/Hackathon0/
   ```

4. **First Run (Authorize):**
   ```bash
   python scripts/gmail_watcher.py /path/to/AI_Employee_Vault
   # Follow browser OAuth flow
   ```

5. **Ongoing Use:**
   ```bash
   python scripts/gmail_watcher.py /path/to/AI_Employee_Vault 120
   # Checks every 120 seconds
   ```

---

## 🧠 Using Qwen Code

### Basic Processing

```bash
# Navigate to vault
cd /path/to/AI_Employee_Vault

# Start Qwen
qwen

# Or start with specific prompt
qwen "Process all files in Needs_Action folder"
```

### Ralph Wiggum Pattern (Persistence)

For autonomous multi-step task completion:

```bash
# Start Ralph loop (if available in your Qwen Code version)
/ralph-loop "Process all files in Needs_Action, move to Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

### Sample Prompts

**Process Communications:**
```
Read all files in /Needs_Action/ and for each:
1. Identify the type (email, file, message)
2. Check Company_Handbook.md for applicable rules
3. Determine priority and required actions
4. Create a Plan.md in /Plans/ if multi-step
5. Request approval in /Pending_Approval/ if sensitive
6. Move processed items to /Done/
```

**Generate CEO Briefing:**
```
Review this week's activity and create a CEO Briefing:
1. Check /Done/ for completed tasks
2. Review /Accounting/ for transactions
3. Check /Business_Goals.md for targets
4. Create briefing in /Briefings/ with:
   - Revenue summary
   - Completed tasks
   - Bottlenecks identified
   - Proactive suggestions
```

---

## ✅ Bronze Tier Checklist

Track your progress:

- [x] **Obsidian vault created** with Dashboard.md
- [x] **Company_Handbook.md** with rules of engagement
- [x] **Business_Goals.md** with Q1 objectives
- [x] **Folder structure** implemented
- [x] **One watcher working** (File System Watcher)
- [x] **Qwen Code integration** - can read/write to vault
- [ ] Gmail watcher (optional - requires API setup)
- [ ] Basic scheduling via cron/Task Scheduler

---

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Set credentials path
export GMAIL_CREDENTIALS_PATH="/path/to/credentials.json"

# Optional: Enable dry-run mode
export DRY_RUN="true"
```

### Watcher Intervals

| Watcher | Default | Recommended |
|---------|---------|-------------|
| File System | Event-driven | Event-driven |
| Gmail | 120s | 60-300s |
| WhatsApp | 30s | 30-60s |

---

## 📝 Workflow Examples

### Example 1: Process a Dropped File

1. **Drop file** into `Inbox/Drop/document.pdf`
2. **Watcher creates** `Needs_Action/FILE_20260318_document.pdf.md`
3. **Qwen reads** the action file
4. **Qwen creates** plan in `Plans/`
5. **Qwen extracts** content and creates summary
6. **You review** and move to `Done/`

### Example 2: Email Processing (Gmail)

1. **Email arrives** with subject "Invoice Request"
2. **Gmail watcher** creates action file
3. **Qwen reads** email, identifies invoice request
4. **Qwen checks** Company_Handbook for rules
5. **Qwen creates** invoice draft in `Pending_Approval/`
6. **You approve** by moving to `Approved/`
7. **Qwen sends** email (via MCP in Silver tier)

---

## 🛠️ Troubleshooting

### Watcher Not Starting

```bash
# Check Python version (need 3.13+)
python --version

# Install dependencies
pip install -r scripts/requirements.txt

# Check file permissions
ls -la scripts/
```

### Qwen Code Not Found

```bash
# Qwen Code should be available in your environment
# If using Qwen Code CLI, ensure it's installed
qwen --version
```

### Files Not Being Processed

1. Check watcher is running (should see log output)
2. Verify file dropped in correct folder (`Inbox/Drop/`)
3. Check `Needs_Action/` for action files
4. Review watcher logs for errors

---

## 📚 Key Documents

| Document | Purpose |
|----------|---------|
| [[Dashboard]] | Real-time summary of all activities |
| [[Company_Handbook]] | Rules governing AI behavior |
| [[Business_Goals]] | Quarterly objectives and metrics |

---

## 🚀 Next Steps (Silver Tier)

After mastering Bronze:

1. **Add Gmail Watcher** - Complete API setup
2. **Add WhatsApp Watcher** - Playwright-based monitoring
3. **Create MCP Server** - For sending emails
4. **Implement Approval Workflow** - Human-in-the-loop
5. **Add Scheduling** - cron/Task Scheduler integration

---

## 📞 Support

- **Hackathon Meetings:** Wednesdays 10:00 PM PKT
- **Zoom:** [Link in main document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- **YouTube:** https://www.youtube.com/@panaversity

---

## 📄 License

This project is part of the Personal AI Employee Hackathon 0.

---

*AI Employee v0.1 (Bronze Tier) | Created: 2026-03-18*
