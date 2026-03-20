"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
All watchers follow the same pattern:
1. Check for updates from their data source
2. Create action files in the Needs_Action folder
3. Run continuously with configurable check interval

Usage:
    class MyWatcher(BaseWatcher):
        def check_for_updates(self) -> list:
            # Return list of new items to process
            pass
        
        def create_action_file(self, item) -> Path:
            # Create .md file in Needs_Action folder
            pass
        
        def run(self):
            # Inherit from base class
            super().run()
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    
    Attributes:
        vault_path (Path): Path to the Obsidian vault
        needs_action (Path): Path to the Needs_Action folder
        check_interval (int): Seconds between checks
        logger (logging.Logger): Logger instance
        processed_ids (set): Set of already processed item IDs
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the base watcher.
        
        Args:
            vault_path (str): Path to the Obsidian vault
            check_interval (int): Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_ids = set()
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Load previously processed IDs (to avoid duplicates after restart)
        self._load_processed_ids()
    
    def _load_processed_ids(self):
        """Load processed IDs from cache file."""
        cache_file = self.vault_path / '.cache' / f'{self.__class__.__name__}_processed.txt'
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.processed_ids = set(line.strip() for line in f)
                self.logger.info(f"Loaded {len(self.processed_ids)} processed IDs from cache")
            except Exception as e:
                self.logger.warning(f"Could not load processed IDs: {e}")
    
    def _save_processed_ids(self):
        """Save processed IDs to cache file."""
        cache_file = self.vault_path / '.cache' / f'{self.__class__.__name__}_processed.txt'
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(cache_file, 'w') as f:
                for item_id in self.processed_ids:
                    f.write(f"{item_id}\n")
        except Exception as e:
            self.logger.warning(f"Could not save processed IDs: {e}")
    
    def _generate_unique_id(self, content: str) -> str:
        """Generate a unique ID for content using SHA256."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string for use as a filename."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Limit length
        return name[:100]
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.
        
        Returns:
            list: List of new items (each item should be a dict with relevant data)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: dict) -> Path:
        """
        Create an action file for an item.
        
        Args:
            item (dict): Item data from check_for_updates
            
        Returns:
            Path: Path to the created action file
        """
        pass
    
    def run(self):
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        
        try:
            while True:
                try:
                    # Check for new items
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f"Found {len(items)} new item(s) to process")
                        
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                self.logger.info(f"Created action file: {filepath.name}")
                            except Exception as e:
                                self.logger.error(f"Error creating action file: {e}")
                    
                    # Save processed IDs periodically
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


if __name__ == "__main__":
    # Example usage (won't work without implementing abstract methods)
    print("This is a base module. Subclass BaseWatcher to create a specific watcher.")
    print("\nExample:")
    print("""
class GmailWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Your Gmail checking logic here
        return []
    
    def create_action_file(self, item) -> Path:
        # Your action file creation logic here
        pass
    
    def run(self):
        super().run()
""")
