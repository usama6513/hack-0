#!/usr/bin/env python3
"""
Verify that the Bronze Tier implementation includes a proper Obsidian vault.
"""

import os
import json

def verify_obsidian_vault():
    """Verify that we have a proper Obsidian vault structure."""
    print("Verifying Obsidian Vault Structure...")
    print("=" * 50)

    vault_path = "AI_Employee_Vault"

    # Check if vault directory exists
    if not os.path.isdir(vault_path):
        print(f"[FAIL] Vault directory '{vault_path}' not found!")
        return False

    print(f"[OK] Vault directory '{vault_path}' exists")

    # Check for .obsidian directory
    obsidian_path = os.path.join(vault_path, ".obsidian")
    if not os.path.isdir(obsidian_path):
        print(f"[FAIL] Obsidian configuration directory not found!")
        return False

    print("[OK] .obsidian configuration directory exists")

    # Check for required Obsidian configuration files
    required_files = [
        "app.json",
        "appearance.json",
        "core-plugins.json",
        "workspace.json"
    ]

    for file in required_files:
        file_path = os.path.join(obsidian_path, file)
        if os.path.isfile(file_path):
            print(f"[OK] {file} configuration file exists")
        else:
            print(f"[WARN] {file} configuration file missing (optional)")

    # Check for required Bronze Tier files in vault
    bronze_files = [
        "Dashboard.md",
        "Company_Handbook.md",
        "README.md"
    ]

    print("\nChecking Bronze Tier files in vault:")
    for file in bronze_files:
        file_path = os.path.join(vault_path, file)
        if os.path.isfile(file_path):
            print(f"[OK] {file} exists in vault")
        else:
            print(f"[FAIL] {file} missing from vault!")
            return False

    # Check for workflow directories
    workflow_dirs = ["Inbox", "Needs_Action", "Done"]

    print("\nChecking workflow directories in vault:")
    for dir_name in workflow_dirs:
        dir_path = os.path.join(vault_path, dir_name)
        if os.path.isdir(dir_path):
            print(f"[OK] {dir_name}/ directory exists")
        else:
            print(f"[FAIL] {dir_name}/ directory missing!")
            return False

    # Check for Python scripts
    python_files = [
        "file_watcher.py",
        "orchestrator.py",
        "run_bronze.py",
        "verify_vault.py"
    ]

    print("\nChecking Python scripts in vault:")
    for file in python_files:
        file_path = os.path.join(vault_path, file)
        if os.path.isfile(file_path):
            print(f"[OK] {file} exists")
        else:
            print(f"[WARN] {file} missing (might be optional)")

    # Check for skills directory
    skills_path = os.path.join(vault_path, "skills")
    if os.path.isdir(skills_path) and os.path.isfile(os.path.join(skills_path, "vault_manager.py")):
        print("[OK] skills/ directory with vault_manager.py exists")
    else:
        print("[FAIL] skills/ directory or vault_manager.py missing!")
        return False

    print("\n" + "=" * 50)
    print("[SUCCESS] Obsidian Vault with Bronze Tier implementation is COMPLETE!")
    print("\nTo open this vault:")
    print("1. Open Obsidian")
    print("2. Click 'Open folder as vault'")
    print("3. Select the 'AI_Employee_Vault' folder")
    print("\nTo run the system:")
    print("cd AI_Employee_Vault")
    print("python run_bronze.py")

    return True

if __name__ == "__main__":
    success = verify_obsidian_vault()
    exit(0 if success else 1)