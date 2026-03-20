"""
LinkedIn Watcher

Monitors LinkedIn for notifications, messages, and engagement opportunities.
Uses Playwright for LinkedIn Web automation.

Prerequisites:
1. Playwright installed: pip install playwright
2. Chromium browser: playwright install chromium
3. LinkedIn account credentials

Usage:
    python linkedin_watcher.py /path/to/vault

Note: Be mindful of LinkedIn's Terms of Service when automating.
      Use reasonable intervals to avoid rate limiting.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for notifications and messages.
    
    Attributes:
        session_path (str): Path to store browser session
        login_url (str): LinkedIn login URL
        keywords (list): Keywords to monitor for
    """
    
    def __init__(self, vault_path: str, check_interval: int = 300, headless: bool = False):
        """
        Initialize LinkedIn Watcher.
        
        Args:
            vault_path (str): Path to Obsidian vault
            check_interval (int): Seconds between checks (default: 300 = 5 min)
            headless (bool): Run browser in headless mode (default: False for first run)
        """
        super().__init__(vault_path, check_interval)
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed")
        
        # Session storage
        self.session_path = self.vault_path / '.cache' / 'linkedin_session'
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if this is first run (no session)
        self.is_first_run = not (self.session_path / 'Default').exists()
        
        # Use visible browser on first run for login
        self.headless = headless if not self.is_first_run else False
        if self.is_first_run:
            self.logger.info("First run detected - will open visible browser for login")
        
        # URLs
        self.login_url = 'https://www.linkedin.com/login'
        self.feed_url = 'https://www.linkedin.com/feed/'
        self.notifications_url = 'https://www.linkedin.com/notifications/'
        self.messaging_url = 'https://www.linkedin.com/messaging/'
        
        # Keywords for monitoring
        self.keywords = {
            'high': ['hiring', 'opportunity', 'interview', 'job', 'position', 'contract'],
            'medium': ['connection', 'message', 'comment', 'post', 'share'],
            'low': ['like', 'view', 'follower']
        }
        
        # Track processed notifications
        self.last_check_time = datetime.now()
    
    def _login_to_linkedin(self, page):
        """
        Login to LinkedIn if not already logged in.
        
        Args:
            page: Playwright page object
        """
        try:
            # Check if already logged in by looking for feed
            page.goto(self.feed_url, timeout=30000)
            
            # Wait a moment to see if we're redirected to login
            page.wait_for_timeout(3000)
            
            # If we're on login page, need to authenticate
            if 'login' in page.url:
                self.logger.info("Not logged in. Please login manually in the browser.")
                self.logger.info("Session will be saved for future runs.")
                
                # Wait for user to login manually (max 2 minutes)
                try:
                    page.wait_for_url('https://www.linkedin.com/feed/*', timeout=120000)
                    self.logger.info("Login successful!")
                    
                    # Save session
                    context = page.context
                    context.storage_state(path=str(self.session_path / 'storage.json'))
                    
                except PlaywrightTimeout:
                    self.logger.error("Login timeout. Please run again and login promptly.")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def _get_notifications(self, page) -> list:
        """
        Get recent notifications from LinkedIn.
        
        Args:
            page: Playwright page object
            
        Returns:
            list: List of notification dicts
        """
        notifications = []
        
        try:
            # Navigate to notifications
            page.goto(self.notifications_url, timeout=30000)
            page.wait_for_timeout(5000)  # Wait for content to load
            
            # Find notification elements (selectors may need updates)
            notification_elements = page.query_selector_all('div.notification-item')
            
            for elem in notification_elements[:10]:  # Limit to 10 recent
                try:
                    text = elem.inner_text()
                    timestamp_elem = elem.query_selector('time')
                    
                    notification = {
                        'type': 'notification',
                        'text': text,
                        'timestamp': timestamp_elem.get_attribute('datetime') if timestamp_elem else None,
                        'priority': self._get_priority(text)
                    }
                    
                    # Only include if matches keywords
                    if notification['priority'] != 'low':
                        notifications.append(notification)
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing notification: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error getting notifications: {e}")
        
        return notifications
    
    def _get_messages(self, page) -> list:
        """
        Get recent messages from LinkedIn.
        
        Args:
            page: Playwright page object
            
        Returns:
            list: List of message dicts
        """
        messages = []
        
        try:
            # Navigate to messaging
            page.goto(self.messaging_url, timeout=30000)
            page.wait_for_timeout(5000)
            
            # Find conversation elements
            conversations = page.query_selector_all('div.conversation-item')
            
            for conv in conversations[:5]:  # Limit to 5 recent
                try:
                    text = conv.inner_text()
                    
                    # Check if unread
                    is_unread = 'unread' in text.lower() or conv.get_attribute('aria-selected') == 'true'
                    
                    if is_unread:
                        message = {
                            'type': 'message',
                            'text': text,
                            'priority': self._get_priority(text)
                        }
                        messages.append(message)
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing message: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error getting messages: {e}")
        
        return messages
    
    def _get_priority(self, text: str) -> str:
        """
        Determine priority based on content.
        
        Args:
            text (str): Notification/message text
            
        Returns:
            str: 'high', 'medium', or 'low'
        """
        text_lower = text.lower()
        
        # Check high priority keywords
        for keyword in self.keywords['high']:
            if keyword in text_lower:
                return 'high'
        
        # Check medium priority keywords
        for keyword in self.keywords['medium']:
            if keyword in text_lower:
                return 'medium'
        
        return 'low'
    
    def check_for_updates(self) -> list:
        """
        Check LinkedIn for new notifications and messages.
        
        Returns:
            list: List of new items to process
        """
        items = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                # Visible browser on first run for login, headless afterwards
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Login if needed
                if not self._login_to_linkedin(page):
                    browser.close()
                    return []
                
                # Get notifications
                notifications = self._get_notifications(page)
                items.extend(notifications)
                
                # Get messages
                messages = self._get_messages(page)
                items.extend(messages)
                
                browser.close()
                
                # Filter out already processed (by text hash)
                new_items = []
                for item in items:
                    item_id = self._generate_unique_id(item['text'])
                    if item_id not in self.processed_ids:
                        item['id'] = item_id
                        new_items.append(item)
                        self.processed_ids.add(item_id)
                
                if new_items:
                    self.logger.info(f"Found {len(new_items)} new LinkedIn item(s)")
                
                return new_items
                
        except Exception as e:
            self.logger.error(f"Error checking LinkedIn: {e}")
            return []
    
    def create_action_file(self, item: dict) -> Path:
        """
        Create an action file for a LinkedIn item.
        
        Args:
            item (dict): LinkedIn notification/message dict
            
        Returns:
            Path: Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        item_type = item.get('type', 'unknown')
        priority = item.get('priority', 'medium')
        
        # Create filename
        safe_text = self._sanitize_filename(item['text'][:40])
        filename = f"LINKEDIN_{item_type.upper()}_{timestamp}_{safe_text}.md"
        
        # Determine suggested actions based on type and priority
        suggested_actions = []
        if item_type == 'message':
            suggested_actions = [
                "Reply to message",
                "Schedule follow-up",
                "Save contact information"
            ]
        elif 'hiring' in item['text'].lower() or 'opportunity' in item['text'].lower():
            suggested_actions = [
                "Review opportunity details",
                "Prepare response",
                "Update profile if interested"
            ]
        elif 'connection' in item['text'].lower():
            suggested_actions = [
                "Accept connection request",
                "Send personalized message",
                "Review profile"
            ]
        else:
            suggested_actions = [
                "Review notification",
                "Take action if needed"
            ]
        
        # Create content
        content = f"""---
type: linkedin_{item_type}
source: LinkedIn
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
item_id: {item.get('id', 'unknown')}
---

# LinkedIn {item_type.title()}

**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Priority:** {priority.upper()}  
**Type:** {item_type}

---

## Content

{item['text']}

---

## Suggested Actions

{chr(10).join(f'- [ ] {action}' for action in suggested_actions)}

## Notes

_Add your notes here_

---

*Created by LinkedIn Watcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Write file
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        
        return filepath
    
    def run(self):
        """
        Main run loop for the LinkedIn watcher.
        
        Note: First run requires manual login.
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Session path: {self.session_path}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info("First run: You'll need to login manually")
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f"Processing {len(items)} item(s)")
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                self.logger.info(f"Created: {filepath.name}")
                            except Exception as e:
                                self.logger.error(f"Error creating action file: {e}")
                    
                    self._save_processed_ids()
                    
                except Exception as e:
                    self.logger.error(f"Error in check loop: {e}")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f"{self.__class__.__name__} stopped by user")
            self._save_processed_ids()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            self._save_processed_ids()
            raise


# Import time for the run loop
import time


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python linkedin_watcher.py <vault_path> [check_interval]")
        print("\nExample:")
        print("  python linkedin_watcher.py ./AI_Employee_Vault 300")
        print("\nNote: Check interval minimum 300 seconds (5 min) recommended")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    # Enforce minimum interval to avoid rate limiting
    if check_interval < 300:
        print("⚠️  Warning: Check interval increased to 300 seconds (5 min)")
        print("   This is to avoid LinkedIn rate limiting")
        check_interval = 300
    
    try:
        watcher = LinkedInWatcher(vault_path, check_interval)
        watcher.run()
    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo fix:")
        print("  pip install playwright")
        print("  playwright install chromium")
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
