"""
AI Employee Orchestrator
This is the main orchestrator that coordinates between watchers, vault operations, and AI processing.
For Bronze Tier, this provides basic coordination between components.
"""

import os
import time
import logging
from datetime import datetime
from skills.vault_manager import VaultManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Main orchestrator for the AI Employee system.
    Coordinates between watchers, vault operations, and AI processing.
    """

    def __init__(self):
        self.vault = VaultManager()
        self.running = False
        self.processing_interval = 30  # Check every 30 seconds
        logger.info("AI Employee Orchestrator initialized")

    def scan_inbox(self):
        """
        Scan the inbox for new files that need processing.
        """
        logger.info("Scanning inbox for new files...")
        inbox_contents = self.vault.read_inbox()

        if inbox_contents:
            logger.info(f"Found {len(inbox_contents)} files in inbox")
            for filename, content in inbox_contents.items():
                logger.info(f"Processing file: {filename}")
                self.process_file(filename, content)
        else:
            logger.info("No new files in inbox")

    def process_file(self, filename, content):
        """
        Process a single file from the inbox.
        For Bronze Tier, this provides basic processing logic.
        """
        try:
            # Log the processing
            logger.info(f"Processing file: {filename}")
            logger.info(f"Content preview: {content[:100]}...")

            # For Bronze Tier, we'll just move files to needs_action
            # In higher tiers, this would involve AI reasoning
            success, message = self.vault.move_to_needs_action(filename, "inbox")

            if success:
                logger.info(f"Successfully moved {filename} to needs_action")

                # Create a processing log entry
                self.log_processing(filename, "moved_to_needs_action")
            else:
                logger.error(f"Failed to move {filename}: {message}")

        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")

    def log_processing(self, filename, action):
        """
        Log processing actions for audit trail.
        """
        log_entry = f"""# Processing Log Entry

**File:** {filename}
**Action:** {action}
**Timestamp:** {datetime.now().isoformat()}
**Orchestrator:** Running in Bronze Tier mode

---
"""
        log_file = f"processing_log_{datetime.now().strftime('%Y%m%d')}.md"

        # Append to daily log file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def update_dashboard(self):
        """
        Update the dashboard with current status.
        """
        try:
            all_files = self.vault.list_all_files()

            dashboard_content = f"""# AI Employee Dashboard

## Overview
This dashboard tracks the activities of your AI Employee.

## Current Status
- **Active Tasks**: {len(all_files['needs_action'])}
- **Inbox Items**: {len(all_files['inbox'])}
- **Completed Today**: {len(all_files['done'])}

## System Health
- **Watchers Running**: File system watcher ready
- **Last Activity**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Vault Status**: Operational

## Quick Actions
- [ ] Check Inbox ({len(all_files['inbox'])} items)
- [ ] Review Needs Action ({len(all_files['needs_action'])} items)
- [ ] Update Status

## Recent Activity
- Orchestrator running in Bronze Tier mode
- Last scan: {datetime.now().strftime('%H:%M:%S')}
"""

            with open('Dashboard.md', 'w', encoding='utf-8') as f:
                f.write(dashboard_content)

            logger.info("Dashboard updated successfully")

        except Exception as e:
            logger.error(f"Error updating dashboard: {str(e)}")

    def run(self):
        """
        Main run loop for the orchestrator.
        """
        logger.info("Starting AI Employee Orchestrator...")
        self.running = True

        try:
            while self.running:
                logger.info("Orchestrator cycle starting...")

                # Update dashboard
                self.update_dashboard()

                # Scan inbox for new files
                self.scan_inbox()

                # Log cycle completion
                logger.info(f"Orchestrator cycle completed. Sleeping for {self.processing_interval} seconds...")

                # Wait before next cycle
                time.sleep(self.processing_interval)

        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Error in orchestrator main loop: {str(e)}")
            self.stop()

    def stop(self):
        """
        Stop the orchestrator gracefully.
        """
        logger.info("Stopping AI Employee Orchestrator...")
        self.running = False

    def process_single_cycle(self):
        """
        Process a single orchestration cycle (useful for testing).
        """
        logger.info("Running single orchestration cycle...")
        self.update_dashboard()
        self.scan_inbox()
        logger.info("Single cycle completed")

def main():
    """
    Main function to run the orchestrator.
    """
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--single', action='store_true', help='Run a single cycle instead of continuous loop')
    parser.add_argument('--interval', type=int, default=30, help='Processing interval in seconds (default: 30)')

    args = parser.parse_args()

    orchestrator = AIOrchestrator()
    orchestrator.processing_interval = args.interval

    if args.single:
        orchestrator.process_single_cycle()
    else:
        orchestrator.run()

if __name__ == "__main__":
    main()