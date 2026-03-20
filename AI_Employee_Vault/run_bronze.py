#!/usr/bin/env python3
"""
Bronze Tier Runner Script - Updated with filesystem_watcher option
This script runs all components of the Bronze Tier AI Employee system.
"""

import subprocess
import sys
import os
import time

def run_component(command, name):
    """Run a component and return the process."""
    print(f"Starting {name}...")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    return process

def main():
    """Main function to run all Bronze Tier components."""
    print("AI Employee Bronze Tier System")
    print("=" * 40)
    print()

    # Check Python dependencies
    try:
        import watchdog
    except ImportError:
        print("ERROR: watchdog library not installed!")
        print("Please run: pip install watchdog")
        sys.exit(1)

    # Create watched folder if it doesn't exist
    if not os.path.exists("Watched_Folder"):
        os.makedirs("Watched_Folder")
        print("Created Watched_Folder directory")

    # Run single cycle of orchestrator to test
    print("\nRunning initial system check...")
    subprocess.run([sys.executable, "orchestrator.py", "--single"])

    # Ask user what to run
    print("\nWhat would you like to run?")
    print("1. File watcher only (file_watcher.py)")
    print("2. Standard filesystem watcher (filesystem_watcher.py)")
    print("3. Orchestrator only")
    print("4. Both file_watcher + orchestrator (full system)")
    print("5. Both filesystem_watcher + orchestrator (full system)")
    print("6. Exit")

    choice = input("\nEnter your choice (1-6): ").strip()

    if choice == "1":
        print("\nStarting file_watcher...")
        print("Drop files into 'Watched_Folder' to test the system")
        print("Press Ctrl+C to stop")
        try:
            subprocess.run([sys.executable, "file_watcher.py"])
        except KeyboardInterrupt:
            print("\nFile watcher stopped")

    elif choice == "2":
        print("\nStarting filesystem_watcher (standard implementation)...")
        print("Drop files into 'Watched_Folder' to test the system")
        print("Press Ctrl+C to stop")
        try:
            subprocess.run([sys.executable, "filesystem_watcher.py"])
        except KeyboardInterrupt:
            print("\nFilesystem watcher stopped")

    elif choice == "3":
        print("\nStarting orchestrator...")
        print("The orchestrator will process files every 30 seconds")
        print("Press Ctrl+C to stop")
        try:
            subprocess.run([sys.executable, "orchestrator.py"])
        except KeyboardInterrupt:
            print("\nOrchestrator stopped")

    elif choice == "4":
        print("\nStarting full system with file_watcher...")

        # Start file watcher in background
        watcher_process = run_component(f"{sys.executable} file_watcher.py", "File Watcher")
        time.sleep(2)  # Give watcher time to start

        # Start orchestrator in background
        orchestrator_process = run_component(f"{sys.executable} orchestrator.py", "Orchestrator")

        print("\nSystem is running!")
        print("- Drop files into 'Watched_Folder' to test")
        print("- Check Dashboard.md for status updates")
        print("- Press Ctrl+C to stop all components")

        try:
            # Wait for interrupt
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping all components...")
            watcher_process.terminate()
            orchestrator_process.terminate()

            # Wait for graceful shutdown
            watcher_process.wait(timeout=5)
            orchestrator_process.wait(timeout=5)

            print("All components stopped")

    elif choice == "5":
        print("\nStarting full system with filesystem_watcher...")

        # Start filesystem watcher in background
        watcher_process = run_component(f"{sys.executable} filesystem_watcher.py", "Filesystem Watcher")
        time.sleep(2)  # Give watcher time to start

        # Start orchestrator in background
        orchestrator_process = run_component(f"{sys.executable} orchestrator.py", "Orchestrator")

        print("\nSystem is running with standard filesystem watcher!")
        print("- Drop files into 'Watched_Folder' to test")
        print("- Check Dashboard.md for status updates")
        print("- Press Ctrl+C to stop all components")

        try:
            # Wait for interrupt
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping all components...")
            watcher_process.terminate()
            orchestrator_process.terminate()

            # Wait for graceful shutdown
            watcher_process.wait(timeout=5)
            orchestrator_process.wait(timeout=5)

            print("All components stopped")

    elif choice == "6":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice!")
        sys.exit(1)

if __name__ == "__main__":
    main()