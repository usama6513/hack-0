"""
File System Watcher for AI Employee
Monitors a specified directory for new files and moves them to the appropriate folder.
"""
import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileWatcher(FileSystemEventHandler):
    """
    A file system watcher that monitors for new files and processes them according to business logic.
    """

    def __init__(self, watch_dir, inbox_dir="Inbox", needs_action_dir="Needs_Action", done_dir="Done"):
        self.watch_dir = watch_dir
        self.inbox_dir = inbox_dir
        self.needs_action_dir = needs_action_dir
        self.done_dir = done_dir

        # Ensure target directories exist
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.needs_action_dir, exist_ok=True)
        os.makedirs(self.done_dir, exist_ok=True)

    def on_created(self, event):
        """
        Handle file creation events.
        """
        if event.is_directory:
            return

        file_path = event.src_path
        logger.info(f"New file detected: {file_path}")

        # Move the file to the Inbox directory for processing
        filename = os.path.basename(file_path)
        target_path = os.path.join(self.inbox_dir, filename)

        # If file already exists in inbox, add a timestamp to prevent overwriting
        if os.path.exists(target_path):
            name, ext = os.path.splitext(filename)
            timestamp = str(int(time.time()))
            target_path = os.path.join(self.inbox_dir, f"{name}_{timestamp}{ext}")

        shutil.move(file_path, target_path)
        logger.info(f"Moved file to Inbox: {target_path}")

    def on_modified(self, event):
        """
        Handle file modification events.
        """
        if event.is_directory:
            return

        file_path = event.src_path
        logger.info(f"File modified: {file_path}")

def main():
    """
    Main function to run the file watcher.
    """
    # Configuration
    WATCH_DIR = "./Watched_Folder"  # Directory to monitor
    INBOX_DIR = "./Inbox"
    NEEDS_ACTION_DIR = "./Needs_Action"
    DONE_DIR = "./Done"

    # Create the watched directory if it doesn't exist
    os.makedirs(WATCH_DIR, exist_ok=True)

    # Create the file watcher
    event_handler = FileWatcher(
        watch_dir=WATCH_DIR,
        inbox_dir=INBOX_DIR,
        needs_action_dir=NEEDS_ACTION_DIR,
        done_dir=DONE_DIR
    )

    # Create the observer
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)

    logger.info(f"Starting file watcher for directory: {WATCH_DIR}")
    logger.info("Press Ctrl+C to stop the watcher")

    # Start the observer
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("File watcher stopped by user")

    observer.join()
    logger.info("File watcher terminated")

if __name__ == "__main__":
    main()