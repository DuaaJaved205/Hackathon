# -*- coding: utf-8 -*-
"""
Auto Orchestrator - Gmail Workflow Automation

Fully automated Gmail workflow:
1. Gmail Watcher checks emails every 120 seconds
2. Creates EMAIL_*.md in Needs_Action/
3. Qwen automatically processes emails
4. Creates Plan.md and Approval Request automatically
5. Human only needs to approve (move to Approved/)
6. Auto-sends approved emails

Usage:
    python auto_orchestrator.py
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
import threading

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


class AutoOrchestrator:
    """
    Automated Orchestrator for Gmail Workflow.
    
    Automatically:
    1. Runs Gmail Watcher (every 120 seconds)
    2. Detects new emails in Needs_Action/
    3. Triggers Qwen to process emails
    4. Creates Plan.md and Approval Requests
    5. Sends approved emails
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_folder = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.needs_action, self.plans_folder, 
                       self.pending_approval, self.approved_folder, 
                       self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files = set()
        self._load_processed_cache()
        
        # Qwen prompt template
        self.qwen_prompt = """
Process all emails in Needs_Action/ folder.

For EACH email file, follow this workflow EXACTLY:

Step 1: Read the email file (from, to, subject, content)
Step 2: Check Company_Handbook.md for applicable rules
Step 3: Create ONE Plan.md in Plans/ folder
        - Use template from Company_Handbook
        - Link to original email
Step 4: Create ONE Approval Request in Pending_Approval/
        - Draft appropriate reply based on Company_Handbook rules
        - Include all required fields
Step 5: Do NOT send yet - wait for human approval

Rules:
- ONE Plan.md per email (check if already exists)
- ONE Approval Request per email (check if already exists)
- Follow Company_Handbook.md guidelines
- Be professional and concise

After processing, update Dashboard.md with:
- Number of emails processed
- Number of approval requests created
"""
        
        import logging
        self.logger = logging.getLogger('AutoOrchestrator')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_processed_cache(self):
        """Load processed file IDs from cache."""
        cache_file = self.vault_path / '.cache' / 'auto_orchestrator_processed.json'
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.processed_files = set(json.load(f))
                self.logger.info(f"Loaded {len(self.processed_files)} processed files from cache")
            except:
                self.processed_files = set()
    
    def _save_processed_cache(self):
        """Save processed file IDs to cache."""
        cache_file = self.vault_path / '.cache' / 'auto_orchestrator_processed.json'
        try:
            with open(cache_file, 'w') as f:
                json.dump(list(self.processed_files), f)
        except Exception as e:
            self.logger.warning(f"Could not save cache: {e}")
    
    def check_needs_action(self):
        """Check for new emails in Needs_Action/."""
        if not self.needs_action.exists():
            return []
        
        email_files = list(self.needs_action.glob('EMAIL_*.md'))
        new_emails = []
        
        for email_file in email_files:
            if email_file.name not in self.processed_files:
                new_emails.append(email_file)
        
        return new_emails
    
    def check_gmail_permission_error(self):
        """Check if Gmail is returning permission errors."""
        try:
            # Try to run gmail_watcher briefly to check for errors
            result = subprocess.run(
                [sys.executable, 'scripts/gmail_watcher.py', '.', '1'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            output = result.stdout + result.stderr
            
            if 'insufficientPermissions' in output or '403 Forbidden' in output:
                self.logger.warning("Gmail permission error detected!")
                self.logger.warning("OAuth token has wrong scope.")
                self.logger.warning("Run: del scripts\\token.json")
                self.logger.warning("Then: python scripts/gmail_watcher.py . 10")
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def run_qwen_processing(self):
        """
        Trigger Qwen to process emails automatically.
        Uses -y flag for automatic file creation.
        """
        self.logger.info("Starting Qwen processing...")
        
        # Check for new emails that need processing
        new_emails = self.check_needs_action()
        
        if not new_emails:
            self.logger.info("No new emails to process")
            return True
        
        # Build email list for prompt
        email_list = ", ".join([e.name for e in new_emails])
        
        # Create Qwen prompt
        qwen_prompt = f"""
Process these {len(new_emails)} email(s) in Needs_Action/ folder:
{email_list}

For EACH email, you MUST create TWO files:

FILE 1 - Plan.md in Plans/ folder:
- Read the email (from, subject, content)
- Check Company_Handbook.md for rules
- Create a plan with draft reply
- Filename: Plans/EMAIL_<subject>_Plan.md

FILE 2 - Approval Request in Pending_Approval/ folder:
- MUST create this file even if auto-send eligible
- Use filename: EMAIL_REPLY_<timestamp>_<subject>.md
- MUST include these fields in frontmatter:
  - related_to: <original email filename>
  - related_plan: <plan filename you created>
- Include: to, from, subject, draft body, approval instructions

IMPORTANT - EMAIL REPLY FORMAT:
When replying to an email:
- **From:** [Original Sender - who you reply TO]
- **To:** [Original Recipient - for reference only]
- **Subject:** Re: [Original Subject]

Example:
If email is FROM: John <john@example.com>
         TO:   you@company.com
Then reply TO: john@example.com (the original sender)

Approval request format:
```markdown
---
type: email_reply_approval
related_to: EMAIL_20260320_120000_Subject.md
related_plan: Plans/EMAIL_Subject_Plan.md
---

# Approval Request: Email Reply

**From:** John <john@example.com>  ← Reply to this person
**To:** you@company.com  ← Original recipient (reference)
**Subject:** Re: Original Subject

## Draft Reply

Your drafted reply here...

---
## To Approve
Move this file to /Approved/ folder.
```

Now process the emails and create BOTH files for each.
"""
        
        # Create prompt file
        prompt_file = self.vault_path / '.cache' / f'qwen_prompt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        prompt_file.write_text(qwen_prompt, encoding='utf-8')
        
        self.logger.info(f"Created prompt file: {prompt_file.name}")
        self.logger.info("Running Qwen with -y flag for automatic processing...")
        
        # Run Qwen automatically with -y flag
        try:
            # Use full path to qwen.cmd on Windows
            import platform
            if platform.system() == 'Windows':
                qwen_cmd = ['qwen.cmd']
            else:
                qwen_cmd = ['qwen']
            
            result = subprocess.run(
                qwen_cmd + [f'@{prompt_file}', '-y'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                encoding='utf-8'
            )
            
            output = result.stdout + result.stderr
            
            # Log output
            self.logger.info("Qwen processing complete")
            
            # Save output to log
            log_file = self.logs_folder / f'qwen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            log_file.write_text(output, encoding='utf-8')
            
            # Check for errors
            if 'Error' in output or 'error' in output:
                self.logger.warning(f"Qwen output contains errors: {output[:200]}")
            else:
                self.logger.info(f"Qwen output: {output[:300]}")
            
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.warning("Qwen processing timed out (5 minutes)")
            return False
        except FileNotFoundError:
            self.logger.error("Qwen Code not found. Please install: npm install -g qwen-code")
            return False
        except Exception as e:
            self.logger.error(f"Error running Qwen: {e}")
            return False
    
    def process_approved_emails(self):
        """Send approved emails."""
        # Look for both EMAIL_SEND_*.md and EMAIL_REPLY_*.md patterns
        approved_files = list(self.approved_folder.glob('EMAIL_SEND_*.md'))
        approved_files += list(self.approved_folder.glob('EMAIL_REPLY_*.md'))
        
        if not approved_files:
            return 0
        
        self.logger.info(f"Found {len(approved_files)} approved email(s) to send")
        
        try:
            # Run gmail_sender.py
            result = subprocess.run(
                [sys.executable, 'scripts/gmail_sender.py', '.', '--process-approved'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            )
            
            output = result.stdout + result.stderr
            self.logger.info(f"Email sending result: {output[:200]}")
            
            # Count sent emails
            sent_count = output.count('✅')
            return sent_count
            
        except Exception as e:
            self.logger.error(f"Error sending emails: {e}")
            return 0
    
    def mark_as_processed(self, email_files):
        """Mark files as processed."""
        for email_file in email_files:
            self.processed_files.add(email_file.name)
        self._save_processed_cache()
    
    def update_dashboard(self, emails_count, approvals_count, sent_count):
        """Update Dashboard.md with current status."""
        dashboard = self.vault_path / 'Dashboard.md'
        
        if not dashboard.exists():
            return
        
        try:
            content = dashboard.read_text(encoding='utf-8')
        except:
            # Fallback to default encoding if utf-8 fails
            content = dashboard.read_text()
        
        # Update timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add status update
        status_update = f"""

---

## Latest Auto-Processing Update
**Time:** {timestamp}
- Emails processed: {emails_count}
- Approval requests created: {approvals_count}
- Emails sent: {sent_count}
"""
        
        # Append to dashboard
        if '## Latest Auto-Processing Update' not in content:
            content += status_update
        else:
            # Replace last update
            parts = content.split('## Latest Auto-Processing Update')
            content = parts[0] + status_update
        
        try:
            dashboard.write_text(content, encoding='utf-8')
        except:
            dashboard.write_text(content)
        
        self.logger.info("Dashboard updated")
    
    def run(self):
        """Main run loop."""
        print_header("AUTO ORCHESTRATOR STARTED")

        print_success("Gmail Watcher: Running (120 second interval)")
        print_success("Qwen Processing: Automatic (with -y flag)")
        print_success("Email Sending: Automatic after approval")
        print_warning("Your ONLY Task:")
        print_warning("  Move approval requests from Pending_Approval/ to Approved/")

        self.logger.info("Auto Orchestrator started")
        self.logger.info("Press Ctrl+C to stop")

        iteration = 0

        try:
            while True:
                iteration += 1
                self.logger.info(f"\n=== Iteration {iteration} ===")

                # Step 1: Check for new emails
                new_emails = self.check_needs_action()

                if new_emails:
                    self.logger.info(f"Found {len(new_emails)} new email(s) to process")

                    # Step 2: Run Qwen processing (automatic with -y flag)
                    success = self.run_qwen_processing()

                    if success:
                        # Mark as processed
                        self.mark_as_processed(new_emails)

                        # Count approvals created (check both patterns)
                        approvals_count = len(list(self.pending_approval.glob('EMAIL_REPLY_*.md')))
                        approvals_count += len(list(self.pending_approval.glob('EMAIL_SEND_*.md')))

                        self.logger.info(f"✅ Qwen processing complete!")
                        self.logger.info(f"📁 Approvals pending: {approvals_count}")
                        self.logger.info(f"👉 Check Pending_Approval/ folder in Obsidian")
                    else:
                        self.logger.warning("Qwen processing failed")
                else:
                    self.logger.info("No new emails")
                    # Check for Gmail permission errors
                    if self.check_gmail_permission_error():
                        self.logger.error("⚠️  GMAIL PERMISSION ERROR DETECTED!")
                        self.logger.error("⚠️  To fix, run these commands:")
                        self.logger.error("⚠️    del scripts\\token.json")
                        self.logger.error("⚠️    python scripts/gmail_watcher.py . 10")

                # Step 3: Process approved emails
                sent_count = self.process_approved_emails()

                if sent_count > 0:
                    self.logger.info(f"✅ Sent {sent_count} email(s)")
                
                # Step 4: Update dashboard
                self.update_dashboard(
                    emails_count=len(new_emails),
                    approvals_count=len(list(self.pending_approval.glob('EMAIL_SEND_*.md'))),
                    sent_count=sent_count
                )
                
                # Step 5: Wait 120 seconds
                self.logger.info(f"Waiting 120 seconds... (Press Ctrl+C to stop)")
                time.sleep(120)
                
        except KeyboardInterrupt:
            self.logger.info("\nAuto Orchestrator stopped by user")
            self._save_processed_cache()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            raise


def main():
    """Main entry point."""
    print_header("GMAIL AUTO ORCHESTRATOR")
    
    print("""
This automation will:
[OK] Check Gmail every 120 seconds
[OK] Create EMAIL_*.md in Needs_Action/
[OK] Auto-run Qwen to process emails
[OK] Create Plan.md in Plans/
[OK] Create Approval Request in Pending_Approval/
[OK] Send approved emails automatically

[!] YOUR TASK:
   Review files in Pending_Approval/ and move to Approved/

""")
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default to current directory
        vault_path = '.'
    
    vault_path = Path(vault_path).resolve()
    
    print_info(f"Vault path: {vault_path}")
    print_info("Starting in 3 seconds... (Press Ctrl+C to cancel)")
    time.sleep(3)
    
    try:
        orchestrator = AutoOrchestrator(str(vault_path))
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
