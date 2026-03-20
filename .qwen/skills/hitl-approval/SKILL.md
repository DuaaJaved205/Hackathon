---
name: hitl-approval
description: |
  Human-in-the-Loop approval workflow for sensitive actions. Manages approval requests,
  tracks decisions, and executes approved actions. Use for emails, payments, posts,
  and any action requiring human oversight.
---

# HITL Approval Workflow

Human-in-the-Loop (HITL) approval system for sensitive actions.

## Architecture

```
Qwen detects sensitive action → Creates approval request →
Human reviews → Moves file → Orchestrator executes → Logs result
```

## Folder Structure

```
Vault/
├── Pending_Approval/     # Awaiting human decision
├── Approved/             # Approved, ready to execute
├── Rejected/             # Rejected, do not execute
└── Logs/                 # Audit trail
```

## Approval Request Template

```markdown
---
type: approval_request
id: APPROVAL_20260318_001
action: email_send
created: 2026-03-18T10:30:00Z
expires: 2026-03-19T10:30:00Z
priority: high
status: pending
---

# Approval Request: Send Email

## Action Details

**Action Type:** Email Send  
**Priority:** High  
**Created:** 2026-03-18 10:30 AM  
**Expires:** 2026-03-19 10:30 AM (24 hours)

## Email Details

**To:** client@example.com  
**Subject:** Invoice #123 - January 2026  
**Body:**

```
Dear Client,

Please find attached your invoice for January 2026.

Amount: $1,500.00
Due Date: February 15, 2026

Thank you for your business!

Best regards,
Your Company
```

**Attachments:**
- /Vault/Invoices/2026-01_Client_A.pdf

## Context

This invoice was requested by the client via email on March 17, 2026.
The amount matches our agreed monthly rate from Business_Goals.md.

## Risk Assessment

| Factor | Level | Notes |
|--------|-------|-------|
| Financial impact | Low | Standard invoice |
| Relationship risk | Low | Routine communication |
| Error recovery | Easy | Can send correction if needed |

## Company Handbook Rules Applied

- ✅ Invoice amount matches agreed rate
- ✅ Client is known contact
- ✅ Email template approved
- ⚠️ Requires approval (financial document)

---

## Decision Required

### To Approve
**Move this file to:** `/Approved/`

The email will be sent within 5 minutes.

### To Reject
**Move this file to:** `/Rejected/`

**Please add rejection reason:**
```markdown
## Rejection Reason
[Add your reason here]
```

### To Request Changes
**Add a comment below and keep in Pending_Approval/**

Qwen will review and create updated approval request.

---

## Audit Trail

| Timestamp | Event | Actor |
|-----------|-------|-------|
| 2026-03-18 10:30 | Created | Qwen Code |
| - | - | - |
```

## Approval Types

### Type 1: Email Send

```markdown
---
action: email_send
to: recipient@example.com
subject: Email Subject
requires_attachment: false
---
```

**Rules:**
- Known contact + <50 words → Can auto-send (per handbook)
- New contact → Always approve
- Attachment → Always approve
- Bulk (>10 recipients) → Always approve

### Type 2: Payment

```markdown
---
action: payment
amount: 500.00
currency: USD
recipient: Vendor Name
account: ****1234
reference: Invoice #456
---
```

**Rules:**
- < $50 recurring → Can auto-approve (if payee exists)
- < $100 one-time → Always approve
- ≥ $100 → Always approve
- New payee → Always approve

### Type 3: Social Media Post

```markdown
---
action: social_post
platform: linkedin
content_preview: "Exciting news!..."
scheduled_time: 2026-03-18T14:00:00Z
---
```

**Rules:**
- All posts → Always approve before first publication
- Scheduled content → Approve once, auto-post recurring
- Replies/DMs → Always approve

### Type 4: File Operation

```markdown
---
action: file_delete
file: /Vault/Temp/old_file.txt
reason: Cleanup, file older than 90 days
---
```

**Rules:**
- Create/Read → Auto-approve
- Move within vault → Auto-approve
- Delete → Always approve
- Move outside vault → Always approve

## Workflow Implementation

### Step 1: Create Approval Request

```python
# hitl_approval.py
from datetime import datetime, timedelta
from pathlib import Path

def create_approval_request(
    action_type: str,
    details: dict,
    priority: str = 'medium',
    expires_hours: int = 24
) -> Path:
    """Create approval request file in Pending_Approval/."""
    
    timestamp = datetime.now()
    expiry = timestamp + timedelta(hours=expires_hours)
    request_id = f"APPROVAL_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    content = f"""---
type: approval_request
id: {request_id}
action: {action_type}
created: {timestamp.isoformat()}
expires: {expiry.isoformat()}
priority: {priority}
status: pending
---

# Approval Request: {action_type.replace('_', ' ').title()}

## Action Details
"""
    
    for key, value in details.items():
        content += f"**{key.replace('_', ' ').title()}:** {value}\n"
    
    content += f"""
---

## Decision Required

### To Approve
**Move this file to:** `/Approved/`

### To Reject
**Move this file to:** `/Rejected/`

---

## Audit Trail
| Timestamp | Event | Actor |
|-----------|-------|-------|
| {timestamp.isoformat()} | Created | Qwen Code |
"""
    
    pending_folder = Path('./Pending_Approval')
    pending_folder.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_action = action_type.replace('_', '-')
    filepath = pending_folder / f"{request_id}_{safe_action}.md"
    filepath.write_text(content)
    
    return filepath
```

### Step 2: Human Decision

Human moves file to one of:
- `/Approved/` → Execute action
- `/Rejected/` → Log and notify
- Keep in `/Pending_Approval/` with comments → Qwen reviews

### Step 3: Execute Approved Action

```python
def process_approved_actions():
    """Check Approved/ folder and execute actions."""
    
    approved_folder = Path('./Approved')
    
    for filepath in approved_folder.glob('*.md'):
        content = filepath.read_text()
        
        # Parse action type
        action_type = parse_frontmatter(content, 'action')
        
        # Execute based on type
        if action_type == 'email_send':
            execute_email_send(content)
        elif action_type == 'payment':
            execute_payment(content)
        elif action_type == 'social_post':
            execute_social_post(content)
        
        # Log execution
        log_action(filepath, action_type, 'executed')
        
        # Move to Done/
        done_folder = Path('./Done')
        done_folder.mkdir(parents=True, exist_ok=True)
        filepath.rename(done_folder / filepath.name)
```

### Step 4: Log Action

```python
def log_action(approval_file: Path, action_type: str, result: str):
    """Log action to audit trail."""
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': action_type,
        'approval_file': approval_file.name,
        'result': result,
        'actor': 'qwen-code'
    }
    
    # Append to daily log
    log_file = Path(f'./Logs/{datetime.now().strftime("%Y-%m-%d")}.json')
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logs = []
    if log_file.exists():
        import json
        logs = json.loads(log_file.read_text())
    
    logs.append(log_entry)
    log_file.write_text(json.dumps(logs, indent=2))
```

## Decision Matrix

| Action | Auto-Approve | Require Approval | Never Allow |
|--------|--------------|------------------|-------------|
| Email to known contact | <50 words | >50 words, new contact | Bulk (>100) |
| Payment existing payee | < $50 recurring | $50-$500 | > $500 |
| Payment new payee | Never | Any amount | - |
| Social post | Never | All posts | Controversial topics |
| File delete | Never | All deletions | System files |
| Data export | Never | All exports | Sensitive data |

## Timeout Handling

```python
def check_expired_approvals():
    """Handle expired approval requests."""
    
    pending_folder = Path('./Pending_Approval')
    
    for filepath in pending_folder.glob('*.md'):
        content = filepath.read_text()
        expires = parse_frontmatter(content, 'expires')
        
        if datetime.fromisoformat(expires) < datetime.now():
            # Expired - notify human
            add_note(filepath, "⚠️ EXPIRED - No response received")
            
            # Move to Rejected/ with note
            rejected_folder = Path('./Rejected')
            rejected_folder.mkdir(parents=True, exist_ok=True)
            filepath.rename(rejected_folder / filepath.name)
```

## Notification System

### Dashboard Alert

```python
def update_dashboard_approvals():
    """Update Dashboard.md with pending approvals count."""
    
    pending_count = len(list(Path('./Pending_Approval').glob('*.md')))
    
    dashboard = Path('./Dashboard.md')
    content = dashboard.read_text()
    
    # Update pending count
    content = content.replace(
        '**Pending Approvals** | 0',
        f'**Pending Approvals** | {pending_count}'
    )
    
    if pending_count > 5:
        content += "\n\n⚠️ **High pending approvals: {pending_count}**\n"
    
    dashboard.write_text(content)
```

## Audit & Compliance

### Daily Audit Report

```markdown
---
date: 2026-03-18
generated: 2026-03-18T23:00:00Z
---

# Daily Approval Audit

## Summary

| Metric | Value |
|--------|-------|
| Total requests | 12 |
| Approved | 8 |
| Rejected | 2 |
| Expired | 1 |
| Pending >24h | 1 |

## Approved Actions

| ID | Action | Amount | Approved By |
|----|--------|--------|-------------|
| APPROVAL_001 | email_send | - | human |
| APPROVAL_002 | payment | $500 | human |

## Rejected Actions

| ID | Action | Reason |
|----|--------|--------|
| APPROVAL_003 | social_post | Content needs revision |

## Recommendations

1. Review expired approval process
2. Follow up on pending >24h
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not executed | Check file moved to Approved/ |
| Wrong action executed | Review approval file content |
| Approval expired | Re-create with updated info |
| Human not notified | Check Dashboard update |

## Best Practices

1. **Clear action details** - Leave no ambiguity
2. **Reasonable expiry** - 24-48 hours typical
3. **Risk assessment** - Help human decide
4. **Audit trail** - Log everything
5. **Graceful rejection** - Capture feedback
6. **Regular cleanup** - Archive old approvals
