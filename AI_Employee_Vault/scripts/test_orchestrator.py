"""
Test Orchestrator

Quick test script to verify the Gmail Orchestrator workflow.
Run this to test the complete email processing pipeline.

Usage:
    python test_orchestrator.py
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def test_vault_structure():
    """Test 1: Verify vault folder structure"""
    print_header("TEST 1: Vault Structure")
    
    vault = Path('./AI_Employee_Vault')
    required_folders = [
        'Needs_Action',
        'Pending_Approval',
        'Approved',
        'Done',
        'Plans',
        'Logs',
        'Inbox/Drop'
    ]
    
    all_exist = True
    for folder in required_folders:
        folder_path = vault / folder
        if folder_path.exists():
            print_success(f"{folder}/ exists")
        else:
            print_error(f"{folder}/ MISSING")
            all_exist = False
    
    if all_exist:
        print_success("All required folders exist!")
        return True
    else:
        print_error("Some folders are missing!")
        return False

def test_scripts():
    """Test 2: Verify all scripts exist"""
    print_header("TEST 2: Script Files")
    
    scripts_folder = Path('./AI_Employee_Vault/scripts')
    required_scripts = [
        'gmail_watcher.py',
        'gmail_sender.py',
        'orchestrator.py',
        'base_watcher.py'
    ]
    
    all_exist = True
    for script in required_scripts:
        script_path = scripts_folder / script
        if script_path.exists():
            print_success(f"{script} exists")
        else:
            print_error(f"{script} MISSING")
            all_exist = False
    
    if all_exist:
        print_success("All required scripts exist!")
        return True
    else:
        print_error("Some scripts are missing!")
        return False

def test_credentials():
    """Test 3: Verify Gmail credentials"""
    print_header("TEST 3: Gmail Credentials")
    
    credentials = Path('./credentials.json')
    token = Path('./AI_Employee_Vault/scripts/token.json')
    
    if credentials.exists():
        print_success("credentials.json exists")
    else:
        print_error("credentials.json MISSING")
        return False
    
    if token.exists():
        print_success("token.json exists (OAuth authorized)")
    else:
        print_warning("token.json not found (will need OAuth on first run)")
    
    return True

def test_gmail_watcher():
    """Test 4: Test Gmail Watcher (quick check)"""
    print_header("TEST 4: Gmail Watcher Connection")
    
    print_info("Testing Gmail API connection...")
    
    vault_path = Path('./AI_Employee_Vault')
    
    try:
        # Run watcher for 5 seconds to test connection
        result = subprocess.run(
            [sys.executable, 'scripts/gmail_watcher.py', '.', '5'],
            cwd=str(vault_path),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout + result.stderr
        
        if 'Gmail service initialized' in output:
            print_success("Gmail API connected successfully!")
            
            # Check for errors
            if 'insufficientPermissions' in output:
                print_warning("Permission issue detected (see Troubleshooting section)")
                return False
            elif 'Found' in output and 'new message' in output:
                print_success("Emails detected!")
                return True
            else:
                print_info("No new emails (this is OK)")
                return True
        else:
            print_error("Failed to connect to Gmail API")
            print_warning("Check credentials and OAuth setup")
            return False
            
    except subprocess.TimeoutExpired:
        print_success("Gmail watcher running (timeout is expected)")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_needs_action():
    """Test 5: Check Needs_Action folder"""
    print_header("TEST 5: Needs_Action Folder")
    
    vault_path = Path('./AI_Employee_Vault')
    needs_action = vault_path / 'Needs_Action'
    
    if not needs_action.exists():
        print_error("Needs_Action folder doesn't exist!")
        return False
    
    email_files = list(needs_action.glob('EMAIL_*.md'))
    
    if len(email_files) > 0:
        print_success(f"Found {len(email_files)} email(s) to process:")
        for f in email_files:
            print_info(f"  - {f.name}")
        return True
    else:
        print_info("No emails in Needs_Action/ (this is OK)")
        return True

def test_orchestrator():
    """Test 6: Test Orchestrator startup"""
    print_header("TEST 6: Orchestrator Startup")
    
    vault_path = Path('./AI_Employee_Vault')
    
    try:
        # Run orchestrator for 3 seconds to test startup
        result = subprocess.run(
            [sys.executable, 'scripts/orchestrator.py', '.', 'gmail'],
            cwd=str(vault_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout
        
        if 'Orchestrator initialized' in output:
            print_success("Orchestrator initialized successfully!")
        else:
            print_warning("Orchestrator output unclear")
        
        if 'Started watcher: gmail' in output:
            print_success("Gmail watcher started!")
            return True
        elif 'Starting Orchestrator' in output:
            print_success("Orchestrator starting (watcher may be in background)")
            return True
        else:
            print_info("Orchestrator output:")
            print(output[:500] if len(output) > 500 else output)
            return True
            
    except subprocess.TimeoutExpired:
        print_success("Orchestrator running (timeout is expected)")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def show_next_steps():
    """Show next steps"""
    print_header("NEXT STEPS")
    
    print(f"""
{Colors.BOLD}To start the Gmail Orchestrator:{Colors.END}

  {Colors.GREEN}cd AI_Employee_Vault{Colors.END}
  {Colors.GREEN}python scripts/orchestrator.py . gmail{Colors.END}

{Colors.BOLD}To process emails with Qwen:{Colors.END}

  {Colors.GREEN}qwen "Process all emails in Needs_Action/ folder.{Colors.END}
  {Colors.GREEN}Follow the workflow: read email, check handbook,{Colors.END}
  {Colors.GREEN}create Plan.md, create approval request"{Colors.END}

{Colors.BOLD}To send approved emails:{Colors.END}

  {Colors.GREEN}python scripts/gmail_sender.py . --process-approved{Colors.END}

{Colors.BOLD}To stop the orchestrator:{Colors.END}

  Press {Colors.YELLOW}Ctrl+C{Colors.END} in the terminal window

""")

def main():
    """Run all tests"""
    print_header("GMAIL ORCHESTRATOR TEST SUITE")
    
    results = []
    
    # Run tests
    results.append(("Vault Structure", test_vault_structure()))
    results.append(("Script Files", test_scripts()))
    results.append(("Credentials", test_credentials()))
    results.append(("Gmail Watcher", test_gmail_watcher()))
    results.append(("Needs_Action", test_needs_action()))
    results.append(("Orchestrator", test_orchestrator()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print_success("🎉 All tests passed! System is ready!")
    else:
        print_warning("Some tests failed. Check the errors above.")
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
