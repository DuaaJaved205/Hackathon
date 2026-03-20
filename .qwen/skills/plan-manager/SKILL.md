---
name: plan-manager
description: |
  Create and manage Plan.md files for multi-step tasks. Tracks progress, dependencies,
  and completion status. Use when tasks require multiple steps or cross-file coordination.
  Integrates with Company_Handbook rules for task prioritization.
---

# Plan Manager Skill

Create structured plans for multi-step tasks and track progress to completion.

## When to Create a Plan

Create a `Plan.md` when:
- Task requires 3+ steps
- Task spans multiple files/folders
- Task requires approval at multiple stages
- Task has dependencies (A must complete before B)
- Task estimated time > 30 minutes

## Plan.md Template

```markdown
---
plan_id: PLAN_20260318_001
created: 2026-03-18T10:30:00Z
created_by: qwen-code
status: in_progress
priority: high
estimated_duration: 2h
actual_duration: -
tags: [invoice, client-communication, email]
related_files:
  - Needs_Action/EMAIL_20260318_invoice_request.md
  - Pending_Approval/EMAIL_invoice_client_a.md
---

# Plan: Process Invoice Request

## Objective
Generate and send January invoice to Client A within 24 hours.

## Context
- Client A requested invoice via email on 2026-03-17
- Amount: $1,500 (from Business_Goals.md rates)
- Due date: Net-30 from invoice date
- Company_Handbook rules apply: Financial documents require approval

## Steps

### Phase 1: Preparation
- [x] Read original email request
- [x] Identify client details (email, rate, project)
- [x] Check Company_Handbook for invoice rules
- [ ] Calculate total amount
- [ ] Generate invoice PDF

### Phase 2: Approval
- [ ] Create approval request in Pending_Approval/
- [ ] Wait for human approval
- [ ] If approved: proceed to Phase 3
- [ ] If rejected: move to Rejected/, update Dashboard

### Phase 3: Execution
- [ ] Send email with invoice (via Email MCP)
- [ ] Log action in Logs/
- [ ] Update Dashboard.md

### Phase 4: Follow-up
- [ ] Create reminder for payment due date
- [ ] Schedule follow-up if unpaid after 15 days
- [ ] Move all files to Done/

## Dependencies
- Email MCP server must be running
- Human approval required before sending
- Invoice template must exist

## Blockers
- None currently

## Notes

### 2026-03-18 10:30
Plan created. Starting Phase 1.

### 2026-03-18 10:35
Client details identified: client_a@example.com, Rate: $1,500/month

---

## Completion Criteria

Task is complete when:
1. Invoice PDF generated
2. Email sent to client
3. Action logged
4. All files moved to Done/
5. Dashboard updated

## Rollback Plan

If sending fails:
1. Log error in plan
2. Notify human via Dashboard
3. Keep approval file in Pending_Approval
4. Retry after human confirmation
```

## Creating a Plan

### Qwen Prompt

```
I have a complex task in Needs_Action/. Please:
1. Read the action file
2. Check Company_Handbook for applicable rules
3. Create a Plan.md in Plans/ folder with:
   - Clear objective
   - All required steps with checkboxes
   - Approval requirements
   - Dependencies and blockers
   - Completion criteria
4. Start executing Phase 1
```

### Programmatic Creation

```python
# plan_manager.py
from datetime import datetime
from pathlib import Path

def create_plan(
    objective: str,
    steps: list,
    priority: str = 'medium',
    requires_approval: bool = True,
    related_files: list = None
) -> Path:
    """Create a new Plan.md file."""
    
    plan_id = f"PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    timestamp = datetime.now().isoformat()
    
    content = f"""---
plan_id: {plan_id}
created: {timestamp}
created_by: qwen-code
status: in_progress
priority: {priority}
requires_approval: {requires_approval}
---

# Plan: {objective}

## Objective
{objective}

## Steps
"""
    
    for i, step in enumerate(steps, 1):
        content += f"- [ ] {step}\n"
    
    content += f"""
## Completion Criteria
- All steps completed
- Approval obtained (if required)
- Files moved to Done/
- Dashboard updated

## Notes
"""
    
    plans_folder = Path('./Plans')
    plans_folder.mkdir(parents=True, exist_ok=True)
    
    filepath = plans_folder / f"{plan_id}.md"
    filepath.write_text(content)
    
    return filepath
```

## Plan States

| State | Description | Next Action |
|-------|-------------|-------------|
| `draft` | Plan created, not started | Begin Phase 1 |
| `in_progress` | Actively working | Continue execution |
| `blocked` | Waiting on external factor | Notify human |
| `pending_approval` | Awaiting human decision | Wait |
| `completed` | All steps done | Archive |
| `cancelled` | Stopped by human | Move to Done/ |

## Progress Tracking

### Update Plan Status

```python
def update_plan_status(plan_path: Path, new_status: str, note: str = None):
    """Update plan status and add note."""
    content = plan_path.read_text()
    
    # Update status in frontmatter
    content = content.replace(
        'status: in_progress',
        f'status: {new_status}'
    )
    
    # Add note
    if note:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        content += f"\n### {timestamp}\n{note}\n"
    
    plan_path.write_text(content)
```

### Daily Progress Review

```markdown
## Progress Log

| Date | Status | Completed Steps | Blockers |
|------|--------|-----------------|----------|
| 2026-03-18 | in_progress | 4/12 | None |
| 2026-03-19 | pending_approval | 6/12 | Awaiting email approval |
| 2026-03-20 | completed | 12/12 | None |
```

## Integration with Approval Workflow

```
Plan.md created → Executes Phase 1 → Creates approval request →
Updates status to pending_approval → Human approves →
Updates status to in_progress → Completes remaining steps →
Updates status to completed
```

### Example Flow

```markdown
---
plan_id: PLAN_20260318_001
status: pending_approval
current_step: 6
---

## Current Status

**Phase:** 2 of 4 (Approval)  
**Completed:** 5/12 steps  
**Blocked on:** Email approval from human

## Next Steps (after approval)
1. Send email via Email MCP
2. Log action
3. Update Dashboard
4. Archive files
```

## Multi-Plan Coordination

When multiple plans are active:

```markdown
# Active Plans Summary

| Plan ID | Objective | Status | Priority |
|---------|-----------|--------|----------|
| PLAN_001 | Invoice Client A | pending_approval | high |
| PLAN_002 | LinkedIn Post | in_progress | medium |
| PLAN_003 | Weekly Report | draft | low |

## Resource Conflicts
- None detected

## Shared Dependencies
- Email MCP: Used by PLAN_001
```

## Completion Criteria Template

```markdown
## Completion Criteria

Task is complete when:
1. [ ] All steps executed successfully
2. [ ] Required approvals obtained
3. [ ] Actions logged in Logs/
4. [ ] Related files moved to Done/
5. [ ] Dashboard.md updated
6. [ ] Human notified (if required)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan not progressing | Check blockers, update status |
| Approval taking too long | Send reminder via Dashboard |
| Steps failing repeatedly | Escalate to human |
| Plan abandoned | Cancel and document lessons |

## Best Practices

1. **One objective per plan** - Keep focused
2. **Clear completion criteria** - Know when done
3. **Regular status updates** - Track progress
4. **Document blockers** - Enable escalation
5. **Link related files** - Maintain context
6. **Archive completed plans** - Move to Done/

## Example: Complex Plan

```markdown
---
plan_id: PLAN_20260318_ceo_briefing
objective: Generate weekly CEO Briefing
estimated_duration: 4h
---

# Plan: Weekly CEO Briefing

## Phases

### Phase 1: Data Collection
- [ ] Read all Done/ files from this week
- [ ] Sum transactions from Accounting/
- [ ] Count completed tasks
- [ ] Identify bottlenecks

### Phase 2: Analysis
- [ ] Compare revenue vs targets
- [ ] Calculate task completion rate
- [ ] Identify subscription waste
- [ ] Find process improvements

### Phase 3: Report Generation
- [ ] Write Executive Summary
- [ ] Create Revenue section
- [ ] Document Completed Tasks
- [ ] List Bottlenecks
- [ ] Add Proactive Suggestions

### Phase 4: Review
- [ ] Save to Briefings/
- [ ] Update Dashboard.md
- [ ] Notify human

## Completion
Briefing saved as Briefings/2026-03-18_Weekly_Briefing.md
```
