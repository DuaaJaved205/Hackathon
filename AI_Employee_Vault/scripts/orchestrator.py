"""
Orchestrator

Master process that manages watcher scripts and triggers Qwen Code processing.
Coordinates the flow between perception (watchers), reasoning (Qwen), and action (MCP).

Usage:
    python orchestrator.py <vault_path>

Features:
- Start/stop watcher processes
- Monitor Needs_Action folder
- Trigger Qwen Code processing
- Manage completion state
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Attributes:
        vault_path (Path): Path to the Obsidian vault
        watchers (dict): Dictionary of watcher processes
        logger (logging.Logger): Logger instance
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path (str): Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.watchers = {}
        self.logger = logging.getLogger('Orchestrator')
        
        # Ensure required folders exist
        (self.vault_path / 'Needs_Action').mkdir(parents=True, exist_ok=True)
        (self.vault_path / 'Inbox' / 'Drop').mkdir(parents=True, exist_ok=True)
        (self.vault_path / '.cache').mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Orchestrator initialized for vault: {self.vault_path}")
    
    def start_watcher(self, name: str, script: str):
        """
        Start a watcher process.
        
        Args:
            name (str): Watcher name
            script (str): Script filename
        """
        if name in self.watchers and self.watchers[name].poll() is None:
            self.logger.info(f"Watcher {name} already running")
            return
        
        script_path = self.vault_path / 'scripts' / script
        
        if not script_path.exists():
            self.logger.warning(f"Script not found: {script_path}")
            return
        
        try:
            proc = subprocess.Popen(
                [sys.executable, str(script_path), str(self.vault_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.watchers[name] = proc
            self.logger.info(f"Started watcher: {name}")
        except Exception as e:
            self.logger.error(f"Failed to start watcher {name}: {e}")
    
    def stop_watcher(self, name: str):
        """
        Stop a watcher process.
        
        Args:
            name (str): Watcher name
        """
        if name not in self.watchers:
            return
        
        proc = self.watchers[name]
        if proc.poll() is None:
            proc.terminate()
            self.logger.info(f"Stopped watcher: {name}")
        
        del self.watchers[name]
    
    def stop_all(self):
        """Stop all watcher processes."""
        for name in list(self.watchers.keys()):
            self.stop_watcher(name)
        self.logger.info("All watchers stopped")
    
    def check_needs_action(self) -> int:
        """
        Check the Needs_Action folder for pending items.
        
        Returns:
            int: Number of pending items
        """
        needs_action = self.vault_path / 'Needs_Action'
        if not needs_action.exists():
            return 0
        
        count = len(list(needs_action.glob('*.md')))
        return count
    
    def trigger_qwen_processing(self, prompt: str = None):
        """
        Trigger Qwen Code to process pending items.

        Args:
            prompt (str): Custom prompt for Qwen (optional)
        """
        pending = self.check_needs_action()

        if pending == 0:
            self.logger.info("No pending items to process")
            return

        self.logger.info(f"Found {pending} pending item(s) for Qwen processing")

        # Default prompt
        if prompt is None:
            prompt = """
Process all files in /Needs_Action folder:
1. Read each file and understand the request
2. Check Company_Handbook.md for applicable rules
3. Create action plans in /Plans/ if multi-step
4. Request approval in /Pending_Approval/ for sensitive actions
5. Move completed items to /Done/
6. Update Dashboard.md with progress

Follow the Ralph Wiggum pattern - keep working until all items are processed.
"""

        # Create a processing prompt file
        prompt_file = self.vault_path / '.cache' / f'prompt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        prompt_file.write_text(prompt)

        self.logger.info(f"Created prompt file: {prompt_file}")
        self.logger.info("To process, run: qwen --cwd <vault_path>")
        self.logger.info(f"Then use prompt from: {prompt_file}")
    
    def run(self, watchers: list = None):
        """
        Run the orchestrator.

        Args:
            watchers (list): List of watcher names to start
        """
        self.logger.info("Starting Orchestrator")

        # Start requested watchers
        if watchers:
            for watcher in watchers:
                if watcher == 'filesystem':
                    self.start_watcher('filesystem', 'filesystem_watcher.py')
                elif watcher == 'gmail':
                    self.start_watcher('gmail', 'gmail_watcher.py')
                elif watcher == 'linkedin':
                    self.start_watcher('linkedin', 'linkedin_watcher.py')
                elif watcher == 'all':
                    # Start all available watchers
                    self.start_watcher('filesystem', 'filesystem_watcher.py')
                    self.start_watcher('gmail', 'gmail_watcher.py')
                    self.start_watcher('linkedin', 'linkedin_watcher.py')

        try:
            while True:
                # Check for pending items periodically
                pending = self.check_needs_action()

                if pending > 0:
                    self.logger.info(f"Pending items: {pending}")
                    self.logger.info("Run 'qwen' in the vault directory to process")

                time.sleep(60)

        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
        finally:
            self.stop_all()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <vault_path> [watchers...]")
        print("\nExample:")
        print("  python orchestrator.py ./AI_Employee_Vault filesystem")
        print("\nAvailable watchers:")
        print("  filesystem  - File system watcher (Inbox/Drop)")
        print("  gmail       - Gmail watcher (requires credentials.json)")
        print("  linkedin    - LinkedIn watcher (requires Playwright)")
        print("  all         - Start all watchers")
        sys.exit(1)

    vault_path = sys.argv[1]
    watchers = sys.argv[2:] if len(sys.argv) > 2 else []

    orchestrator = Orchestrator(vault_path)

    try:
        orchestrator.run(watchers)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        orchestrator.stop_all()
        sys.exit(1)


if __name__ == "__main__":
    main()
