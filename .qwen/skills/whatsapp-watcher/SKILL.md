---
name: whatsapp-watcher
description: |
  WhatsApp monitoring using Playwright for WhatsApp Web automation. Detects messages,
  keywords, and creates action files. Use for WhatsApp-based communication monitoring.
  Requires WhatsApp Web session and Playwright installed.
---

# WhatsApp Watcher

Monitor WhatsApp Web for new messages and create action files in Needs_Action folder.

## Prerequisites

### 1. Install Playwright

```bash
npm install -D playwright
playwright install chromium
```

### 2. Install Python Dependencies

```bash
pip install playwright
```

### 3. WhatsApp Web Setup

- WhatsApp account with WhatsApp Web enabled
- Phone nearby for QR code scan (first time only)
- Stable internet connection

## Architecture

```
WhatsApp Web → Playwright Browser → Keyword Detection → 
Action File Creation → Needs_Action/ → Qwen Processing
```

## Quick Start

### Start WhatsApp Watcher

```bash
cd /path/to/AI_Employee_Vault
python scripts/whatsapp_watcher.py ./AI_Employee_Vault
```

### First Run (Authenticate)

1. Script opens browser to WhatsApp Web
2. Scan QR code with your phone
3. Session saved for future runs
4. Watcher starts monitoring

## Configuration

### Watched Keywords

Default priority keywords (configurable):

```python
KEYWORDS = {
    'high': ['urgent', 'asap', 'emergency', 'invoice', 'payment', 'help'],
    'medium': ['meeting', 'call', 'today', 'deadline', 'review'],
    'low': ['hello', 'thanks', 'ok', 'sure']
}
```

### Check Interval

```bash
# Default: Check every 30 seconds
python scripts/whatsapp_watcher.py ./vault 30
```

## Action File Format

When a message is detected, creates:

```markdown
---
type: whatsapp
from: +1234567890
chat: John Doe
received: 2026-03-18T10:30:00Z
priority: high
keywords: ['urgent', 'invoice']
status: pending
---

# WhatsApp Message

**From:** John Doe (+1234567890)  
**Chat:** Individual  
**Received:** 2026-03-18 10:30:00  
**Priority:** HIGH

---

## Message Content

Hey, can you send me the invoice for January? It's urgent.

---

## Suggested Actions

- [ ] Reply to sender
- [ ] Generate invoice
- [ ] Forward to accounting
- [ ] Archive after processing

## Notes

_Add your notes here_

---

*Created by WhatsApp Watcher*
```

## Workflow: Message Processing

1. **Watcher detects** message with keyword "invoice"
2. **Creates action file** in `Needs_Action/`
3. **Qwen reads** file, checks Company_Handbook
4. **Creates plan** in `Plans/`
5. **Generates invoice** draft
6. **Requests approval** in `Pending_Approval/`
7. **Human approves** → sends via Email MCP

## Script Structure

```python
# whatsapp_watcher.py
from playwright.sync_api import sync_playwright
from base_watcher import BaseWatcher

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path, check_interval=30):
        super().__init__(vault_path, check_interval)
        self.session_path = self.vault_path / '.cache' / 'whatsapp_session'
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help']
    
    def check_for_updates(self) -> list:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                self.session_path,
                headless=True
            )
            page = browser.pages[0]
            page.goto('https://web.whatsapp.com')
            
            # Wait for chat list
            page.wait_for_selector('[data-testid="chat-list"]')
            
            # Find unread messages
            unread = page.query_selector_all('[aria-label*="unread"]')
            messages = []
            
            for chat in unread:
                text = chat.inner_text().lower()
                if any(kw in text for kw in self.keywords):
                    messages.append({
                        'text': text,
                        'chat': chat,
                        'priority': self._get_priority(text)
                    })
            
            browser.close()
            return messages
    
    def create_action_file(self, item) -> Path:
        # Create .md file in Needs_Action/
        pass
    
    def _get_priority(self, text: str) -> str:
        for kw in ['urgent', 'asap', 'emergency']:
            if kw in text:
                return 'high'
        return 'medium'
```

## Priority Detection

| Keywords | Priority | Response Time |
|----------|----------|---------------|
| urgent, asap, emergency, invoice, payment | 🔴 High | <1 hour |
| meeting, call, today, deadline | 🟠 Medium | <4 hours |
| hello, thanks, ok | 🟢 Low | <24 hours |

## Security Considerations

### Session Storage

- Session stored in `.cache/whatsapp_session/`
- Never commit to git (add to .gitignore)
- Encrypt for production use

### Message Content

- Only process messages with keywords
- Don't store full message history
- Delete processed action files after 90 days

### Rate Limiting

```python
# Max checks per hour
MAX_CHECKS = 120  # Every 30 seconds

# Max messages processed per check
MAX_MESSAGES = 10
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not appearing | Clear session folder, restart watcher |
| Not detecting messages | Check WhatsApp Web is loaded |
| Session expired | Re-scan QR code |
| Browser crashes | Reduce concurrent checks |

## Integration with Orchestrator

```python
# In orchestrator.py
def start_whatsapp_watcher(self):
    self.start_watcher('whatsapp', 'whatsapp_watcher.py')

# Start with orchestrator
python scripts/orchestrator.py ./vault filesystem whatsapp
```

## Example Usage

```bash
# Start watcher
python scripts/whatsapp_watcher.py "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"

# Watcher output:
# WhatsAppWatcher - INFO - Starting WhatsAppWatcher
# WhatsAppWatcher - INFO - Session path: ...\whatsapp_session
# WhatsAppWatcher - INFO - Scanning for messages...
# WhatsAppWatcher - INFO - Found 1 new message(s)
# WhatsAppWatcher - INFO - Created action file: WHATSAPP_20260318_103000_john_doe.md
```

## Testing

```bash
# Test without WhatsApp Web (mock mode)
python scripts/whatsapp_watcher.py ./vault --mock

# Test keyword detection
python scripts/whatsapp_watcher.py ./vault --test-keywords
```
