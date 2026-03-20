---
name: scheduler
description: |
  Schedule recurring tasks using cron (Linux/Mac) or Task Scheduler (Windows).
  Automates daily briefings, weekly audits, periodic checks, and time-based triggers.
  Use for any task that needs to run at specific times or intervals.
---

# Scheduler Skill

Schedule and automate time-based tasks for your AI Employee.

## Architecture

```
System Scheduler (cron/Task Scheduler) → 
  Triggers Script → Qwen Processes → Updates Vault
```

## Scheduling Options

### Option 1: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add scheduled tasks
```

### Option 2: Windows Task Scheduler

```powershell
# Using schtasks command
schtasks /Create /TN "AI Employee" /TR "python script.py" /SC DAILY /ST 08:00
```

### Option 3: Python APScheduler

```python
# For cross-platform Python-based scheduling
pip install apscheduler
```

## Scheduled Tasks

### Task 1: Daily Briefing (8:00 AM)

**Purpose:** Start each day with a summary of pending items and priorities.

```bash
# Cron entry (daily at 8 AM)
0 8 * * * cd /path/to/vault && qwen "Generate daily briefing" >> Logs/daily_briefing.log
```

**Output:**
```markdown
---
date: 2026-03-18
type: daily_briefing
generated: 2026-03-18T08:00:00Z
---

# Daily Briefing

## Today's Priorities
1. Process 3 pending emails
2. Approve invoice for Client A
3. Review LinkedIn post draft

## Pending Actions
- 3 items in Needs_Action/
- 1 item in Pending_Approval/

## Today's Meetings
- 2:00 PM: Client call
```

### Task 2: WhatsApp Check (Every 5 minutes)

**Purpose:** Continuously monitor WhatsApp for urgent messages.

```bash
# Cron entry (every 5 minutes)
*/5 * * * * cd /path/to/vault && python scripts/whatsapp_watcher.py ./vault
```

### Task 3: Gmail Check (Every 2 minutes)

**Purpose:** Monitor Gmail for new messages.

```bash
# Cron entry (every 2 minutes)
*/2 * * * * cd /path/to/vault && python scripts/gmail_watcher.py ./vault
```

### Task 4: Weekly Audit (Sunday 10:00 PM)

**Purpose:** Generate CEO Briefing with weekly summary.

```bash
# Cron entry (every Sunday at 10 PM)
0 22 * * 0 cd /path/to/vault && qwen "Generate weekly CEO briefing" >> Logs/weekly_briefing.log
```

**Output:**
```markdown
---
week: 2026-W12
type: weekly_briefing
generated: 2026-03-17T22:00:00Z
---

# Weekly CEO Briefing

## Revenue This Week
- Total: $2,450
- Invoices sent: 3
- Invoices paid: 2

## Completed Tasks
- 15 tasks completed
- 2 tasks overdue

## Bottlenecks
- Client B proposal took 5 days (expected: 2)

## Proactive Suggestions
1. Cancel Notion subscription (no activity in 45 days)
2. Follow up on overdue invoice #120
```

### Task 5: Monthly Subscription Audit (1st of month)

**Purpose:** Review all subscriptions for waste.

```bash
# Cron entry (1st of every month at 9 AM)
0 9 1 * * cd /path/to/vault && qwen "Audit subscriptions from bank transactions" >> Logs/subscription_audit.log
```

### Task 6: Process Pending Items (Every hour)

**Purpose:** Auto-process Needs_Action folder.

```bash
# Cron entry (every hour)
0 * * * * cd /path/to/vault && qwen "Process all files in Needs_Action/" >> Logs/processing.log
```

## Windows Task Scheduler Setup

### Create Scheduled Task (GUI)

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name: "AI Employee - Daily Briefing"
4. Trigger: Daily at 8:00 AM
5. Action: Start a program
6. Program: `qwen`
7. Arguments: `"Generate daily briefing"`
8. Start in: `C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault`

### Create Scheduled Task (PowerShell)

```powershell
# Daily Briefing at 8 AM
$action = New-ScheduledTaskAction -Execute "qwen" `
  -Argument "Generate daily briefing" `
  -WorkingDirectory "C:\Users\Haya Javed\Downloads\Hackathon0\AI_Employee_Vault"

$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

Register-ScheduledTask -TaskName "AI Employee - Daily Briefing" `
  -Action $action -Trigger $trigger -User "Haya Javed"
```

### List Scheduled Tasks

```powershell
# List all AI Employee tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "AI Employee*"}
```

### Run Task Manually

```powershell
# Start a scheduled task
Start-ScheduledTask -TaskName "AI Employee - Daily Briefing"
```

## Python APScheduler (Cross-Platform)

### Installation

```bash
pip install apscheduler
```

### Basic Scheduler Script

```python
# scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_qwen(prompt: str):
    """Run Qwen with a prompt."""
    result = subprocess.run(
        ['qwen', prompt],
        cwd='./AI_Employee_Vault',
        capture_output=True,
        text=True
    )
    logger.info(result.stdout)

def run_watcher(script: str):
    """Run a watcher script."""
    subprocess.run(
        ['python', f'scripts/{script}', './AI_Employee_Vault'],
        cwd='./AI_Employee_Vault'
    )

# Create scheduler
sched = BlockingScheduler()

# Daily briefing at 8 AM
sched.add_job(
    run_qwen,
    CronTrigger(hour=8, minute=0),
    args=['Generate daily briefing'],
    id='daily_briefing'
)

# WhatsApp check every 5 minutes
sched.add_job(
    run_watcher,
    IntervalTrigger(minutes=5),
    args=['whatsapp_watcher.py'],
    id='whatsapp_check'
)

# Weekly audit Sunday 10 PM
sched.add_job(
    run_qwen,
    CronTrigger(day_of_week='sun', hour=22, minute=0),
    args=['Generate weekly CEO briefing'],
    id='weekly_audit'
)

# Start scheduler
logger.info("Starting scheduler...")
sched.start()
```

### Run as Background Service

```bash
# Linux/Mac (using nohup)
nohup python scheduler.py > scheduler.log 2>&1 &

# Windows (using nssm)
nssm install AI_Employee_Scheduler "python" "scheduler.py"
nssm start AI_Employee_Scheduler
```

## Schedule Configuration File

```yaml
# schedules.yaml
schedules:
  daily_briefing:
    trigger: "cron"
    hour: 8
    minute: 0
    action: "qwen"
    prompt: "Generate daily briefing"
  
  whatsapp_monitor:
    trigger: "interval"
    minutes: 5
    action: "python"
    script: "whatsapp_watcher.py"
  
  gmail_monitor:
    trigger: "interval"
    minutes: 2
    action: "python"
    script: "gmail_watcher.py"
  
  weekly_audit:
    trigger: "cron"
    day_of_week: "sun"
    hour: 22
    minute: 0
    action: "qwen"
    prompt: "Generate weekly CEO briefing"
  
  subscription_audit:
    trigger: "cron"
    day: 1
    hour: 9
    minute: 0
    action: "qwen"
    prompt: "Audit subscriptions from bank transactions"
```

## Monitoring Scheduled Tasks

### Check Task History

```bash
# Cron logs (Linux)
grep CRON /var/log/syslog

# Task Scheduler history (Windows)
# Open Task Scheduler → Select task → View → Enable All Tasks History
```

### Health Check Script

```python
# health_check.py
import subprocess
from datetime import datetime

def check_schedulers():
    """Check if all schedulers are running."""
    
    checks = [
        ("WhatsApp Watcher", "pgrep -f whatsapp_watcher"),
        ("Gmail Watcher", "pgrep -f gmail_watcher"),
        ("Orchestrator", "pgrep -f orchestrator"),
    ]
    
    for name, cmd in checks:
        result = subprocess.run(cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"✅ {name}: Running")
        else:
            print(f"❌ {name}: Not running")
            print(f"   Restarting...")
            # Auto-restart logic here
```

## Error Handling

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def run_scheduled_task():
    """Run task with retry logic."""
    # Task implementation
    pass
```

### Failure Notification

```python
def notify_on_failure(task_name: str, error: str):
    """Send failure notification."""
    
    content = f"""---
type: alert
severity: high
task: {task_name}
error: {error}
---

# Scheduled Task Failed

**Task:** {task_name}  
**Error:** {error}  
**Time:** {datetime.now()}

## Action Required
Please check the scheduler logs and restart if needed.
"""
    
    # Write to Needs_Action for immediate attention
    Path('./Needs_Action/ALERT_scheduler_failure.md').write_text(content)
```

## Best Practices

1. **Log everything** - Capture stdout/stderr
2. **Set reasonable intervals** - Don't overload APIs
3. **Handle failures gracefully** - Retry with backoff
4. **Monitor health** - Check if schedulers running
5. **Timezone aware** - Use UTC or specify timezone
6. **Test before deploying** - Run manually first
7. **Document schedules** - Keep schedule.yaml updated

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check scheduler service status |
| Wrong time | Verify timezone settings |
| Permission denied | Run as appropriate user |
| Missing output | Check log file paths |
| Multiple executions | Ensure no duplicate schedules |

## Quick Reference

### Cron Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sunday=0)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

### Common Schedules

| Description | Cron |
|-------------|------|
| Every minute | `* * * * *` |
| Every 5 minutes | `*/5 * * * *` |
| Every hour | `0 * * * *` |
| Daily at 8 AM | `0 8 * * *` |
| Weekly Sunday 10 PM | `0 22 * * 0` |
| Monthly 1st at 9 AM | `0 9 1 * *` |
