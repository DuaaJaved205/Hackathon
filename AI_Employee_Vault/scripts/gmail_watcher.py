"""
Gmail Watcher

Monitors Gmail for new unread messages and creates action files in the Needs_Action folder.
Uses the Gmail API to fetch messages.

Prerequisites:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download credentials.json (already placed in project root)
4. First run will authorize and create token.json

Usage:
    python gmail_watcher.py /path/to/vault

Environment Variables:
    GMAIL_CREDENTIALS_PATH: Path to credentials.json (default: ../../credentials.json)
"""

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from email.utils import parseaddr

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

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


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread messages and creates action files.

    Attributes:
        credentials_path (str): Path to OAuth credentials file
        token_path (str): Path to store OAuth token
        SCOPES (list): Required Gmail API scopes
        service: Gmail API service object
    """

    # Use gmail.modify scope to allow marking messages as read
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, vault_path: str, credentials_path: str = None, check_interval: int = 120):
        """
        Initialize Gmail Watcher.
        
        Args:
            vault_path (str): Path to Obsidian vault
            credentials_path (str): Path to credentials.json (default: ../../credentials.json)
            check_interval (int): Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail API libraries not installed")
        
        # Default credentials path - looks in project root
        if credentials_path:
            self.credentials_path = credentials_path
        else:
            self.credentials_path = os.getenv(
                'GMAIL_CREDENTIALS_PATH',
                str(Path(__file__).parent.parent.parent / 'credentials.json')
            )
        
        self.token_path = str(Path(__file__).parent / 'token.json')
        
        # Initialize Gmail service
        self.service = None
        self._authenticate()
        
        # Keywords that indicate high priority
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'important',
            'deadline', 'emergency', 'action required', 'review'
        ]
    
    def _authenticate(self):
        """
        Authenticate with Gmail API.
        
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
            self.logger.info("Gmail service initialized")
            return self.service
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return None
    
    def check_for_updates(self) -> list:
        """
        Check for new unread messages in Gmail.
        
        Returns:
            list: List of message dicts with id, snippet, and headers
        """
        if not self.service:
            self._authenticate()
            if not self.service:
                return []
        
        try:
            # Fetch unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
                    self.processed_ids.add(msg['id'])
            
            if new_messages:
                self.logger.info(f"Found {len(new_messages)} new message(s)")
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            # Try to re-authenticate
            self._authenticate()
            return []
    
    def _get_message_details(self, message_id: str) -> dict:
        """
        Get full message details.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            dict: Message details with headers and body
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            header_dict = {h['name'].lower(): h['value'] for h in headers}
            
            # Extract body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            elif 'body' in message['payload']:
                if message['payload']['body'].get('data'):
                    body = base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode('utf-8')
            
            # Check for attachments
            has_attachment = False
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part.get('filename', ''):
                        has_attachment = True
                        break
            
            return {
                'id': message_id,
                'from': header_dict.get('from', 'Unknown'),
                'to': header_dict.get('to', ''),
                'subject': header_dict.get('subject', 'No Subject'),
                'date': header_dict.get('date', ''),
                'snippet': message.get('snippet', ''),
                'body': body if body else message.get('snippet', ''),
                'has_attachment': has_attachment
            }
            
        except Exception as e:
            self.logger.error(f"Error getting message details: {e}")
            return None
    
    def _determine_priority(self, message: dict) -> str:
        """
        Determine message priority based on content.
        
        Args:
            message (dict): Message details
            
        Returns:
            str: 'high', 'medium', or 'low'
        """
        text = f"{message['subject']} {message['snippet']} {message['body']}".lower()
        
        # Check for priority keywords
        for keyword in self.priority_keywords:
            if keyword in text:
                return 'high'
        
        # Check if from known contact (simplified)
        sender_email = parseaddr(message['from'])[1]
        if sender_email:
            return 'medium'
        
        return 'low'
    
    def create_action_file(self, item: dict) -> Path:
        """
        Create an action file for a Gmail message.
        
        Args:
            item (dict): Gmail message dict with 'id' key
            
        Returns:
            Path: Path to created action file
        """
        # Get full message details
        message = self._get_message_details(item['id'])
        
        if not message:
            raise ValueError(f"Could not retrieve message {item['id']}")
        
        # Determine priority
        priority = self._determine_priority(message)
        
        # Parse sender
        sender_name, sender_email = parseaddr(message['from'])
        if not sender_name:
            sender_name = sender_email
        
        # Create filename
        subject_safe = self._sanitize_filename(message['subject'][:50])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"EMAIL_{timestamp}_{subject_safe}.md"
        
        # Create content
        content = f"""---
type: email
from: {message['from']}
from_email: {sender_email}
to: {message['to']}
subject: {message['subject']}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
message_id: {message['id']}
has_attachment: {message['has_attachment']}
---

# Email: {message['subject']}

**From:** {message['from']}  
**Received:** {message['date']}  
**Priority:** {priority.upper()}
**Has Attachment:** {message['has_attachment']}

---

## Content

{message['body'] if message['body'] else message['snippet']}

---

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create task from email
- [ ] Archive after processing

## Notes

_Add your notes here_

---

*Created by Gmail Watcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Write file
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')

        # Save processed ID immediately to prevent duplicates
        self.processed_ids.add(message['id'])
        self._save_processed_ids()

        # Mark message as read
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.info(f"Marked message {message['id']} as read")
        except Exception as e:
            self.logger.warning(f"Could not mark message as read: {e}")

        return filepath


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python gmail_watcher.py <vault_path> [check_interval]")
        print("\nExample:")
        print("  python gmail_watcher.py ./AI_Employee_Vault 120")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    
    try:
        watcher = GmailWatcher(vault_path, check_interval=check_interval)
        
        if watcher.service:
            watcher.run()
        else:
            print("\n❌ Failed to initialize Gmail watcher")
            print("\nTo fix:")
            print("1. Ensure credentials.json exists in project root")
            print("2. Check that Gmail API is enabled in Google Cloud Console")
            print("3. Run the script again to trigger OAuth flow")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo fix:")
        print("1. Go to Google Cloud Console")
        print("2. Enable Gmail API")
        print("3. Create OAuth 2.0 credentials (Desktop app)")
        print("4. Download credentials.json")
        print("5. Place in project root: C:\\Users\\Haya Javed\\Downloads\\Hackathon0\\")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nWatcher stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
