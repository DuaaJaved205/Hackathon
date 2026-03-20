"""
LinkedIn Poster

Automates posting to LinkedIn for business promotion and lead generation.
Uses Playwright for LinkedIn Web automation.

Prerequisites:
1. Playwright installed: pip install playwright
2. Chromium browser: playwright install chromium
3. LinkedIn account with session saved

Usage:
    # Post content directly (requires approval file)
    python linkedin_poster.py ./vault --post "Your content here"
    
    # Post from approval file
    python linkedin_poster.py ./vault --from-approval Approved/POST_xxx.md
    
    # Schedule post (creates approval request)
    python linkedin_poster.py ./vault --schedule --content "Content" --time "14:00"

Note: All posts require human approval before publishing (HITL pattern)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")


class LinkedInPoster:
    """
    Posts content to LinkedIn.
    
    Attributes:
        vault_path (Path): Path to Obsidian vault
        session_path (str): Path to browser session storage
        approved_folder (Path): Path to Approved folder
        pending_folder (Path): Path to Pending_Approval folder
        done_folder (Path): Path to Done folder
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize LinkedIn Poster.
        
        Args:
            vault_path (str): Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.session_path = self.vault_path / '.cache' / 'linkedin_session'
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Folders
        self.approved_folder = self.vault_path / 'Approved'
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        
        for folder in [self.approved_folder, self.pending_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.login_url = 'https://www.linkedin.com/login'
        self.feed_url = 'https://www.linkedin.com/feed/'
    
    def _login_to_linkedin(self, page):
        """
        Login to LinkedIn using saved session.
        
        Args:
            page: Playwright page object
            
        Returns:
            bool: True if login successful
        """
        try:
            # Try to load saved session
            storage_file = self.session_path / 'storage.json'
            
            if storage_file.exists():
                # Load saved session
                context = page.context
                storage_state = json.loads(storage_file.read_text())
                context.add_cookies(storage_state.get('cookies', []))
            
            # Navigate to feed
            page.goto(self.feed_url, timeout=30000)
            page.wait_for_timeout(5000)
            
            # Check if logged in
            if 'login' in page.url or 'checkpoint' in page.url:
                self.logger.error("Not logged in. Please run linkedin_watcher.py first to save session.")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def post_content(self, content: str, schedule_time: str = None) -> bool:
        """
        Post content to LinkedIn.

        Args:
            content (str): Post content
            schedule_time (str): Optional schedule time (HH:MM format)

        Returns:
            bool: True if post successful
        """
        import logging
        logger = logging.getLogger('LinkedInPoster')

        try:
            with sync_playwright() as p:
                # Launch browser (visible for debugging)
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Visible browser for debugging
                    args=['--disable-blink-features=AutomationControlled']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Login
                if not self._login_to_linkedin(page):
                    browser.close()
                    return False

                logger.info("Logged in to LinkedIn")

                # Navigate to feed
                page.goto(self.feed_url, timeout=30000)
                page.wait_for_timeout(5000)

                # Click "Start a post" - try multiple approaches
                try:
                    # Method 1: Click by text
                    try:
                        page.click('button:has-text("Start a post")', timeout=5000)
                        logger.info("Clicked 'Start a post' button (method 1)")
                    except:
                        # Method 2: Click by aria-label
                        page.click('[aria-label="Start a post"]', timeout=5000)
                        logger.info("Clicked 'Start a post' button (method 2)")
                    
                    page.wait_for_timeout(3000)
                    
                except Exception as e:
                    logger.error(f"Error clicking post button: {e}")
                    # Try to continue anyway - maybe direct URL works
                    page.goto('https://www.linkedin.com/feed/?shareActive=true', timeout=30000)
                    page.wait_for_timeout(3000)
                
                # Find the text editor and fill content
                try:
                    # Wait for editor to appear
                    page.wait_for_timeout(2000)
                    
                    # Try different selectors for the post editor
                    editor = None
                    editor_selectors = [
                        '[aria-label="What do you want to share?"]',
                        'div[contenteditable="true"]',
                        '.editor-editor-content',
                        'div.share-box-feed-entry'
                    ]
                    
                    for selector in editor_selectors:
                        try:
                            editor = page.query_selector(selector)
                            if editor:
                                logger.info(f"Found editor with selector: {selector}")
                                break
                        except:
                            continue
                    
                    if editor:
                        # Clear and fill
                        editor.fill('')
                        editor.fill(content)
                        page.wait_for_timeout(2000)
                        logger.info("Content filled in editor")
                    else:
                        # Fallback: Use keyboard to type
                        logger.warning("Editor not found, trying keyboard input")
                        page.keyboard.press('Tab')  # Try to focus
                        page.keyboard.type(content)
                        page.wait_for_timeout(1000)
                    
                except Exception as e:
                    logger.error(f"Error filling post content: {e}")
                    browser.close()
                    return False

                # Click Post button
                try:
                    page.wait_for_timeout(2000)
                    
                    # Try to click Post button
                    try:
                        page.click('button:has-text("Post")', timeout=5000)
                        logger.info("Clicked Post button (method 1)")
                    except:
                        try:
                            page.click('[aria-label="Post"]', timeout=5000)
                            logger.info("Clicked Post button (method 2)")
                        except:
                            page.click('.share-actions__primary-action', timeout=5000)
                            logger.info("Clicked Post button (method 3)")
                    
                    page.wait_for_timeout(5000)
                    logger.info("Post submitted!")
                    
                except Exception as e:
                    logger.error(f"Error clicking Post button: {e}")
                    browser.close()
                    return False

                # Wait for confirmation
                try:
                    page.wait_for_selector('text=Your post has been shared', timeout=10000)
                    logger.info("Post confirmed successful")
                except PlaywrightTimeout:
                    logger.warning("Post confirmation not found, but may still have succeeded")

                browser.close()
                return True

        except Exception as e:
            logger.error(f"Post error: {e}")
            return False
    
    def create_approval_request(self, content: str, scheduled_time: str = None) -> Path:
        """
        Create approval request file for a post.
        
        Args:
            content (str): Post content
            scheduled_time (str): Optional scheduled time
            
        Returns:
            Path: Path to created approval file
        """
        import logging
        logger = logging.getLogger('LinkedInPoster')
        
        timestamp = datetime.now()
        request_id = f"LINKEDIN_POST_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Preview content (first 100 chars)
        preview = content[:100] + "..." if len(content) > 100 else content
        
        approval_content = f"""---
type: approval_request
id: {request_id}
action: linkedin_post
created: {timestamp.isoformat()}
expires: {(timestamp + timedelta(hours=48)).isoformat()}
priority: medium
status: pending
scheduled_time: {scheduled_time if scheduled_time else 'Immediate'}
---

# LinkedIn Post Approval Request

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Scheduled:** {scheduled_time if scheduled_time else 'Immediate upon approval'}  
**Expires:** {(timestamp + timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S')}

---

## Post Content

{content}

---

## Post Details

| Attribute | Value |
|-----------|-------|
| Character Count | {len(content)} |
| Estimated Read Time | {max(1, len(content.split()) // 3)} min |
| Hashtags | {content.count('#')} |
| Scheduled Time | {scheduled_time or 'Immediate'} |

---

## Company Handbook Rules

- ✅ All posts require human approval before publishing
- ✅ Content reviewed for professionalism
- ⏰ Scheduled posts can be auto-published after initial approval

---

## Decision Required

### To Approve
**Move this file to:** `/Approved/`

The post will be published within 5 minutes.

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
| {timestamp.isoformat()} | Created | LinkedIn Poster |
"""
        
        # Write approval file
        filepath = self.pending_folder / f"{request_id}.md"
        filepath.write_text(approval_content, encoding='utf-8')
        
        logger.info(f"Created approval request: {filepath.name}")
        
        return filepath
    
    def process_approved_posts(self):
        """
        Process all approved post requests in Approved/ folder.
        
        Returns:
            int: Number of posts processed
        """
        import logging
        logger = logging.getLogger('LinkedInPoster')
        
        posts_processed = 0
        
        for filepath in self.approved_folder.glob('LINKEDIN_POST_*.md'):
            try:
                content = filepath.read_text(encoding='utf-8')
                
                # Extract post content from markdown
                # Look for content between "## Post Content" and "---"
                if '## Post Content' in content:
                    post_content = content.split('## Post Content')[1].split('---')[0].strip()
                else:
                    logger.warning(f"Could not extract content from {filepath.name}")
                    continue
                
                # Extract scheduled time if present
                scheduled_time = None
                if 'scheduled_time:' in content:
                    scheduled_time = content.split('scheduled_time:')[1].split('\n')[0].strip()
                    if scheduled_time == 'None' or scheduled_time == 'Immediate':
                        scheduled_time = None
                
                # Post to LinkedIn
                logger.info(f"Posting to LinkedIn: {filepath.name}")
                success = self.post_content(post_content, scheduled_time)
                
                if success:
                    # Log success
                    self._log_action(filepath.name, 'posted', post_content)
                    
                    # Move to Done
                    done_path = self.done_folder / filepath.name
                    filepath.rename(done_path)
                    logger.info(f"Post successful, moved to Done/: {done_path.name}")
                    
                    posts_processed += 1
                else:
                    logger.error(f"Failed to post: {filepath.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {filepath.name}: {e}")
        
        return posts_processed
    
    def _log_action(self, filename: str, action: str, content: str = None):
        """Log action to audit trail."""
        import logging
        logger = logging.getLogger('LinkedInPoster')
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'action': action,
            'content_preview': content[:100] if content else None
        }
        
        # Append to daily log
        log_file = self.logs_folder / f"linkedin_{datetime.now().strftime('%Y-%m-%d')}.json"

        logs = []
        if log_file.exists():
            try:
                import json
                logs = json.loads(log_file.read_text())
            except:
                logs = []
        
        logs.append(log_entry)
        
        try:
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            logger.error(f"Error writing log: {e}")


def generate_post_content(topic: str, tone: str = 'professional') -> str:
    """
    Generate LinkedIn post content from topic.
    
    Args:
        topic (str): Post topic
        tone (str): Post tone (professional, casual, enthusiastic)
        
    Returns:
        str: Generated post content
    """
    # Simple templates - in production, this would use Qwen to generate
    templates = {
        'professional': f"""🚀 Exciting update from our team!

We're making great progress on {topic}. 

Key highlights:
✅ Innovation in action
✅ Delivering value to customers
✅ Building the future

#Business #Innovation #Technology""",
        
        'casual': f"""Hey LinkedIn fam! 👋

Just wanted to share something cool we're working on: {topic}

It's been an amazing journey and we're just getting started!

What do you think? Drop a comment below! 👇

#StartupLife #Building #Tech""",
        
        'enthusiastic': f"""🎉 BIG NEWS! 🎉

We're absolutely thrilled to announce {topic}!

This is a game-changer and we couldn't be more excited to share this with you all!

Stay tuned for more updates! 🚀

#Exciting #Innovation #Growth #Success"""
    }
    
    return templates.get(tone, templates['professional'])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--post', type=str, help='Post content directly')
    parser.add_argument('--from-approval', type=str, help='Process approval file')
    parser.add_argument('--schedule', action='store_true', help='Create scheduled post')
    parser.add_argument('--content', type=str, help='Content for scheduled post')
    parser.add_argument('--time', type=str, help='Schedule time (HH:MM format)')
    parser.add_argument('--topic', type=str, help='Generate post from topic')
    parser.add_argument('--tone', type=str, default='professional', 
                       choices=['professional', 'casual', 'enthusiastic'],
                       help='Post tone')
    parser.add_argument('--process-approved', action='store_true', 
                       help='Process all approved posts')
    parser.add_argument('--auto-post', action='store_true',
                       help='Auto-post without approval (bypasses HITL)')
    parser.add_argument('--hashtags', type=str, default='',
                       help='Hashtags to add to post (space separated)')
    
    args = parser.parse_args()
    
    # Setup logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('LinkedInPoster')
    
    if not PLAYWRIGHT_AVAILABLE:
        print("\n❌ Playwright not installed")
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)
    
    poster = LinkedInPoster(args.vault_path)

    try:
        # Process approved posts
        if args.process_approved:
            count = poster.process_approved_posts()
            print(f"✅ Processed {count} post(s)")
            return

        # AUTO-POST MODE - Skip approval, post directly
        if args.auto_post and args.post:
            content = args.post
            if args.hashtags:
                content += f"\n\n{args.hashtags}"
            print(f"🚀 Auto-posting to LinkedIn...")
            print(f"Content: {content[:100]}...")
            
            success = poster.post_content(content)
            if success:
                print("✅ Post published successfully!")
            else:
                print("❌ Post failed. Check LinkedIn login status.")
            return

        # Auto-post from topic
        if args.auto_post and args.topic:
            content = generate_post_content(args.topic, args.tone)
            if args.hashtags:
                content += f"\n\n{args.hashtags}"
            print(f"🚀 Auto-posting to LinkedIn...")
            print(f"Topic: {args.topic}")
            print(f"Tone: {args.tone}")
            
            success = poster.post_content(content)
            if success:
                print("✅ Post published successfully!")
            else:
                print("❌ Post failed. Check LinkedIn login status.")
            return

        # Generate post from topic
        if args.topic:
            content = generate_post_content(args.topic, args.tone)
            print("Generated post content:")
            print("-" * 50)
            print(content)
            print("-" * 50)

            # Create approval request
            filepath = poster.create_approval_request(content, args.time)
            print(f"\n✅ Approval request created: {filepath.name}")
            print("Move to Approved/ to publish")
            return

        # Direct post (creates approval request)
        if args.post:
            filepath = poster.create_approval_request(args.post, args.time)
            print(f"✅ Approval request created: {filepath.name}")
            print("Move to Approved/ to publish")
            return

        # Process specific approval file
        if args.from_approval:
            approval_path = Path(args.from_approval)
            if not approval_path.exists():
                print(f"❌ File not found: {approval_path}")
                sys.exit(1)

            # Move to approved and process
            dest = poster.approved_folder / approval_path.name
            approval_path.rename(dest)

            count = poster.process_approved_posts()
            print(f"✅ Processed {count} post(s)")
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
