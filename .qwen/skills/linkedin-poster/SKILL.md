---
name: linkedin-poster
description: |
  LinkedIn automation using Playwright for posting updates, articles, and engaging with content.
  Use for business promotion, lead generation, and professional networking. Requires LinkedIn
  account and approval workflow for all posts.
---

# LinkedIn Poster Skill

Automate LinkedIn posting and engagement for business growth.

## Prerequisites

### 1. Install Playwright

```bash
npm install -D playwright
playwright install chromium
```

### 2. Python Dependencies

```bash
pip install playwright
```

### 3. LinkedIn Account

- Active LinkedIn account
- Company page (optional, for business posts)
- Stable internet connection

## Architecture

```
Business_Goals.md → Content Generation → Draft Post → 
Human Approval → LinkedIn Post → Engagement Tracking
```

## Quick Start

### Post to LinkedIn

```bash
# Start LinkedIn MCP server
node /path/to/linkedin-mcp/index.js

# Or use Playwright directly
python scripts/linkedin_poster.py ./vault --post "Your content here"
```

## Content Types

### 1. Business Update

```markdown
---
type: linkedin_post
category: business_update
created: 2026-03-18
status: draft
approval_required: true
---

# Post Content

🚀 Exciting news! We've launched our new AI Employee service.

Key features:
✅ 24/7 autonomous operation
✅ Local-first privacy
✅ Human-in-the-loop safety

#AI #Automation #Business

---

## Approval
Move to /Approved/ to post
```

### 2. Thought Leadership

```markdown
# Post Content

The future of work isn't human vs AI—it's human + AI.

After building 50+ autonomous agents, here's what I've learned:

1. Start with clear rules
2. Keep humans in the loop
3. Measure everything

What's your experience?

#FutureOfWork #AI #Leadership
```

### 3. Lead Generation

```markdown
# Post Content

Struggling with inbox overload?

Our AI Employee:
📧 Processes 1000s of emails daily
🎯 Prioritizes what matters
✍️ Drafts responses for review

Result: 10x productivity gain

DM for demo!

#Productivity #AI #Business
```

## Posting Workflow

### Step 1: Generate Content

Qwen reads `Business_Goals.md` and creates post draft:

```markdown
---
type: approval_request
action: linkedin_post
content_preview: "Exciting news! We've launched..."
scheduled: 2026-03-18T14:00:00Z
status: pending
---

# LinkedIn Post Approval

**Content Preview:**
Exciting news! We've launched our new AI Employee service...

**Hashtags:** #AI #Automation #Business

**Post Time:** Today at 2:00 PM

## To Approve
Move to `/Approved/` to post

## To Reject
Move to `/Rejected/` with feedback
```

### Step 2: Human Review

1. Read the approval file
2. Review content, hashtags, timing
3. Move to `/Approved/` or `/Rejected/`

### Step 3: Execute Post

```python
# linkedin_poster.py
from playwright.sync_api import sync_playwright

def post_to_linkedin(content: str, credentials: dict):
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            credentials['session_path'],
            headless=True
        )
        page = browser.pages[0]
        
        # Navigate to LinkedIn
        page.goto('https://www.linkedin.com/feed/')
        
        # Click create post
        page.click('[aria-label="Start a post"]')
        
        # Wait for editor
        page.wait_for_selector('[aria-label="What do you want to share?"]')
        
        # Type content
        page.fill('[aria-label="What do you want to share?"]', content)
        
        # Click post
        page.click('button:has-text("Post")')
        
        # Wait for confirmation
        page.wait_for_selector('text=Your post has been shared')
        
        browser.close()
        return True
```

## Content Calendar

### Posting Schedule (from Business_Goals.md)

| Day | Time | Content Type |
|-----|------|--------------|
| Monday | 9:00 AM | Motivation/Goals |
| Wednesday | 2:00 PM | Educational/How-to |
| Friday | 11:00 AM | Business Update/Case Study |

### Auto-Generate Posts

```python
# Generate weekly posts from Business_Goals.md
def generate_weekly_content():
    goals = read_business_goals()
    posts = []
    
    # Post 1: Progress update
    posts.append({
        'type': 'progress',
        'content': f"This week we're focusing on {goals['weekly_focus']}..."
    })
    
    # Post 2: Educational
    posts.append({
        'type': 'educational',
        'content': f"Here's what we learned about {goals['industry']}..."
    })
    
    return posts
```

## Engagement Rules

### Company Handbook Rules

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Post draft | ❌ | **Always** |
| Reply to comment | ❌ | **Always** |
| Like post | ✅ | If from known contact |
| Share post | ❌ | **Always** |

### Engagement Workflow

```python
# Check engagement rules
def should_engage(post: dict) -> bool:
    if post['type'] == 'comment_reply':
        return False  # Always require approval
    
    if post['type'] == 'like' and post['from_known_contact']:
        return True  # Auto-approve
    
    return False  # Default: require approval
```

## Analytics Tracking

### Post Performance

```markdown
---
post_id: abc123
posted: 2026-03-18T14:00:00Z
content_preview: "Exciting news!..."
---

# Post Analytics

| Metric | Value |
|--------|-------|
| Impressions | 1,234 |
| Likes | 45 |
| Comments | 12 |
| Shares | 8 |
| Clicks | 67 |

## ROI Tracking
- Leads generated: 3
- Demo requests: 1
- Connection requests: 5
```

## Configuration

### Session Management

```python
# Store LinkedIn session
SESSION_PATH = "./.cache/linkedin_session"

# First run: Login manually
# Subsequent runs: Use saved session
```

### Posting Limits

```python
# Safe posting limits
MAX_POSTS_PER_DAY = 3
MAX_CONNECTION_REQUESTS = 20
MAX_MESSAGES_PER_DAY = 50
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Clear session, re-authenticate |
| Post not appearing | Check LinkedIn algorithm limits |
| Browser crashes | Reduce headless timeout |
| Rate limited | Wait 24 hours, reduce frequency |

## Integration with Business Goals

```python
# Read Business_Goals.md for content themes
def get_content_themes():
    goals = read_markdown('./Business_Goals.md')
    return {
        'focus': goals.get('weekly_focus', 'AI Automation'),
        'metrics': goals.get('key_metrics', []),
        'projects': goals.get('active_projects', [])
    }
```

## Example: Full Workflow

```bash
# 1. Qwen generates post from Business_Goals.md
qwen "Generate 3 LinkedIn posts from this week's goals"

# 2. Creates approval files in Pending_Approval/
# - LINKEDIN_POST_20260318_motivation.md
# - LINKEDIN_POST_20260320_educational.md
# - LINKEDIN_POST_20260322_business.md

# 3. Human reviews and approves
# Move files to /Approved/

# 4. Orchestrator posts
python scripts/linkedin_poster.py ./vault --auto

# 5. Logs results
# Updates Dashboard.md with analytics
```

## Content Templates

### Template 1: Problem/Solution

```
Problem: [Common pain point]

Solution: [Your approach]

Result: [Specific outcome]

[Call to action]

#Hashtags
```

### Template 2: List Post

```
[Number] lessons from [experience]:

1. [Lesson 1]
2. [Lesson 2]
3. [Lesson 3]

What would you add?

#Hashtags
```

### Template 3: Before/After

```
Before [your solution]:
- [Pain point 1]
- [Pain point 2]

After [your solution]:
- [Benefit 1]
- [Benefit 2]

[Call to action]

#Hashtags
```
