---
name: email-mcp
description: |
  Email automation using Gmail API via MCP server. Send, draft, search, and manage emails.
  Use when tasks require sending emails, managing inbox, or email-based communication.
  Requires Gmail API credentials setup.
---

# Email MCP Server

Automate email operations via Gmail API MCP server.

## Prerequisites

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Server Lifecycle

### Start Server

```bash
# Start Gmail MCP server
node /path/to/email-mcp/index.js

# Or using npx (if available)
npx @anthropic/email-mcp --credentials /path/to/credentials.json
```

### Stop Server

```bash
# Close connections and stop
pkill -f "email-mcp"
```

## Quick Reference

### Send Email

```bash
# Send email immediately
python3 scripts/mcp-client.py call -u http://localhost:8809 -t email_send \
  -p '{"to": "recipient@example.com", "subject": "Hello", "body": "Message content"}'
```

### Draft Email

```bash
# Create draft (requires approval before sending)
python3 scripts/mcp-client.py call -u http://localhost:8809 -t email_draft \
  -p '{"to": "recipient@example.com", "subject": "Invoice #123", "body": "Please find attached..."}'
```

### Search Emails

```bash
# Search inbox
python3 scripts/mcp-client.py call -u http://localhost:8809 -t email_search \
  -p '{"query": "is:unread from:client@example.com"}'
```

### Read Email

```bash
# Get email by ID
python3 scripts/mcp-client.py call -u http://localhost:8809 -t email_read \
  -p '{"message_id": "abc123"}'
```

### Mark as Read

```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t email_mark_read \
  -p '{"message_id": "abc123"}'
```

### Send with Attachment

```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t email_send \
  -p '{
    "to": "client@example.com",
    "subject": "Invoice #123",
    "body": "Please find attached your invoice.",
    "attachments": ["/path/to/invoice.pdf"]
  }'
```

## Workflow: Send Email (HITL)

1. **Create approval request** in `/Pending_Approval/`
2. **Human reviews** and moves to `/Approved/`
3. **Execute send** via MCP
4. **Log action** in `/Logs/`
5. **Move to** `/Done/`

### Example Approval File

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #123
created: 2026-03-18T10:30:00Z
status: pending
---

# Email Approval Request

**To:** client@example.com  
**Subject:** Invoice #123  
**Body Preview:** Please find attached your invoice for January 2026...

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.
```

## Workflow: Auto-Reply to Known Contact

```python
# Check Company_Handbook rules
# If sender is known and email is simple:
# 1. Draft reply
# 2. If <50 words, can auto-send (per handbook rules)
# 3. Otherwise, request approval

# MCP call
python3 scripts/mcp-client.py call -u http://localhost:8809 -t email_send \
  -p '{
    "to": "known@client.com",
    "subject": "Re: Meeting Tomorrow",
    "body": "Hi, yes 2pm works perfectly. See you then!",
    "in_reply_to": "msg123"
  }'
```

## Configuration

### MCP Server Config

```json
// ~/.config/qwen-code/mcp.json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json",
        "GMAIL_TOKEN_PATH": "/path/to/token.json"
      }
    }
  ]
}
```

### Environment Variables

```bash
export GMAIL_CREDENTIALS_PATH="/path/to/credentials.json"
export GMAIL_TOKEN_PATH="/path/to/token.json"
export DRY_RUN="false"  # Set to "true" for testing
```

## Security Rules (from Company Handbook)

| Scenario | Action | Approval Required |
|----------|--------|-------------------|
| Reply to known contact | Draft reply | No (if <50 words) |
| Reply to new contact | Draft reply | **Yes** |
| Bulk email (>10 recipients) | Draft only | **Yes** |
| Email with attachment | Draft only | **Yes** |
| Forward internal discussion | Draft only | **Yes** |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run OAuth flow, check credentials.json |
| Token expired | Delete token.json, re-authenticate |
| API quota exceeded | Wait 24 hours or request quota increase |
| Server not responding | Check port 8809, restart server |

## Verification

```bash
# Test connection
python3 scripts/mcp-client.py call -u http://localhost:8809 -t email_search \
  -p '{"query": "is:inbox", "maxResults": 1}'

# Expected: Recent email from inbox
```

## Integration with Watchers

Gmail Watcher creates action files → Qwen processes → Email MCP sends:

```
Gmail Watcher → Needs_Action/ → Qwen reads → Creates approval → 
Human approves → Email MCP sends → Logs → Done/
```
