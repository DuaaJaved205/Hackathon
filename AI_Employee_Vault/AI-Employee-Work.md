# How the AI Employee Works - Step-by-Step Guide

Let me walk you through the complete workflow with exact commands.

---

## 🎯 System Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   WATCHERS      │────▶│  NEEDS_ACTION    │────▶│   CLAUDE CODE   │
│ (Python scripts)│     │   (Folder)       │     │  (Reasoning)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│     DONE/       │◀────│   APPROVAL       │◀────│   MCP SERVERS   │
│  (Completed)    │     │  (Human Review)  │     │    (Actions)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## 📋 Step 1: Install Python Dependencies

**Why:** The watcher scripts need Python libraries to monitor files.

```bash
cd "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault\scripts"
pip install watchdog
```

**What this does:**
- `watchdog` - Library that watches folders for new files (event-driven, no polling)

---

## 📋 Step 2: Start the File Watcher

**Why:** The watcher runs in the background, waiting for files to drop into the Inbox folder.

```bash
cd "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"
python scripts/filesystem_watcher.py "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"
```

**What you'll see:**
```
2026-03-18 10:00:00 - FilesystemWatcher - INFO - Starting FilesystemWatcher
2026-03-18 10:00:00 - FilesystemWatcher - INFO - Drop folder: ...\AI_Employee_Vault\Inbox\Drop
2026-03-18 10:00:00 - FilesystemWatcher - INFO - File watcher started. Waiting for files...
```

**Keep this terminal open** - the watcher runs continuously until you press `Ctrl+C`.

---

## 📋 Step 3: Test by Dropping a File

**Why:** This triggers the watcher to create an action file.

**Action:** Copy any file (PDF, TXT, DOCX, etc.) into:
```
C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault\Inbox\Drop\
```

**What happens automatically:**
1. Watcher detects the new file
2. Creates a `.md` action file in `Needs_Action/`
3. Logs the event

**Example output:**
```
2026-03-18 10:05:00 - FilesystemWatcher - INFO - New file detected: invoice.pdf
2026-03-18 10:05:00 - FilesystemWatcher - INFO - Created action file: FILE_20260318_100500_invoice.pdf.md
```

---

## 📋 Step 4: Open Obsidian (Optional but Recommended)

**Why:** Obsidian gives you a visual interface to see files being created and processed.

1. Open Obsidian
2. **File → Open Folder**
3. Select: `C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault`

You'll now see:
- `Dashboard.md` - Your main view
- `Needs_Action/` - New action files appear here
- `Company_Handbook.md` - Rules for the AI

---

## 📋 Step 5: Run Qwen Code to Process Files

**Why:** Qwen reads the action files, thinks about what needs to be done, and creates plans.

Open a **new terminal** (keep watcher running in the first one):

```bash
cd "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"
qwen
```

**Then type this prompt:**
```
I have files in Needs_Action folder. Please:
1. Read all files in Needs_Action/
2. For each file, understand what action is needed
3. Check Company_Handbook.md for rules on how to handle this
4. Create a plan in Plans/ folder if it's multi-step
5. If approval is needed, create a file in Pending_Approval/
6. Move completed items to Done/
7. Update Dashboard.md with what you did
```

**What Qwen will do:**
1. Read each action file
2. Apply rules from Company_Handbook.md
3. Create plans, request approvals, or complete tasks
4. Log all actions

---

## 📋 Step 6: Review and Approve (Human-in-the-Loop)

**Why:** Sensitive actions require your approval before executing.

If Claude needs approval, it creates a file like:
```
Pending_Approval/REVIEW_invoice_2026-03-18.md
```

**Your action:**
1. Read the file in Obsidian
2. If you approve: Move file to `Approved/` folder
3. If you reject: Move file to `Rejected/` folder

**Then tell Claude:**
```
Check the Approved/ folder and execute the approved actions.
```

---

## 📋 Step 7: Mark Tasks Complete

**Why:** Moving files to `Done/` tracks completion and updates the Dashboard.

After Claude processes everything, tell it:
```
Move all processed items from Needs_Action/ to Done/ and update the Dashboard.
```

---

## 🔄 Complete Workflow Example

Here's a real scenario end-to-end:

### Scenario: Process an Invoice File

```bash
# Terminal 1 - Start watcher (keep running)
cd "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"
python scripts/filesystem_watcher.py "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"

# Terminal 2 - Drop a file
copy "C:\Users\Haya Javed\Downloads\invoice_march.pdf" "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault\Inbox\Drop\"

# Watcher output (Terminal 1):
# New file detected: invoice_march.pdf
# Created action file: FILE_20260318_100500_invoice_march.pdf.md

# Terminal 3 - Run Qwen
cd "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"
qwen

# Qwen prompt:
"Process the new file in Needs_Action. Identify what type of document it is,
extract key information, and tell me what actions should be taken.
Check Company_Handbook.md for financial document rules."
```

---

## 🎮 Quick Command Reference

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `pip install watchdog` | Installs file monitoring library | First-time setup |
| `python scripts/filesystem_watcher.py <vault_path>` | Starts file watcher | Always run first (keep running) |
| `cd <vault_path> && qwen` | Starts Qwen Code | When you need to process files |
| `copy <file> Inbox\Drop\` | Drops file for processing | When you have files to process |

---

## 🔍 What Each Folder Does

| Folder | Purpose |
|--------|---------|
| `Inbox/Drop/` | Drop files here - watcher picks them up |
| `Needs_Action/` | Auto-created action files wait here |
| `Plans/` | Claude creates multi-step plans here |
| `Pending_Approval/` | Actions waiting for your OK |
| `Approved/` | Move files here to approve |
| `Rejected/` | Move files here to reject |
| `Done/` | Completed tasks |
| `Briefings/` | CEO reports (weekly summaries) |
| `Logs/` | Audit trail of all actions |

---

## 💡 Pro Tips

1. **Keep watcher running** - Start it once, minimize the terminal
2. **Batch process** - Drop multiple files, then run Claude once
3. **Check Dashboard.md** - Always shows current status
4. **Review Company_Handbook.md** - Understand the rules Claude follows
5. **Use Obsidian** - Visual file management is easier than command line

---

## 🚨 Troubleshooting

**Watcher not detecting files?**
```bash
# Verify watcher is running - you should see log output
# Check the Drop folder path is correct
dir "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault\Inbox\Drop"
```

**Qwen not found?**
```bash
# Qwen Code should be available in your environment
# If using Qwen Code CLI, ensure it's installed
qwen --version
```

**Need to stop watcher?**
```bash
# In the watcher terminal, press Ctrl+C
```
