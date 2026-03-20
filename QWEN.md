# Project Context: Personal AI Employee Hackathon 0

## Project Overview

This directory contains resources for **Building Autonomous FTEs (Full-Time Equivalent) in 2026** - a hackathon project focused on creating a "Digital FTE": a local-first, AI-powered autonomous agent that manages personal and business affairs 24/7.

### Core Concept

The project transforms Qwen Code from a reactive chatbot into a **proactive business partner** that:
- Monitors communications (Gmail, WhatsApp, LinkedIn)
- Manages business tasks (social media, payments, projects)
- Performs autonomous audits and generates CEO briefings
- Operates with human-in-the-loop approval for sensitive actions

### Architecture Components

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine with Ralph Wiggum persistence loop |
| **Memory/GUI** | Obsidian (Markdown) | Local dashboard, knowledge base, task tracking |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems for triggers |
| **Hands** | MCP Servers | External actions (email, browser automation, payments) |

## Key Files

| File | Description |
|------|-------------|
| `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md` | Comprehensive architectural blueprint and hackathon guide (1201 lines) |
| `skills-lock.json` | Qwen skills configuration (tracks installed skills) |
| `.qwen/skills/` | Qwen skills directory (see Available Skills below) |

## Available Skills

### Bronze Tier Skills
| Skill | Description | Location |
|-------|-------------|----------|
| `browsing-with-playwright` | Browser automation for web interactions | `.qwen/skills/browsing-with-playwright/` |

### Silver Tier Skills
| Skill | Description | Location |
|-------|-------------|----------|
| `email-mcp` | Email automation via Gmail API | `.qwen/skills/email-mcp/` |
| `whatsapp-watcher` | WhatsApp Web monitoring via Playwright | `.qwen/skills/whatsapp-watcher/` |
| `linkedin-poster` | LinkedIn posting and engagement | `.qwen/skills/linkedin-poster/` |
| `plan-manager` | Plan.md creation for multi-step tasks | `.qwen/skills/plan-manager/` |
| `hitl-approval` | Human-in-the-Loop approval workflow | `.qwen/skills/hitl-approval/` |
| `scheduler` | Cron/Task Scheduler integration | `.qwen/skills/scheduler/` |

## Technology Stack

### Required Software
- **Qwen Code** - Primary reasoning engine
- **Obsidian** v1.10.6+ - Knowledge base dashboard (local Markdown)
- **Python** 3.13+ - Watcher scripts and orchestration
- **Node.js** v24+ LTS - MCP servers and automation
- **GitHub Desktop** - Version control for vault

### Key Libraries/Tools
- **Playwright** - Browser automation (WhatsApp, LinkedIn)
- **Google Gmail API** - Email monitoring and sending
- **Watchdog (Python)** - File system monitoring
- **APScheduler** - Cross-platform task scheduling
- **Model Context Protocol (MCP)** - External system integration

## Project Structure

```
Hackathon0/
├── Personal AI Employee Hackathon 0_...md    # Main blueprint document
├── skills-lock.json                           # Qwen skills config
├── QWEN.md                                    # This context file
└── .qwen/
    └── skills/
        ├── browsing-with-playwright/          # Browser automation skill
        ├── email-mcp/                         # Email automation (Silver)
        ├── whatsapp-watcher/                  # WhatsApp monitoring (Silver)
        ├── linkedin-poster/                   # LinkedIn posting (Silver)
        ├── plan-manager/                      # Plan.md management (Silver)
        ├── hitl-approval/                     # HITL workflow (Silver)
        └── scheduler/                         # Task scheduling (Silver)
```

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hrs | Obsidian vault, 1 watcher, basic Qwen integration |
| **Silver** | 20-30 hrs | Multiple watchers, MCP server, approval workflow, scheduling |
| **Gold** | 40+ hrs | Full integration, Odoo accounting, Ralph Wiggum loop |
| **Platinum** | 60+ hrs | Cloud deployment, 24/7 operation, A2A messaging |

### Silver Tier Deliverables (Complete)
- ✅ Two or more Watcher scripts (Gmail + WhatsApp + File System)
- ✅ LinkedIn auto-posting for business promotion
- ✅ Plan.md creation for multi-step tasks
- ✅ Email MCP server for sending emails
- ✅ Human-in-the-loop approval workflow
- ✅ Basic scheduling via cron/Task Scheduler

## Key Patterns

### 1. Watcher Architecture
Lightweight Python scripts monitor inputs and create `.md` files in `/Needs_Action/` folder:
```python
# All watchers follow BaseWatcher pattern:
# 1. check_for_updates() → list of new items
# 2. create_action_file(item) → .md file in Needs_Action/
# 3. run() → continuous loop with configurable interval
```

### 2. Ralph Wiggum Loop (Persistence)
Stop hook pattern that keeps Claude working autonomously:
- Intercepts Claude's exit attempt
- Checks if task is complete (file in `/Done/`)
- Re-injects prompt if incomplete → continues loop

### 3. Human-in-the-Loop (HITL)
For sensitive actions, Claude writes approval request files:
```
/Pending_Approval/PAYMENT_Client_A_2026-01-07.md
  → User moves to /Approved/ → Action executes
  → User moves to /Rejected/ → Action cancelled
```

### 4. Business Handover
Scheduled audits generate "Monday Morning CEO Briefing":
- Revenue summary
- Completed tasks
- Bottleneck analysis
- Proactive suggestions (cost optimization, deadlines)

## Development Conventions

### Obsidian Vault Structure
```
Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1 objectives, metrics
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Pending tasks
├── In_Progress/<agent>/      # Claimed by agent
├── Pending_Approval/         # Awaiting human decision
├── Approved/                 # Approved actions
├── Done/                     # Completed tasks
└── Briefings/                # Generated reports
```

### Agent Skills
All AI functionality should be implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - reusable, promptable capabilities for Claude Code.

## Running & Testing

### Playwright MCP Server
```bash
# Start
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### Qwen Code Commands
```bash
# Check version
qwen --version

# Start with Ralph loop
/ralph-loop "Process all files in /Needs_Action" --completion-promise "TASK_COMPLETE"
```

## Silver Tier Skills Usage

### Email MCP
```bash
# Send email (after approval)
python scripts/mcp-client.py call -u http://localhost:8809 -t email_send \
  -p '{"to": "client@example.com", "subject": "Hello", "body": "Message"}'
```

### WhatsApp Watcher
```bash
# Start monitoring
python scripts/whatsapp_watcher.py ./AI_Employee_Vault 30
```

### LinkedIn Poster
```bash
# Post to LinkedIn (after approval)
python scripts/linkedin_poster.py ./vault --post "Your content"
```

### Scheduler Setup
```bash
# Windows Task Scheduler - Daily briefing at 8 AM
schtasks /Create /TN "AI Employee" /TR "qwen 'Generate daily briefing'" /SC DAILY /ST 08:00
```

## Meeting Schedule

**Research & Showcase:** Every Wednesday at 10:00 PM PKT
- First meeting: Wednesday, January 7th, 2026
- Zoom: [Link in main document](Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md)
- YouTube backup: https://www.youtube.com/@panaversity

## References

- [Ralph Wiggum Stop Hook](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Odoo Integration](https://github.com/AlanOgic/mcp-odoo-adv)
- [Oracle Cloud Free VMs](https://www.oracle.com/cloud/free/)
