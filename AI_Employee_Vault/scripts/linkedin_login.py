"""
LinkedIn First Login Helper

Opens a visible browser window for you to login to LinkedIn.
After successful login, the session is saved and future runs can be headless.

Usage:
    python linkedin_login.py ./AI_Employee_Vault
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright

def main():
    vault_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    
    session_path = vault_path / '.cache' / 'linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("LinkedIn Login Helper")
    print("=" * 60)
    print()
    print("A browser window will open in 3 seconds...")
    print()
    print("INSTRUCTIONS:")
    print("1. Login to LinkedIn in the browser window")
    print("2. Wait until you see your feed (homepage)")
    print("3. Close the browser window when done")
    print("4. Session will be saved automatically")
    print()
    print("Press Ctrl+C to cancel")
    print()
    
    time.sleep(3)
    
    try:
        with sync_playwright() as p:
            # Launch visible browser
            browser = p.chromium.launch_persistent_context(
                str(session_path),
                headless=False,  # Visible browser
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized'
                ]
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            print("\nOpening LinkedIn login...")
            page.goto('https://www.linkedin.com/login')
            
            # Wait for user to login and navigate to feed
            print("Waiting for login... (will wait up to 5 minutes)")
            
            try:
                # Wait for user to reach feed page
                page.wait_for_url('https://www.linkedin.com/feed/*', timeout=300000)
                print("\n✅ Login successful! Detected LinkedIn feed.")
                print("\nSaving session...")
                
                # Save session
                context = browser.contexts[0]
                storage_state = context.storage_state()
                
                # Save to file
                import json
                storage_file = session_path / 'storage.json'
                with open(storage_file, 'w') as f:
                    json.dump(storage_state, f, indent=2)
                
                print(f"✅ Session saved to: {storage_file}")
                print("\nYou can now close this window.")
                print("Future runs will use this saved session.")
                
                # Keep browser open for a few more seconds
                time.sleep(5)
                
            except Exception as e:
                print(f"\n⚠️  Login timeout or error: {e}")
                print("Please run again and complete login faster.")
            
            browser.close()
            
    except KeyboardInterrupt:
        print("\n\n❌ Login cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Run the LinkedIn watcher:")
    print(f"   python scripts/linkedin_watcher.py {vault_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
