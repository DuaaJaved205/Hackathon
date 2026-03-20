"""
Gmail Sender

Sends emails via Gmail API with Human-in-the-Loop (HITL) approval workflow.
Used for Silver Tier AI Employee email automation.

Prerequisites:
1. Gmail API enabled in Google Cloud Console
2. OAuth credentials (credentials.json in project root)
3. OAuth token (token.json in scripts/ folder)

Usage:
    # Send email directly (for testing)
    python gmail_sender.py ./vault --to "recipient@example.com" --subject "Test" --body "Message"

    # Process approved emails from Approved/ folder
    python gmail_sender.py ./vault --process-approved

    # Create approval request (HITL mode)
    python gmail_sender.py ./vault --create-approval --to "client@example.com" --subject "Invoice" --body "Content"
"""

import os
import sys
import base64
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    GMAIL_AVAILABLE = True
except ImportError as e:
    GMAIL_AVAILABLE = False
    print(f"Error importing Gmail libraries: {e}")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)


class GmailSender:
    """
    Sends emails via Gmail API with HITL approval workflow.

    Attributes:
        vault_path (Path): Path to Obsidian vault
        credentials_path (str): Path to OAuth credentials
        token_path (str): Path to OAuth token
        service: Gmail API service object
        approved_folder (Path): Path to Approved folder
        pending_folder (Path): Path to Pending_Approval folder
        done_folder (Path): Path to Done folder
        logs_folder (Path): Path to Logs folder
    """

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, vault_path: str, credentials_path: str = None):
        """
        Initialize Gmail Sender.

        Args:
            vault_path (str): Path to Obsidian vault
            credentials_path (str): Path to credentials.json (optional)
        """
        self.vault_path = Path(vault_path)
        
        # Setup logging FIRST (before authentication)
        import logging
        self.logger = logging.getLogger('GmailSender')

        # Credentials
        if credentials_path:
            self.credentials_path = credentials_path
        else:
            self.credentials_path = os.getenv(
                'GMAIL_CREDENTIALS_PATH',
                str(Path(__file__).parent.parent.parent / 'credentials.json')
            )

        self.token_path = str(Path(__file__).parent / 'token.json')

        # Folders
        self.approved_folder = self.vault_path / 'Approved'
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_folder = self.vault_path / 'Plans'

        for folder in [self.approved_folder, self.pending_folder, self.done_folder, self.logs_folder, self.needs_action, self.plans_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # Initialize Gmail service
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with Gmail API for sending emails.

        Returns:
            Gmail API service object or None if authentication fails
        """
        try:
            creds = None

            # Load existing token
            if os.path.exists(self.token_path):
                try:
                    creds = Credentials.from_authorized_user_file(
                        self.token_path,
                        self.SCOPES
                    )
                    self.logger.info("Loaded existing OAuth token")
                except Exception as e:
                    self.logger.warning(f"Could not load token: {e}")
                    creds = None

            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        self.logger.info("Refreshed OAuth token")
                    except RefreshError:
                        self.logger.warning("Token refresh failed, re-authenticating")
                        creds = None

                if not creds:
                    if not os.path.exists(self.credentials_path):
                        self.logger.error(
                            f"Credentials file not found: {self.credentials_path}\n"
                            f"Please ensure credentials.json exists in project root"
                        )
                        return None

                    self.logger.info("Starting OAuth flow...")
                    self.logger.info(f"Using credentials: {self.credentials_path}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                    # Save token for future use
                    with open(self.token_path, 'w') as token:
                        token.write(creds.to_json())
                    self.logger.info("Authentication successful, token saved")

            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Gmail send service initialized")
            return self.service

        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return None

    def _create_message(self, to: str, subject: str, body: str, from_email: str = 'me',
                       attachments: list = None, in_reply_to: str = None):
        """
        Create a MIME message for sending.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body text
            from_email (str): Sender email (default: 'me')
            attachments (list): List of file paths to attach
            in_reply_to (str): Message ID to reply to

        Returns:
            str: Base64 encoded message
        """
        if attachments:
            message = MIMEMultipart()
            message.attach(MIMEText(body, 'plain'))

            for file_path in attachments:
                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{Path(file_path).name}"'
                    )
                    message.attach(part)
                except Exception as e:
                    self.logger.warning(f"Could not attach {file_path}: {e}")
        else:
            message = MIMEText(body)

        message['to'] = to
        message['from'] = from_email
        message['subject'] = subject

        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}

    def send_email(self, to: str, subject: str, body: str,
                   attachments: list = None, in_reply_to: str = None) -> bool:
        """
        Send an email via Gmail API.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body text
            attachments (list): List of file paths to attach
            in_reply_to (str): Message ID to reply to

        Returns:
            bool: True if sent successfully
        """
        if not self.service:
            self.logger.error("Gmail service not initialized")
            return False

        try:
            message = self._create_message(to, subject, body, attachments=attachments,
                                          in_reply_to=in_reply_to)

            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            self.logger.info(f"Email sent to {to} with subject: {subject}")
            self.logger.info(f"Message ID: {sent_message['id']}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False

    def create_approval_request(self, to: str, subject: str, body: str,
                               attachments: list = None, priority: str = 'medium') -> Path:
        """
        Create approval request file for an email.

        Args:
            to (str): Recipient email
            subject (str): Email subject
            body (str): Email body
            attachments (list): List of attachment paths
            priority (str): Priority level

        Returns:
            Path: Path to created approval file
        """
        timestamp = datetime.now()
        request_id = f"EMAIL_SEND_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        # Preview body (first 200 chars)
        preview = body[:200] + "..." if len(body) > 200 else body

        approval_content = f"""---
type: approval_request
id: {request_id}
action: email_send
created: {timestamp.isoformat()}
expires: {(timestamp + timedelta(hours=48)).isoformat()}
priority: {priority}
status: pending
---

# Email Send Approval Request

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Expires:** {(timestamp + timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S')}

---

## Email Details

| Field | Value |
|-------|-------|
| **To:** | {to} |
| **Subject:** | {subject} |
| **Priority:** | {priority.title()} |
| **Attachments:** | {', '.join(attachments) if attachments else 'None'} |

---

## Email Content

{body}

---

## Company Handbook Rules Applied

- ✅ All emails to new contacts require approval
- ✅ Emails with attachments require approval
- ✅ Bulk emails (>10 recipients) require approval
- ⚠️ Financial documents require approval

---

## Decision Required

### To Approve
**Move this file to:** `/Approved/`

The email will be sent within 5 minutes.

### To Reject
**Move this file to:** `/Rejected/`

**Please add rejection reason below:**
```markdown
## Rejection Reason
[Add your reason here]
```

### To Request Changes
**Add a comment below and keep in Pending_Approval/**

---

## Audit Trail

| Timestamp | Event | Actor |
|-----------|-------|-------|
| {timestamp.isoformat()} | Created | Gmail Sender |
"""

        # Write approval file
        filepath = self.pending_folder / f"{request_id}.md"
        filepath.write_text(approval_content, encoding='utf-8')

        self.logger.info(f"Created approval request: {filepath.name}")

        return filepath

    def process_approved_emails(self):
        """
        Process all approved email requests in Approved/ folder.

        Returns:
            int: Number of emails processed
        """
        emails_sent = 0

        # Look for both EMAIL_SEND_*.md and EMAIL_REPLY_*.md patterns
        approved_files = list(self.approved_folder.glob('EMAIL_SEND_*.md'))
        approved_files += list(self.approved_folder.glob('EMAIL_REPLY_*.md'))

        for filepath in approved_files:
            try:
                content = filepath.read_text(encoding='utf-8')

                # Parse email details from markdown
                email_data = self._parse_approval_file(content)

                if not email_data:
                    self.logger.warning(f"Could not parse {filepath.name}")
                    continue

                # Get related email and plan from approval file
                related_email = None
                related_plan = None
                
                if 'related_email:' in content:
                    related_email = content.split('related_email:')[1].split('\n')[0].strip()
                if 'related_to:' in content:
                    related_email = content.split('related_to:')[1].split('\n')[0].strip()
                if 'related_plan:' in content:
                    related_plan = content.split('related_plan:')[1].split('\n')[0].strip()

                # Send email
                self.logger.info(f"Sending email: {filepath.name}")
                success = self.send_email(
                    to=email_data['to'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    attachments=email_data.get('attachments'),
                    in_reply_to=email_data.get('in_reply_to')
                )

                if success:
                    # Log action
                    self._log_action(filepath.name, 'sent', email_data)

                    # Move to Done
                    done_path = self.done_folder / filepath.name
                    filepath.rename(done_path)
                    self.logger.info(f"Email sent, moved to Done/: {done_path.name}")

                    # Delete related email from Needs_Action/
                    if related_email:
                        needs_action_email = self.needs_action / related_email
                        if needs_action_email.exists():
                            needs_action_email.unlink()
                            self.logger.info(f"Deleted: {related_email}")

                    # Delete related plan from Plans/
                    if related_plan:
                        # Handle both full path and just filename
                        if '/' in related_plan or '\\' in related_plan:
                            plan_path = self.vault_path / related_plan.replace('/', '\\')
                        else:
                            plan_path = self.plans_folder / related_plan
                        if plan_path.exists():
                            plan_path.unlink()
                            self.logger.info(f"Deleted plan: {related_plan}")

                    emails_sent += 1
                else:
                    self.logger.error(f"Failed to send: {filepath.name}")

            except Exception as e:
                self.logger.error(f"Error processing {filepath.name}: {e}")

        return emails_sent

    def _parse_approval_file(self, content: str) -> dict:
        """Parse email details from approval file."""
        email_data = {}
        
        # Try new format first (Qwen-created)
        if '**From:**' in content:
            # Extract From (this is who we reply to)
            from_field = content.split('**From:**')[1].split('\n')[0].strip()
            # Remove any arrow comments like "← Reply to this person"
            if '←' in from_field:
                from_field = from_field.split('←')[0].strip()
            # Extract email from "Name <email@domain.com>" format
            import re
            email_match = re.search(r'<([^>]+)>', from_field)
            if email_match:
                email_data['to'] = email_match.group(1)  # Reply to sender's email
            else:
                email_data['to'] = from_field  # Use as-is if no angle brackets
            
            # Extract original recipient (for reference)
            if '**To:**' in content:
                to_field = content.split('**To:**')[1].split('\n')[0].strip()
                if '←' in to_field:
                    to_field = to_field.split('←')[0].strip()
                email_data['original_to'] = to_field
            
            # Extract subject
            if '**Subject:**' in content:
                email_data['subject'] = content.split('**Subject:**')[1].split('\n')[0].strip()
            
            # Extract body - try multiple formats
            # Format 1: Inside code block after "Draft Reply"
            if '## Draft Reply' in content:
                draft_section = content.split('## Draft Reply')[1]
                # Try code block first
                if '```' in draft_section:
                    parts = draft_section.split('```')
                    if len(parts) > 1:
                        email_data['body'] = parts[1].strip()
                else:
                    # No code block - get text between "## Draft Reply" and next "##" or "---"
                    body_text = draft_section.split('##')[0] if '##' in draft_section else draft_section
                    body_text = body_text.split('---')[0] if '---' in body_text else body_text
                    # Remove "To Approve" and other sections
                    if 'To Approve' in body_text:
                        body_text = body_text.split('To Approve')[0]
                    email_data['body'] = body_text.strip()
                
                # Clean up body - remove "From:", "To:", "Subject:" lines if present
                if 'body' in email_data:
                    body_lines = email_data['body'].split('\n')
                    clean_lines = [l for l in body_lines if not l.strip().startswith('From:') and not l.strip().startswith('To:') and not l.strip().startswith('Subject:')]
                    email_data['body'] = '\n'.join(clean_lines).strip()
            
            # Format 2: Direct body in markdown
            if 'body' not in email_data and '**Body:**' in content:
                body_section = content.split('**Body:**')[1]
                if '```' in body_section:
                    parts = body_section.split('```')
                    if len(parts) > 1:
                        email_data['body'] = parts[1].strip()
                else:
                    email_data['body'] = body_section.split('\n\n')[0].strip()
        else:
            # Try old format (table-based)
            if '| **To:** |' in content:
                email_data['to'] = content.split('| **To:** |')[1].split('|')[0].strip()
            if '| **Subject:** |' in content:
                email_data['subject'] = content.split('| **Subject:** |')[1].split('|')[0].strip()
            if '## Email Content' in content:
                email_data['body'] = content.split('## Email Content')[1].split('---')[0].strip()

        # Extract attachments
        if '| **Attachments:** |' in content or '**Attachments:**' in content:
            if '| **Attachments:** |' in content:
                attachments_str = content.split('| **Attachments:** |')[1].split('|')[0].strip()
            else:
                attachments_str = content.split('**Attachments:**')[1].split('\n')[0].strip()
            
            if attachments_str.lower() != 'none' and attachments_str:
                email_data['attachments'] = [a.strip() for a in attachments_str.split(',')]
            else:
                email_data['attachments'] = []
        else:
            email_data['attachments'] = []

        return email_data

    def _log_action(self, filename: str, action: str, email_data: dict):
        """Log action to audit trail."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'action': action,
            'to': email_data.get('to'),
            'subject': email_data.get('subject')
        }

        # Append to daily log
        log_file = self.logs_folder / f"gmail_{datetime.now().strftime('%Y-%m-%d')}.json"

        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []

        logs.append(log_entry)

        try:
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            self.logger.error(f"Error writing log: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gmail Sender for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--to', type=str, help='Recipient email address')
    parser.add_argument('--subject', type=str, help='Email subject')
    parser.add_argument('--body', type=str, help='Email body text')
    parser.add_argument('--attachments', type=str, nargs='+', help='Attachment file paths')
    parser.add_argument('--in-reply-to', type=str, help='Message ID to reply to')
    parser.add_argument('--priority', type=str, default='medium',
                       choices=['low', 'medium', 'high'], help='Priority level')
    parser.add_argument('--create-approval', action='store_true',
                       help='Create approval request (HITL mode)')
    parser.add_argument('--process-approved', action='store_true',
                       help='Process all approved emails')
    parser.add_argument('--send-direct', action='store_true',
                       help='Send email directly without approval (testing only)')

    args = parser.parse_args()

    # Setup logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('GmailSender')

    if not GMAIL_AVAILABLE:
        print("\n❌ Gmail API libraries not installed")
        print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        sys.exit(1)

    sender = GmailSender(args.vault_path)

    if not sender.service:
        print("\n❌ Failed to initialize Gmail sender")
        print("\nTo fix:")
        print("1. Ensure credentials.json exists in project root")
        print("2. Run gmail_watcher.py first to authenticate")
        sys.exit(1)

    try:
        # Process approved emails
        if args.process_approved:
            count = sender.process_approved_emails()
            print(f"✅ Processed {count} email(s)")
            return

        # Send direct (testing only)
        if args.send_direct and args.to and args.subject and args.body:
            print(f"📧 Sending email directly to {args.to}...")
            success = sender.send_email(
                to=args.to,
                subject=args.subject,
                body=args.body,
                attachments=args.attachments,
                in_reply_to=args.in_reply_to
            )
            if success:
                print("✅ Email sent successfully!")
            else:
                print("❌ Failed to send email")
            return

        # Create approval request
        if args.create_approval and args.to and args.subject and args.body:
            filepath = sender.create_approval_request(
                to=args.to,
                subject=args.subject,
                body=args.body,
                attachments=args.attachments,
                priority=args.priority
            )
            print(f"✅ Approval request created: {filepath.name}")
            print("Move to Approved/ to send")
            return

        # Default: show help
        parser.print_help()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
