
C:\Users\Haya Javed\Downloads\Silver-Tier-Final\AI_Employee_Vault>python scripts/auto_orchestrator.py

←[1m←[94m======================================================================←[0m
←[1m←[94m                       GMAIL AUTO ORCHESTRATOR                        ←[0m
←[1m←[94m======================================================================←[0m


This automation will:
[OK] Check Gmail every 120 seconds
[OK] Create EMAIL_*.md in Needs_Action/
[OK] Auto-run Qwen to process emails
[OK] Create Plan.md in Plans/
[OK] Create Approval Request in Pending_Approval/
[OK] Send approved emails automatically

[!] YOUR TASK:
   Review files in Pending_Approval/ and move to Approved/


←[94mℹ️  Vault path: C:\Users\Haya Javed\Downloads\Silver-Tier-Final\AI_Employee_Vault←[0m
←[94mℹ️  Starting in 3 seconds... (Press Ctrl+C to cancel)←[0m

←[1m←[94m======================================================================←[0m
←[1m←[94m                      AUTO ORCHESTRATOR STARTED                       ←[0m
←[1m←[94m======================================================================←[0m

←[92m✅ Gmail Watcher: Running (120 second interval)←[0m
←[92m✅ Qwen Processing: Automatic (with -y flag)←[0m
←[92m✅ Email Sending: Automatic after approval←[0m
←[93m⚠️  Your ONLY Task:←[0m
←[93m⚠️    Move approval requests from Pending_Approval/ to Approved/←[0m
2026-03-20 21:41:50,346 - AutoOrchestrator - INFO - Auto Orchestrator started
2026-03-20 21:41:50,346 - AutoOrchestrator - INFO - Press Ctrl+C to stop
2026-03-20 21:41:50,346 - AutoOrchestrator - INFO -
=== Iteration 1 ===
2026-03-20 21:41:50,347 - AutoOrchestrator - INFO - Found 1 new email(s) to process
2026-03-20 21:41:50,347 - AutoOrchestrator - INFO - Starting Qwen processing...
2026-03-20 21:41:50,349 - AutoOrchestrator - INFO - Created prompt file: qwen_prompt_20260320_214150.txt
2026-03-20 21:41:50,349 - AutoOrchestrator - INFO - Running Qwen with -y flag for automatic processing...
2026-03-20 21:42:24,578 - AutoOrchestrator - INFO - Qwen processing complete
2026-03-20 21:42:24,579 - AutoOrchestrator - INFO - Qwen output: Done. Created both files:

1. **Plans/EMAIL_Eid_Plan.md** - Contains the plan with draft reply following Company Handbook rules (known contact, <50 words = auto-send eligible)

2. **Pending_Approval/EMAIL_REPLY_20260320_214150_Eid.md** - Approval request with the drafted Eid Mubarak reply

Move the
2026-03-20 21:42:24,580 - AutoOrchestrator - INFO - ✅ Qwen processing complete!
2026-03-20 21:42:24,581 - AutoOrchestrator - INFO - 📁 Approvals pending: 1
2026-03-20 21:42:24,581 - AutoOrchestrator - INFO - 👉 Check Pending_Approval/ folder in Obsidian
2026-03-20 21:42:24,591 - AutoOrchestrator - INFO - Dashboard updated
2026-03-20 21:42:24,591 - AutoOrchestrator - INFO - Waiting 120 seconds... (Press Ctrl+C to stop)
2026-03-20 21:44:24,592 - AutoOrchestrator - INFO -
=== Iteration 2 ===
2026-03-20 21:44:24,593 - AutoOrchestrator - INFO - No new emails
2026-03-20 21:44:29,612 - AutoOrchestrator - INFO - Found 1 approved email(s) to send
2026-03-20 21:44:31,749 - AutoOrchestrator - INFO - Email sending result: 2026-03-20 21:44:30,206 - GmailSender - INFO - Loaded existing OAuth token
2026-03-20 21:44:30,208 - googleapiclient.discovery_cache - INFO - file_cache is only supported with oauth2client<4.0.0
2026-
2026-03-20 21:44:31,760 - AutoOrchestrator - INFO - Dashboard updated
2026-03-20 21:44:31,761 - AutoOrchestrator - INFO - Waiting 120 seconds... (Press Ctrl+C to stop)