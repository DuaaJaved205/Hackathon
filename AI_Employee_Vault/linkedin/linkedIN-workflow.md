# 🔍 LinkedIn Watcher - Complete Working Guide

Let me explain exactly how the LinkedIn Watcher works, step by step.

---

## 📋 What LinkedIn Watcher Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    LINKEDIN WATCHER FLOW                        │
└─────────────────────────────────────────────────────────────────┘

1. Opens Chromium browser (headless)
        ↓
2. Navigates to LinkedIn.com
        ↓
3. Loads saved session (or asks you to login)
        ↓
4. Checks Notifications page
        ↓
5. Checks Messages page
        ↓
6. Filters by keywords (hiring, opportunity, message, etc.)
        ↓
7. Creates .md action file for each relevant item
        ↓
8. Saves to Needs_Action/ folder
        ↓
9. Waits 5 minutes → Repeats from step 4
```

---

## 🗂️ File Structure

```
Hackathon0/
├── AI_Employee_Vault/
│   ├── scripts/
│   │   └── linkedin_watcher.py      # Main watcher script
│   ├── .cache/
│   │   └── linkedin_session/
│   │       └── storage.json          # Saved login session
│   ├── Needs_Action/
│   │   └── LINKEDIN_MESSAGE_20260318_103000_john_doe.md  # Created by watcher
│   └── Logs/
│       └── linkedin_2026-03-18.log   # Activity logs
└── linkedIN-workflow.md              # This file
```

---

## 🔧 Step-by-Step Code Flow

### Step 1: Initialize Watcher

```python
# When you run: python linkedin_watcher.py . 300

watcher = LinkedInWatcher(
    vault_path=".",
    check_interval=300  # 5 minutes
)

# Sets up:
# - Session path: .cache/linkedin_session/
# - Keywords to monitor
# - URLs to check
```

---

### Step 2: Launch Browser

```python
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="./.cache/linkedin_session",  # Saves cookies
        headless=True,  # No visible browser window
        args=['--disable-blink-features=AutomationControlled']  # Avoid detection
    )
    
    page = browser.pages[0]
```

**What happens:**
- Chromium browser launches in background
- Uses persistent profile (saves login session)
- Runs headless (no visible window)
- Tries to avoid bot detection

---

### Step 3: Login Check

```python
page.goto('https://www.linkedin.com/feed/')

# If already logged in (session exists):
# → Goes directly to feed

# If not logged in (first run):
# → Redirects to login page
# → Waits for manual login (2 minutes timeout)
# → Saves session after successful login
```

**First Run:**
```
Browser opens → linkedin.com/login
You enter email/password manually
LinkedIn may send verification code
After login → Session saved to .cache/linkedin_session/storage.json
```

**Subsequent Runs:**
```
Browser opens → Auto-logged in via saved cookies
No manual intervention needed
```

---

### Step 4: Check Notifications

```python
page.goto('https://www.linkedin.com/notifications/')
page.wait_for_timeout(5000)  # Wait for content to load

# Find notification elements
notifications = page.query_selector_all('div.notification-item')

for notification in notifications[:10]:  # Last 10 notifications
    text = notification.inner_text()
    
    # Example notification text:
    # "John Doe commented on your post: Great article!"
    
    priority = get_priority(text)  # high/medium/low
    
    if priority != 'low':  # Only keep relevant items
        notifications_list.append({
            'type': 'notification',
            'text': text,
            'priority': priority
        })
```

**What gets captured:**

| Notification Type | Example | Priority |
|-------------------|---------|--------|
| Comment on post | "John commented on your post" | Medium |
| Job opportunity | "Hiring: Software Engineer" | High |
| Connection request | "Jane wants to connect" | Medium |
| Message | "You have a new message" | High |
| Like on post | "John liked your post" | Low (ignored) |
| Profile view | "Someone viewed your profile" | Low (ignored) |

---

### Step 5: Check Messages

```python
page.goto('https://www.linkedin.com/messaging/')
page.wait_for_timeout(5000)

# Find conversations
conversations = page.query_selector_all('div.conversation-item')

for conv in conversations[:5]:  # Last 5 conversations
    text = conv.inner_text()
    
    # Check if unread
    if 'unread' in text.lower():
        messages_list.append({
            'type': 'message',
            'text': text,
            'priority': 'high'  # Messages are always high priority
        })
```

---

### Step 6: Filter by Keywords

```python
keywords = {
    'high': ['hiring', 'opportunity', 'interview', 'job', 'position', 'contract'],
    'medium': ['connection', 'message', 'comment', 'post', 'share'],
    'low': ['like', 'view', 'follower']
}

def get_priority(text):
    text_lower = text.lower()
    
    for keyword in keywords['high']:
        if keyword in text_lower:
            return 'high'
    
    for keyword in keywords['medium']:
        if keyword in text_lower:
            return 'medium'
    
    return 'low'
```

**Examples:**

| Text | Priority | Why |
|------|----------|-----|
| "Hiring: Senior Developer" | High | Contains "hiring" |
| "New job opportunity at Google" | High | Contains "opportunity", "job" |
| "Jane wants to connect" | Medium | Contains "connection" |
| "John commented on your post" | Medium | Contains "comment", "post" |
| "Someone liked your post" | Low | Only "like" - ignored |

---

### Step 7: Create Action File

```python
def create_action_file(self, item):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"LINKEDIN_{item['type'].upper()}_{timestamp}.md"
    
    content = f"""---
type: linkedin_{item['type']}
source: LinkedIn
received: {datetime.now().isoformat()}
priority: {item['priority']}
status: pending
---

# LinkedIn {item['type'].title()}

**From:** {item.get('from', 'Unknown')}  
**Received:** {datetime.now()}  
**Priority:** {item['priority'].upper()}

---

## Content

{item['text']}

---

## Suggested Actions

- [ ] Reply to message
- [ ] Schedule follow-up
- [ ] Save contact information

## Notes

_Add your notes here_
"""
    
    filepath = self.needs_action / filename
    filepath.write_text(content)
    return filepath
```

**Example Output File:**

```markdown
---
type: linkedin_message
source: LinkedIn
received: 2026-03-18T22:30:00
priority: high
status: pending
---

# LinkedIn Message

**Received:** 2026-03-18 22:30:00  
**Priority:** HIGH

---

## Content

John Doe: "Hi! I saw your profile and I'm interested in discussing a job opportunity at our company. Are you available for a call this week?"

---

## Suggested Actions

- [ ] Reply to message
- [ ] Schedule follow-up
- [ ] Save contact information

## Notes

_Add your notes here_
```

---

### Step 8: Save Processed IDs

```python
# Track which items we've already processed
self.processed_ids.add(item_id)

# Save to cache file
cache_file = self.vault_path / '.cache' / 'LinkedInWatcher_processed.txt'
with open(cache_file, 'w') as f:
    for item_id in self.processed_ids:
        f.write(f"{item_id}\n")
```

**Why:** Prevents duplicate action files on next run.

---

### Step 9: Wait and Repeat

```python
while True:
    items = self.check_for_updates()
    
    for item in items:
        create_action_file(item)
    
    time.sleep(300)  # Wait 5 minutes
```

---

## 🎯 Complete Example Run

### Start Watcher

```bash
cd "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"
python scripts/linkedin_watcher.py . 300
```

### Console Output

```
2026-03-18 22:30:00 - LinkedInWatcher - INFO - Starting LinkedInWatcher
2026-03-18 22:30:00 - LinkedInWatcher - INFO - Session path: .\.cache\linkedin_session
2026-03-18 22:30:00 - LinkedInWatcher - INFO - Check interval: 300 seconds
2026-03-18 22:30:05 - LinkedInWatcher - INFO - Loaded existing session
2026-03-18 22:30:10 - LinkedInWatcher - INFO - Found 2 new LinkedIn item(s)
2026-03-18 22:30:10 - LinkedInWatcher - INFO - Created: LINKEDIN_MESSAGE_20260318_223010.md
2026-03-18 22:30:10 - LinkedInWatcher - INFO - Created: LINKEDIN_NOTIFICATION_20260318_223010.md
2026-03-18 22:35:10 - LinkedInWatcher - INFO - Checking for updates...
2026-03-18 22:35:15 - LinkedInWatcher - INFO - No new items
```

### Files Created

```
Needs_Action/
├── LINKEDIN_MESSAGE_20260318_223010.md
└── LINKEDIN_NOTIFICATION_20260318_223010.md
```

---

## 🧪 Test It Yourself

### First Run (Login Required)

```bash
cd "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"

# Start watcher
python scripts/linkedin_watcher.py . 300
```

**What happens:**
1. Browser opens in background
2. Navigates to LinkedIn
3. If first time → Waits for you to login (check terminal for URL)
4. After login → Session saved
5. Starts monitoring

### Check Results

```bash
# Open Obsidian and check:
Needs_Action/ folder → Look for LINKEDIN_*.md files
```

---

## ⚙️ Configuration Options

### Change Check Interval

```bash
# Check every 2 minutes (120 seconds)
python scripts/linkedin_watcher.py . 120

# Check every 10 minutes (600 seconds)
python scripts/linkedin_watcher.py . 600
```

**Recommended:** 300 seconds (5 minutes) - avoids rate limiting

### Customize Keywords

Edit `linkedin_watcher.py`:

```python
self.keywords = {
    'high': ['your', 'custom', 'keywords'],
    'medium': ['more', 'keywords'],
    'low': ['ignore', 'these']
}
```

---

## 🛑 Stop Watcher

```bash
# Press Ctrl+C in terminal
```

---

## 📊 What Happens After Action File is Created

```
LinkedIn Watcher → Creates LINKEDIN_*.md in Needs_Action/
        ↓
Qwen Code → Reads file when you run `qwen`
        ↓
Checks Company_Handbook.md for rules
        ↓
Creates Plan.md if multi-step
        ↓
Creates approval request if action needed
        ↓
Human approves → Action executed
        ↓
File moved to Done/
```

---

## 🔒 Security & Privacy

| Concern | How It's Handled |
|---------|------------------|
| Login credentials | Never stored - only session cookies |
| Session file | Stored locally in `.cache/` |
| Data collected | Only notifications/messages with keywords |
| Rate limiting | 5-minute minimum interval |
| Bot detection | Uses stealth flags to avoid detection |

---

## ❓ FAQ

**Q: Do I need to stay logged in?**  
A: No - session is saved after first login.

**Q: Will LinkedIn ban my account?**  
A: Use at your own risk. The watcher is passive (read-only) and runs infrequently to avoid detection.

**Q: Can it auto-reply to messages?**  
A: No - it only monitors. Replies require Qwen + HITL approval + LinkedIn Poster.

**Q: What if session expires?**  
A: Watcher will notify you. Re-run and login again.

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `scripts/linkedin_watcher.py` | Main watcher script |
| `scripts/linkedin_poster.py` | Post to LinkedIn (with approval) |
| `.qwen/skills/linkedin-poster/SKILL.md` | Skill documentation |
| `SILVER_TIER_README.md` | Complete Silver Tier setup |

---

## 🚀 Quick Commands Reference

```bash
# Start LinkedIn watcher
python scripts/linkedin_watcher.py . 300

# Start all watchers (Gmail + LinkedIn + File)
python scripts/orchestrator.py . all

# Create a LinkedIn post (requires approval)
python scripts/linkedin_poster.py . --topic "Your Topic" --tone professional

# Process approved posts
python scripts/linkedin_poster.py . --process-approved

# Clear LinkedIn session (force re-login)
rmdir /s /q .cache\linkedin_session
```

---

*Generated: 2026-03-18*  
*AI Employee v0.2 (Silver Tier)*
