"""
Agent Skills for AI Employee
Implements the required functionality to read from and write to the vault as Agent Skills.
"""

import os
import json
from datetime import datetime
import glob
import time

class VaultManager:
    """
    A class to manage reading from and writing to the Obsidian vault.
    """

    def __init__(self, inbox_dir="Inbox", needs_action_dir="Needs_Action", done_dir="Done"):
        self.inbox_dir = inbox_dir
        self.needs_action_dir = needs_action_dir
        self.done_dir = done_dir

        # Ensure directories exist
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.needs_action_dir, exist_ok=True)
        os.makedirs(self.done_dir, exist_ok=True)

    def read_inbox(self):
        """
        Read all files in the Inbox directory.
        """
        files = glob.glob(os.path.join(self.inbox_dir, "*.md"))
        contents = {}

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                contents[os.path.basename(file_path)] = f.read()

        return contents

    def read_needs_action(self):
        """
        Read all files in the Needs_Action directory.
        """
        files = glob.glob(os.path.join(self.needs_action_dir, "*.md"))
        contents = {}

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                contents[os.path.basename(file_path)] = f.read()

        return contents

    def read_done(self):
        """
        Read all files in the Done directory.
        """
        files = glob.glob(os.path.join(self.done_dir, "*.md"))
        contents = {}

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                contents[os.path.basename(file_path)] = f.read()

        return contents

    def move_to_needs_action(self, filename, source="inbox"):
        """
        Move a file from Inbox to Needs_Action.
        """
        if source == "inbox":
            src_path = os.path.join(self.inbox_dir, filename)
        else:
            return False, f"Unknown source: {source}"

        # Check if source file exists
        if not os.path.exists(src_path):
            return False, f"File {filename} not found in {source}"

        # Check if destination file already exists and handle accordingly
        dest_path = os.path.join(self.needs_action_dir, filename)
        if os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            timestamp = str(int(time.time()))
            dest_path = os.path.join(self.needs_action_dir, f"{name}_{timestamp}{ext}")

        os.rename(src_path, dest_path)
        return True, f"Moved {filename} from {source} to Needs_Action"

    def move_to_done(self, filename, source="needs_action"):
        """
        Move a file from Needs_Action to Done.
        """
        if source == "needs_action":
            src_path = os.path.join(self.needs_action_dir, filename)
        else:
            return False, f"Unknown source: {source}"

        # Check if source file exists
        if not os.path.exists(src_path):
            return False, f"File {filename} not found in {source}"

        # Check if destination file already exists and handle accordingly
        dest_path = os.path.join(self.done_dir, filename)
        if os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            timestamp = str(int(time.time()))
            dest_path = os.path.join(self.done_dir, f"{name}_{timestamp}{ext}")

        os.rename(src_path, dest_path)
        return True, f"Moved {filename} from {source} to Done"

    def create_task(self, filename, content, destination="inbox"):
        """
        Create a new task file in the specified directory.
        """
        if destination == "inbox":
            dest_path = os.path.join(self.inbox_dir, filename)
        elif destination == "needs_action":
            dest_path = os.path.join(self.needs_action_dir, filename)
        elif destination == "done":
            dest_path = os.path.join(self.done_dir, filename)
        else:
            return False, f"Unknown destination: {destination}"

        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True, f"Created task {filename} in {destination}"

    def list_all_files(self):
        """
        List all files in all directories.
        """
        all_files = {
            "inbox": glob.glob(os.path.join(self.inbox_dir, "*")),
            "needs_action": glob.glob(os.path.join(self.needs_action_dir, "*")),
            "done": glob.glob(os.path.join(self.done_dir, "*"))
        }

        # Get just the filenames
        for key in all_files:
            all_files[key] = [os.path.basename(path) for path in all_files[key]]

        return all_files

def main():
    """
    Main function to demonstrate the Agent Skills functionality.
    """
    print("AI Employee Vault Manager")
    print("=" * 30)

    # Initialize the vault manager
    vault = VaultManager()

    # Demonstrate the functionality
    print("\\nCurrent vault status:")
    files = vault.list_all_files()
    for folder, file_list in files.items():
        print(f"  {folder}: {file_list}")

    print("\\nReading Inbox contents:")
    inbox_contents = vault.read_inbox()
    for filename, content in inbox_contents.items():
        print(f"  File: {filename}")
        print(f"  Content preview: {content[:100]}...")
        print()

    # Example of creating a new task
    task_content = f"""# New Task
Created at: {datetime.now()}

## Description
This is a sample task created by the AI Employee.

## Action Required
Process this task and move to appropriate folder.
"""

    success, message = vault.create_task("sample_task.md", task_content, "inbox")
    print(f"\\nCreating sample task: {message}")

    # Show updated status
    print("\\nUpdated vault status:")
    files = vault.list_all_files()
    for folder, file_list in files.items():
        print(f"  {folder}: {file_list}")

if __name__ == "__main__":
    main()