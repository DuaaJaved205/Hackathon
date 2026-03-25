# LinkedIn Automation - Complete Guide

**AI Employee Silver Tier - LinkedIn Integration**

---

## 🎯 Overview

Complete LinkedIn automation for the AI Employee system, including:
- **LinkedIn Watcher** - Monitor notifications and messages
- **LinkedIn Poster** - Auto-post content with approval workflow
- **Session Management** - Persistent login for automation

---

## 📋 What's Automated vs Manual

### ✅ Fully Automated

| Task | How It Works |
|------|--------------|
| **LinkedIn Login** | Session saved after first login, auto-reused |
| **Browser Launch** | Opens automatically via Playwright |
| **Navigation** | Goes to LinkedIn feed/notifications/messages |
| **Monitoring** | Checks every 5 minutes for new activity |
| **Keyword Filtering** | Filters by priority (high/medium/low) |
| **Action File Creation** | Creates .md files in Needs_Action/ |
| **Post Publishing** | Posts content automatically (after approval) |
| **Logging** | Saves action logs automatically |

### ⚠️ Requires Manual Setup (One-Time)

| Task | How To Do It | Frequency |
|------|--------------|-----------|
| **Initial LinkedIn Login** | Run `linkedin_login.py` and login | Once only |
| **Install Dependencies** | `pip install playwright` + `playwright install chromium` | Once only |

### 🔒 Human-in-the-Loop (HITL)

| Mode | Description | When to Use |
|------|-------------|-------------|
| **Approval Mode** | Creates approval file, waits for human review | Business posts, important announcements |
| **Auto-Post Mode** | Posts immediately without approval | Quick posts, testing |

---

## 🗂️ File Structure

```
AI_Employee_Vault/
├── scripts/
│   ├── linkedin_watcher.py      # Monitor notifications/messages
│   ├── linkedin_poster.py       # Post to LinkedIn
│   └── linkedin_login.py        # First-time login helper
├── .cache/
│   └── linkedin_session/        # Saved login session
│       └── storage.json
├── Needs_Action/
│   └── LINKEDIN_*.md           # Action files from watcher
├── Pending_Approval/
│   └── LINKEDIN_POST_*.md      # Posts awaiting approval
├── Approved/
│   └── LINKEDIN_POST_*.md      # Approved posts ready to publish
├── Done/
│   └── LINKEDIN_POST_*.md      # Published posts
└── Logs/
    └── linkedin_YYYY-MM-DD.json # Activity logs
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Step 2: First-Time Login (One-Time Setup)

```bash
cd AI_Employee_Vault
python scripts/linkedin_login.py .
```

**What happens:**
1. Browser opens (visible)
2. Navigate to LinkedIn login
3. **You login manually**
4. Session saved to `.cache/linkedin_session/`
5. Browser closes

**✅ Done!** Never need to login again (unless session expires).

### Step 3: Start LinkedIn Watcher

```bash
# Monitor LinkedIn every 5 minutes (300 seconds)
python scripts/linkedin_watcher.py . 300
```

**Or start all watchers:**
```bash
python scripts/orchestrator.py . all
```

---

## 🔍 LinkedIn Watcher - How It Works

### Complete Flow

```
1. Opens Chromium browser (headless)
        ↓
2. Navigates to LinkedIn.com
        ↓
3. Loads saved session (auto-login)
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

### Code Flow

```python
# Initialize watcher
watcher = LinkedInWatcher(
    vault_path=".",
    check_interval=300  # 5 minutes
)

# Launch browser
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="./.cache/linkedin_session",  # Saves session
        headless=True,  # Background operation
        args=['--disable-blink-features=AutomationControlled']  # Avoid detection
    )
    
    page = browser.pages[0]
    page.goto('https://www.linkedin.com/feed/')
    
    # Check notifications and messages
    notifications = check_notifications(page)
    messages = check_messages(page)
    
    # Filter by keywords and create action files
    for item in notifications + messages:
        if item['priority'] != 'low':
            create_action_file(item)
```

### Keyword Filtering

```python
keywords = {
    'high': ['hiring', 'opportunity', 'interview', 'job', 'position', 'contract'],
    'medium': ['connection', 'message', 'comment', 'post', 'share'],
    'low': ['like', 'view', 'follower']
}
```

**Priority Examples:**

| Text | Priority | Why |
|------|----------|-----|
| "Hiring: Senior Developer" | 🔴 High | Contains "hiring" |
| "New job opportunity at Google" | 🔴 High | Contains "opportunity", "job" |
| "Jane wants to connect" | 🟡 Medium | Contains "connection" |
| "John commented on your post" | 🟡 Medium | Contains "comment", "post" |
| "Someone liked your post" | ⚪ Low | Only "like" - ignored |

### Action File Format

**Example: `LINKEDIN_MESSAGE_20260320_120000.md`**

```markdown
---
type: linkedin_message
source: LinkedIn
received: 2026-03-20T12:00:00
priority: high
status: pending
---

# LinkedIn Message

**Received:** 2026-03-20 12:00:00
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

## 📝 LinkedIn Poster - How It Works

### Posting Methods

#### Method 1: Auto-Post (Instant, No Approval)

```bash
# Post custom text
python scripts/linkedin_poster.py . --auto-post --post "Your post content here"

# Post with hashtags
python scripts/linkedin_poster.py . --auto-post --post "Your content" --hashtags "#AI #Tech"

# AI-generated content from topic
python scripts/linkedin_poster.py . --auto-post --topic "AI Employee Launch" --tone enthusiastic

# Generate + hashtags
python scripts/linkedin_poster.py . --auto-post --topic "Business Update" --tone professional --hashtags "#Business #Growth"
```

**What happens:**
1. Browser opens (visible)
2. Logs into LinkedIn automatically
3. Clicks "Start a post"
4. Types content
5. Clicks "Post"
6. ✅ **Post published!**

**Time:** ~30-60 seconds

---

#### Method 2: Approval Workflow (HITL - Recommended)

**Step 1: Create Approval Request**

```bash
# Create post (creates approval file)
python scripts/linkedin_poster.py . --post "Your business post content"
```

**Output:**
```
✅ Approval request created: Pending_Approval/LINKEDIN_POST_20260320_120000.md
Move to Approved/ to publish
```

**Step 2: Review & Approve (Manual)**

1. Open Obsidian
2. Go to `Pending_Approval/` folder
3. Open: `LINKEDIN_POST_*.md`
4. Review content
5. **Move file to `Approved/` folder**

**Step 3: Publish**

```bash
python scripts/linkedin_poster.py . --process-approved
```

**Output:**
```
✅ Processed 1 post(s)
Post submitted!
```

---

### Post Tone Options

When using `--topic`, specify the tone:

| Tone | Use Case | Example |
|------|----------|---------|
| `professional` | Business updates, announcements | "We are pleased to announce..." |
| `casual` | Informal updates, team culture | "Hey LinkedIn fam! Quick update..." |
| `enthusiastic` | Exciting news, launches | "🎉 BIG NEWS! We're thrilled..." |

**Example:**
```bash
python scripts/linkedin_poster.py . --auto-post --topic "Product Launch" --tone enthusiastic
```

**Generated Post:**
```
🎉 BIG NEWS! 🎉

We're absolutely thrilled to announce Product Launch!

This is a game-changer and we couldn't be more excited to share this with you all!

Stay tuned for more updates! 🚀

#Innovation #Tech #ProductLaunch
```

---

## 🔄 Complete Workflow Examples

### Example 1: Monitor LinkedIn + Reply to Message

```
1. LinkedIn Watcher detects message
   → "Hi! Interested in job opportunity..."
        ↓
2. Creates action file
   → Needs_Action/LINKEDIN_MESSAGE_*.md
        ↓
3. Qwen processes file
   → Checks Company_Handbook.md
        ↓
4. Creates Plan.md
   → Plans/LINKEDIN_MESSAGE_Plan.md
        ↓
5. Creates approval request
   → Pending_Approval/LINKEDIN_REPLY_*.md
        ↓
6. Human approves (move to Approved/)
        ↓
7. LinkedIn Poster sends reply
   → Post published
        ↓
8. Moves to Done/
```

---

### Example 2: Business Announcement Post

```bash
# Create approval request
python scripts/linkedin_poster.py . --post "Excited to announce our new AI Employee Silver Tier!

Key features:
✅ Gmail integration
✅ LinkedIn automation
✅ Multi-platform support

#AI #Automation #Business"

# In Obsidian:
# 1. Review file in Pending_Approval/
# 2. Move to Approved/
# 3. Run:
python scripts/linkedin_poster.py . --process-approved
```

---

### Example 3: AI-Generated Content

```bash
# Let AI generate post about "Product Launch"
python scripts/linkedin_poster.py . --auto-post --topic "Product Launch" --tone enthusiastic --hashtags "#Innovation #Tech"
```

---

## 🔧 Command Reference

### Posting Commands

```bash
# Auto-post custom text (instant)
python scripts/linkedin_poster.py . --auto-post --post "Your content"

# Auto-post from topic (AI generates)
python scripts/linkedin_poster.py . --auto-post --topic "Topic" --tone professional

# Add hashtags
python scripts/linkedin_poster.py . --auto-post --post "Content" --hashtags "#Tag1 #Tag2"

# Create approval request (HITL)
python scripts/linkedin_poster.py . --post "Your content"

# Process approved posts
python scripts/linkedin_poster.py . --process-approved

# Show help
python scripts/linkedin_poster.py . --help
```

### Monitoring Commands

```bash
# Start LinkedIn watcher (monitors notifications)
python scripts/linkedin_watcher.py . 300

# Check every 2 minutes (120 seconds)
python scripts/linkedin_watcher.py . 120

# Check every 10 minutes (600 seconds)
python scripts/linkedin_watcher.py . 600
```

### Login Commands

```bash
# First-time login (opens visible browser)
python scripts/linkedin_login.py .

# Clear session (force re-login)
rmdir /s /q .cache\linkedin_session
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

### Change Browser Behavior

Edit `linkedin_poster.py`:

```python
# Line ~130: Change headless mode
headless=False,  # Visible browser (recommended for debugging)
# OR
headless=True,   # Invisible browser (production)
```

### Customize Post Templates

Edit `generate_post_content()` function in `linkedin_poster.py`:

```python
templates = {
    'professional': """🚀 Exciting update from our team!

We're making great progress on {topic}.

Key highlights:
✅ Innovation in action
✅ Delivering value

#Business #Innovation""",

    'casual': """Hey LinkedIn fam! 👋

Working on something cool: {topic}

Stay tuned!

#StartupLife""",

    'enthusiastic': """🎉 BIG NEWS! 🎉

Thrilled to announce {topic}!

This is amazing! 🚀

#Exciting #Growth"""
}
```

---

## 🛠️ Troubleshooting

### Issue: "Not logged in"

**Solution:**
```bash
# Clear old session
rmdir /s /q .cache\linkedin_session

# Re-run login
python scripts/linkedin_login.py .
```

---

### Issue: "Post button not found"

**Cause:** LinkedIn UI changed or page didn't load fully

**Solution:**
1. Check browser window is visible during posting
2. Ensure you're logged in to LinkedIn
3. Wait for page to fully load before posting
4. Try running again

---

### Issue: "Playwright not installed"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

---

### Issue: "Element not visible"

**Cause:** LinkedIn may have updated their UI selectors

**Solution:**
1. Open `linkedin_poster.py`
2. Update selectors in `post_content()` method
3. Or run with visible browser to debug

---

### Issue: Session expires

**Symptoms:** Browser opens to login page every time

**Solution:**
```bash
# Clear and re-login
rmdir /s /q .cache\linkedin_session
python scripts/linkedin_login.py .
```

---

## 🔒 Security & Best Practices

### Session Security

| Do | Don't |
|----|-------|
| ✅ Store session in `.cache/` | ❌ Commit `.cache/` to git |
| ✅ Use local session storage | ❌ Share session files |
| ✅ Re-login after 30 days | ❌ Use on public computers |

**Add to `.gitignore`:**
```
.cache/linkedin_session/
```

### Posting Best Practices

| Best Practice | Why |
|---------------|-----|
| Use approval workflow for business posts | Prevents mistakes |
| Review auto-generated content | Ensure accuracy |
| Don't post too frequently | Avoid rate limiting |
| Add relevant hashtags | Increase reach |
| Post during business hours | Better engagement |

### Rate Limiting

| Action | Recommended Limit |
|--------|-------------------|
| Posts per day | 3-5 |
| Posts per hour | 1 |
| Connection requests | 20/day |
| Messages | 50/day |

---

## 📊 Monitoring & Logs

### Check Post History

```bash
# View today's logs
type Logs\linkedin_2026-03-20.json
```

### Log Format

```json
{
  "timestamp": "2026-03-20T12:00:00",
  "file": "LINKEDIN_POST_20260320_120000.md",
  "action": "posted",
  "content_preview": "Testing AI Employee Silver Tier..."
}
```

---

## 🎯 Integration with AI Employee

### With Qwen Code

```bash
# Ask Qwen to create and post
qwen "Create a LinkedIn post about our Silver Tier launch and post it"

# Qwen will:
# 1. Generate content
# 2. Create approval file (if HITL mode)
# 3. Wait for approval
# 4. Post when approved
```

### With Watchers

```
LinkedIn Watcher → Detects notification → Creates action file →
Qwen processes → Creates response → LinkedIn Poster posts reply
```

---

## ✅ Checklist for New Users

### First-Time Setup
- [ ] Install Playwright: `pip install playwright`
- [ ] Install Chromium: `playwright install chromium`
- [ ] Run login helper: `python scripts/linkedin_login.py .`
- [ ] Login to LinkedIn in browser
- [ ] Verify session saved: `.cache/linkedin_session/` exists

### Before Each Post
- [ ] Decide: Auto-post or Approval mode?
- [ ] Prepare content or topic
- [ ] Choose tone (professional/casual/enthusiastic)
- [ ] Add hashtags if needed

### After Posting
- [ ] Check LinkedIn to verify post published
- [ ] Review logs in `Logs/` folder
- [ ] Monitor engagement on LinkedIn

---

## 🚀 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│              LINKEDIN POSTING QUICK REFERENCE               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FIRST TIME:                                                │
│  python scripts/linkedin_login.py .                         │
│                                                             │
│  AUTO-POST (Instant):                                       │
│  python scripts/linkedin_poster.py . --auto-post --post "…" │
│                                                             │
│  AI-GENERATED POST:                                         │
│  python scripts/linkedin_poster.py . --auto-post \          │
│    --topic "Topic" --tone professional                      │
│                                                             │
│  WITH HASHTAGS:                                             │
│  python scripts/linkedin_poster.py . --auto-post \          │
│    --post "…" --hashtags "#AI #Tech"                        │
│                                                             │
│  APPROVAL MODE (HITL):                                      │
│  1. python scripts/linkedin_poster.py . --post "…"          │
│  2. Move file from Pending_Approval/ to Approved/           │
│  3. python scripts/linkedin_poster.py . --process-approved  │
│                                                             │
│  MONITORING:                                                │
│  python scripts/linkedin_watcher.py . 300                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📞 Support

| Issue | Solution |
|-------|----------|
| Login fails | Check credentials, clear session, re-login |
| Post not publishing | Check browser visible, review error logs |
| Selectors not working | LinkedIn UI may have changed, update selectors |
| Session keeps expiring | Check if being logged out elsewhere |

---

*Generated: 2026-03-21*
*AI Employee v0.9 (Silver Tier - LinkedIn Integration)*
