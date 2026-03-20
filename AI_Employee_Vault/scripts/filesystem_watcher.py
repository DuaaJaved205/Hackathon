"""
File System Watcher

Monitors a drop folder for new files and creates action files in the Needs_Action folder.
This is a simple watcher that works immediately without API setup.

Use cases:
- Drag and drop files for processing
- Monitor downloads folder
- Watch for exported data files

Usage:
    python filesystem_watcher.py /path/to/vault

Watched folder: <vault>/Inbox/Drop
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Watchdog not installed. Install with:")
    print("  pip install watchdog")


class DropFolderHandler(FileSystemEventHandler):
    """
    Handles file system events in the drop folder.
    
    Attributes:
        watcher: Parent FilesystemWatcher instance
    """
    
    def __init__(self, watcher):
        """
        Initialize the handler.
        
        Args:
            watcher: Parent FilesystemWatcher instance
        """
        super().__init__()
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
        
        source_path = Path(event.src_path)
        
        # Skip hidden files and temp files
        if source_path.name.startswith('.') or source_path.suffix.endswith('.tmp'):
            return
        
        self.logger.info(f"New file detected: {source_path.name}")
        
        # Wait a moment for file to finish writing
        import time
        time.sleep(0.5)
        
        # Create action file
        try:
            self.watcher.process_file(source_path)
        except Exception as e:
            self.logger.error(f"Error processing file: {e}")


class FilesystemWatcher(BaseWatcher):
    """
    Watches a folder for new files and creates action files.
    
    Attributes:
        drop_folder: Path to the folder being watched
        observer: Watchdog Observer instance
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize Filesystem Watcher.
        
        Args:
            vault_path (str): Path to Obsidian vault
            check_interval (int): Seconds between checks (not used with watchdog)
        """
        super().__init__(vault_path, check_interval)
        
        if not WATCHDOG_AVAILABLE:
            raise ImportError("Watchdog library not installed")
        
        # Set up drop folder
        self.drop_folder = self.vault_path / 'Inbox' / 'Drop'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Set up observer
        self.observer = None
        self.event_handler = DropFolderHandler(self)
        
        self.logger.info(f"Watching folder: {self.drop_folder}")
    
    def process_file(self, source_path: Path) -> Path:
        """
        Process a new file and create an action file.
        
        Args:
            source_path: Path to the new file
            
        Returns:
            Path: Path to created action file
        """
        # Generate unique ID
        file_id = self._generate_unique_id(str(source_path))
        
        # Skip if already processed
        if file_id in self.processed_ids:
            self.logger.info(f"File already processed: {source_path.name}")
            return None
        
        self.processed_ids.add(file_id)
        
        # Get file info
        stat = source_path.stat()
        file_size = stat.st_size
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create filename
        safe_name = self._sanitize_filename(source_path.name[:50])
        filename = f"FILE_{timestamp}_{safe_name}.md"
        
        # Determine file type hints
        file_type_hints = self._get_file_type_hints(source_path)
        
        # Create content
        content = f"""---
type: file_drop
original_name: {source_path.name}
file_id: {file_id}
size: {file_size}
size_human: {self._format_size(file_size)}
received: {datetime.now().isoformat()}
priority: medium
status: pending
{file_type_hints}
---

# File Drop: {source_path.name}

**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Size:** {self._format_size(file_size)}  
**Type:** {source_path.suffix.upper()}

---

## File Information

{file_type_hints}

## Suggested Actions

- [ ] Review file content
- [ ] Extract relevant information
- [ ] Create tasks from file
- [ ] Move to appropriate folder
- [ ] Archive after processing

## Notes

_Add your notes here_

---

*Created by File System Watcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Write action file
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created action file: {filepath.name}")
        
        return filepath
    
    def _get_file_type_hints(self, source_path: Path) -> str:
        """
        Get hints about file type based on extension.
        
        Args:
            source_path: Path to the file
            
        Returns:
            str: YAML-formatted hints
        """
        hints = []
        
        extension_map = {
            '.pdf': 'category: document',
            '.doc': 'category: document',
            '.docx': 'category: document',
            '.txt': 'category: text',
            '.md': 'category: markdown',
            '.csv': 'category: data\nformat: csv',
            '.xlsx': 'category: data\nformat: spreadsheet',
            '.xls': 'category: data\nformat: spreadsheet',
            '.json': 'category: data\nformat: json',
            '.xml': 'category: data\nformat: xml',
            '.jpg': 'category: image',
            '.jpeg': 'category: image',
            '.png': 'category: image',
            '.gif': 'category: image',
            '.zip': 'category: archive',
            '.rar': 'category: archive',
            '.7z': 'category: archive',
        }
        
        return extension_map.get(source_path.suffix.lower(), 'category: other')
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            str: Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def check_for_updates(self) -> list:
        """
        Not used with watchdog (event-driven).
        
        Returns:
            list: Empty list
        """
        return []
    
    def create_action_file(self, item) -> Path:
        """
        Not used with watchdog (event-driven).
        
        Args:
            item: Not used
            
        Returns:
            Path: None
        """
        return None
    
    def run(self):
        """
        Start the file system watcher.
        
        Uses watchdog Observer for event-driven file monitoring.
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Drop folder: {self.drop_folder}")
        
        try:
            # Set up observer
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.drop_folder),
                recursive=False
            )
            self.observer.start()
            self.logger.info("File watcher started. Waiting for files...")
            
            # Keep running
            while True:
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("File watcher stopped by user")
        except Exception as e:
            self.logger.error(f"Error in file watcher: {e}")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()
            self._save_processed_ids()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python filesystem_watcher.py <vault_path>")
        print("\nExample:")
        print("  python filesystem_watcher.py ./AI_Employee_Vault")
        print("\nDrop files into: <vault>/Inbox/Drop/")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    try:
        watcher = FilesystemWatcher(vault_path)
        watcher.run()
    except ImportError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nWatcher stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
