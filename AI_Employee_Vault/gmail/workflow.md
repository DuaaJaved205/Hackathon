# Gmail Silver Tier - Complete Workflow Guide

## 🎯 ONE Command to Start Everything

```bash
cd "C:\Users\Haya Javed\Downloads\Silver-Tier-Final\AI_Employee_Vault"
python scripts/auto_orchestrator.py
```

**Run this ONCE** - then everything is automatic except your approval.

---

## ✅ What's AUTOMATIC (Done by System)

| # | Step | What Happens | Time |
|---|------|--------------|------|
| 1 | **Gmail Monitoring** | Checks Gmail every 120 seconds | Continuous |
| 2 | **Email Detection** | Creates `EMAIL_*.md` in `Needs_Action/` | Within 120s |
| 3 | **Qwen Processing** | Runs automatically with `-y` flag | Immediate |
| 4 | **Plan Creation** | Creates `Plans/Plan_*.md` for each email | Automatic |
| 5 | **Approval Request** | Creates `Pending_Approval/EMAIL_REPLY_*.md` | Automatic |
| 6 | **Approval Detection** | Checks `Approved/` folder every 120 seconds | Continuous |
| 7 | **Email Sending** | Sends emails via Gmail API | Within 120s of approval |
| 8 | **File Cleanup** | Moves files to `Done/` | Automatic |
| 9 | **Dashboard Update** | Updates `Dashboard.md` with status | Automatic |

---

## ⚠️ What's MANUAL (Your Task)

| # | Step | What You Do | When |
|---|------|-------------|------|
| 1 | **Review Approval** | Open Obsidian, check `Pending_Approval/` | When notified |
| 2 | **Approve/Reject** | Move file to `Approved/` or `Rejected/` | After review |

**That's the ONLY thing you do!**

---

## 🔄 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  YOU (ONE TIME):                                            │
│  python scripts/auto_orchestrator.py                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (AUTOMATIC - runs continuously)
┌─────────────────────────────────────────────────────────────┐
│  1. Gmail Watcher checks inbox every 120 seconds            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (when email arrives)
┌─────────────────────────────────────────────────────────────┐
│  2. EMAIL_*.md created in Needs_Action/                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (AUTOMATIC - within same cycle)
┌─────────────────────────────────────────────────────────────┐
│  3. Qwen runs with -y flag                                  │
│     - Creates Plans/Plan_*.md                               │
│     - Creates Pending_Approval/EMAIL_REPLY_*.md             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (WAITING FOR YOU)
┌─────────────────────────────────────────────────────────────┐
│  4. YOUR TASK:                                              │
│     - Open Obsidian                                         │
│     - Go to Pending_Approval/ folder                        │
│     - Review EMAIL_REPLY_*.md files                         │
│     - Move to Approved/ to send                             │
│     - Move to Rejected/ to reject                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (AUTOMATIC - within 120 seconds)
┌─────────────────────────────────────────────────────────────┐
│  5. Auto Orchestrator detects files in Approved/            │
│     - Runs: python scripts/gmail_sender.py                 │
│       --process-approved                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (AUTOMATIC)
┌─────────────────────────────────────────────────────────────┐
│  6. Gmail Sender sends emails                               │
│     - Uses Gmail API                                        │
│     - Logs to Logs/gmail_*.json                             │
│     - Moves files to Done/                                  │
│     - Updates Dashboard.md                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📬 How Email Sending Works

### The Detection Mechanism

**Auto Orchestrator polls the `Approved/` folder every 120 seconds:**

```python
# In auto_orchestrator.py (runs every 120 seconds)
def process_approved_emails(self):
    # Check Approved/ folder for EMAIL_REPLY_*.md files
    approved_files = list(self.approved_folder.glob('EMAIL_REPLY_*.md'))
    
    if approved_files:
        # Found approved emails! Send them
        for file in approved_files:
            send_email(file)
```

### File Flow

```
Step 1: Qwen creates approval request
        Pending_Approval/EMAIL_REPLY_20260320_191624.md
        
Step 2: YOU move file to Approved/
        Approved/EMAIL_REPLY_20260320_191624.md
        ↑
        Auto Orchestrator detects this within 120 seconds
        
Step 3: Auto Orchestrator runs gmail_sender.py
        python scripts/gmail_sender.py --process-approved
        
Step 4: Gmail Sender reads all files in Approved/
        - Extracts sender email from "From:" field
        - Sends reply to original sender
        - Logs to Logs/gmail_*.json
        - Moves file to Done/
```

### Email Reply Logic

**Important:** Replies are sent to the **original sender**, not the recipient!

```
Original Email:
  From: John <john@example.com>
  To:   you@company.com
  
Reply Email (automatic):
  To:   john@example.com  ← Replies to original sender
  From: you@company.com
```

The approval file format ensures this:
```markdown
**From:** John <john@example.com>  ← System replies to this email
**To:** you@company.com             ← For reference only
```

---

## 📋 Step-by-Step Instructions

### Step 1: Start Automation (ONE TIME)

```bash
cd "C:\Users\Haya Javed\Downloads\Silver-Tier-Final\AI_Employee_Vault"
python scripts/auto_orchestrator.py
```

**Keep this terminal open** - it runs continuously.

**Expected Output:**
```
======================================================================
                      AUTO ORCHESTRATOR STARTED
======================================================================

✅ Gmail Watcher: Running (120 second interval)
✅ Qwen Processing: Automatic (with -y flag)
✅ Email Sending: Automatic after approval
⚠️  Your ONLY Task:
⚠️    Move approval requests from Pending_Approval/ to Approved/

=== Iteration 1 ===
Found 2 new email(s) to process
Created prompt file: qwen_prompt_20260320_203000.txt
Running Qwen with -y flag for automatic processing...
✅ Qwen processing complete!
📁 Approvals pending: 2
👉 Check Pending_Approval/ folder in Obsidian
```

---

### Step 2: Review & Approve (YOUR TASK)

**When you see "Approvals pending: X" in the logs:**

1. **Open Obsidian**
2. **Navigate to:** `Pending_Approval/` folder
3. **Open each file:** `EMAIL_REPLY_*.md`
4. **Review the drafted reply**
5. **Decide:**
   - ✅ **Approve:** Drag file to `Approved/` folder
   - ❌ **Reject:** Drag file to `Rejected/` folder

**That's it!** The system takes over from here.

---

### Step 3: Automatic Sending (HAPPENS AUTOMATICALLY)

**Within 120 seconds of moving file to `Approved/`:**

Auto Orchestrator will log:
```
=== Iteration 2 ===
✅ Sent 2 email(s)
Dashboard updated
```

**Check `Done/` folder** - files should be there.

---

## 🔍 Monitoring

### Check What's Happening

**Watch the terminal output:**
```
=== Iteration 1 ===
Found 2 new email(s) to process          ← New emails detected
✅ Qwen processing complete!              ← Plans + Approvals created
📁 Approvals pending: 2                   ← Waiting for your approval
👉 Check Pending_Approval/ folder         ← YOUR TASK!

=== Iteration 2 ===
No new emails                             ← No new emails
✅ Sent 2 email(s)                        ← Your approvals were sent!
Dashboard updated                         ← Status updated
```

### Check Folders in Obsidian

| Folder | What to Look For |
|--------|------------------|
| `Needs_Action/` | New emails appear here (auto-created) |
| `Pending_Approval/` | Approval requests appear here (auto-created) |
| `Approved/` | Should be empty (you move files here, then they're sent) |
| `Done/` | Completed emails accumulate here |

---

## 🛑 Stopping

**Press `Ctrl+C`** in the terminal window.

---

## 🛠️ Troubleshooting

### ⚠️ "No New Emails" But You Sent an Email

**Symptom:** Orchestrator shows "No new emails" but you know an email arrived.

**Cause:** OAuth token has wrong permissions or Gmail cache is stale.

**QUICK FIX - Use the fix script:**

```bash
# Double-click this file:
fix-gmail-auth.bat

# Or run manually:
cd "C:\Users\Haya Javed\Downloads\Silver-Tier-Final"
fix-gmail-auth.bat
```

**The script will:**
1. Stop the orchestrator
2. Delete old OAuth token
3. Delete Gmail cache
4. Open browser for re-authentication
5. Restart Auto Orchestrator

**MANUAL FIX:**

```bash
# Step 1: Stop the orchestrator (Ctrl+C)

# Step 2: Delete old OAuth token
del scripts\token.json

# Step 3: Delete Gmail cache
del .cache\GmailWatcher_processed.txt

# Step 4: Run Gmail Watcher (opens browser for authentication)
python scripts/gmail_watcher.py . 10

# Step 5: Complete OAuth in browser
# - Browser opens automatically
# - Sign in to Google
# - Grant permissions
# - Token saved

# Step 6: Restart Auto Orchestrator
python scripts/auto_orchestrator.py
```

**Expected Output:**
```
GmailWatcher - INFO - Loaded existing OAuth token
GmailWatcher - INFO - Gmail service initialized
GmailWatcher - INFO - Found 1 new message(s)
GmailWatcher - INFO - Created action file: EMAIL_*.md
```

**AUTOMATIC DETECTION:**

The Auto Orchestrator now automatically detects permission errors and will show:

```
⚠️  GMAIL PERMISSION ERROR DETECTED!
⚠️  To fix, run these commands:
⚠️    del scripts\token.json
⚠️    python scripts/gmail_watcher.py . 10
```

---

### Approval Requests Not Appearing

**Wait for Qwen to complete** (can take 30-60 seconds)

**Check logs:**
```bash
type Logs\qwen_*.log
```

**If still nothing, run Qwen manually:**
```bash
qwen "@.cache\qwen_prompt_*.txt" -y
```

---

### Emails Not Sending After Approval

**Check:**
1. File is in `Approved/` (not `Pending_Approval/`)
2. Auto Orchestrator is running (check terminal)
3. Wait up to 120 seconds

**Manual send:**
```bash
python scripts/gmail_sender.py . --process-approved
```

---

### Qwen Errors

**Error:** "write_file requires user approval"

**Fix:** Make sure you're using `-y` flag:
```bash
qwen "@.cache\qwen_prompt_*.txt" -y
```

---

### Gmail Permission Errors

**Error:** "403 Insufficient Permissions"

**Fix:**
```bash
# Delete old token with wrong scope
del scripts\token.json

# Re-run watcher (creates token with gmail.modify scope)
python scripts/gmail_watcher.py . 10
```

---

## 📞 Quick Commands

| Command | Purpose |
|---------|---------|
| `python scripts/auto_orchestrator.py` | **Start full automation** |
| `qwen "@.cache\qwen_prompt_*.txt" -y` | Process emails manually |
| `python scripts/gmail_sender.py . --process-approved` | Send approved emails |
| `python scripts/test_orchestrator.py` | Run test suite |
| `del scripts\token.json` | Reset OAuth (fix permission errors) |
| `python scripts/gmail_watcher.py . 10` | Re-authenticate Gmail |
| `Ctrl+C` | Stop orchestrator |

---

## 🎉 Summary

### What You Do (2 steps):
1. **Start:** `python scripts/auto_orchestrator.py` (once)
2. **Approve:** Move files from `Pending_Approval/` to `Approved/` (when notified)

### What's Automatic (9 steps):
1. ✅ Gmail monitoring (every 120s)
2. ✅ Email detection
3. ✅ Action file creation
4. ✅ Qwen processing
5. ✅ Plan creation
6. ✅ Approval request creation
7. ✅ Approval detection (every 120s)
8. ✅ Email sending
9. ✅ Cleanup & dashboard update

---

## 🔧 Common Issues Quick Fix

| Issue | Quick Fix |
|-------|-----------|
| "No new emails" but email exists | `del scripts\token.json` then `python scripts/gmail_watcher.py . 10` |
| Approvals not appearing | Wait 60s, check `Logs\qwen_*.log` |
| Emails not sending | Check file in `Approved/`, wait 120s |
| Permission errors | Delete token.json, re-authenticate |

---

*Generated: 2026-03-20*
*AI Employee v0.8 (Silver Tier - Fully Automated)*
