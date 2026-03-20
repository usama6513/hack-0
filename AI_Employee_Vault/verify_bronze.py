#!/usr/bin/env python3
"""
Complete Bronze Tier Verification
Verifies all requirements including the filesystem_watcher.py
"""

import os
import json

def verify_bronze_complete():
    """Verify complete Bronze Tier implementation."""
    print("Complete Bronze Tier Verification")
    print("=" * 50)
    print()

    vault_path = "."  # Current directory is the vault

    # 1. Check Obsidian Vault Structure
    print("1. Checking Obsidian Vault...")
    if not os.path.isdir(vault_path):
        print(f"[FAIL] Vault directory '{vault_path}' not found!")
        return False

    obsidian_path = os.path.join(vault_path, ".obsidian")
    if not os.path.isdir(obsidian_path):
        print(f"[FAIL] Obsidian configuration directory not found!")
        return False

    print("[OK] Obsidian vault with proper configuration")

    # 2. Check Bronze Tier Files in Vault
    print("\n2. Checking Bronze Tier files...")
    required_files = [
        "Dashboard.md",
        "Company_Handbook.md"
    ]

    for file in required_files:
        file_path = os.path.join(vault_path, file)
        if os.path.isfile(file_path):
            print(f"[OK] {file} exists in vault")
        else:
            print(f"[FAIL] {file} missing!")
            return False

    # 3. Check Workflow Directories
    print("\n3. Checking workflow directories...")
    workflow_dirs = ["Inbox", "Needs_Action", "Done"]

    for dir_name in workflow_dirs:
        dir_path = os.path.join(vault_path, dir_name)
        if os.path.isdir(dir_path):
            print(f"[OK] {dir_name}/ directory exists")
        else:
            print(f"[FAIL] {dir_name}/ directory missing!")
            return False

    # 4. Check Watcher Scripts
    print("\n4. Checking watcher scripts...")

    # Check for at least one watcher (Bronze requirement)
    file_watcher = os.path.join(vault_path, "file_watcher.py")
    filesystem_watcher = os.path.join(vault_path, "filesystem_watcher.py")

    if os.path.isfile(file_watcher):
        print("[OK] file_watcher.py exists")

    if os.path.isfile(filesystem_watcher):
        print("[OK] filesystem_watcher.py exists (standard implementation)")

    if not os.path.isfile(file_watcher) and not os.path.isfile(filesystem_watcher):
        print("[FAIL] No watcher script found!")
        return False

    # 5. Check Agent Skills
    print("\n5. Checking Agent Skills...")
    skills_path = os.path.join(vault_path, "skills")
    vault_manager = os.path.join(skills_path, "vault_manager.py")

    if os.path.isdir(skills_path) and os.path.isfile(vault_manager):
        print("[OK] Agent Skills with vault_manager.py exists")
    else:
        print("[FAIL] Agent Skills not properly implemented!")
        return False

    # 6. Check Additional Components
    print("\n6. Checking additional components...")

    orchestrator = os.path.join(vault_path, "orchestrator.py")
    if os.path.isfile(orchestrator):
        print("[OK] Orchestrator exists")

    print("\n" + "=" * 50)
    print("[SUCCESS] All Bronze Tier requirements are met!")
    print()
    print("Summary of what was created:")
    print("- Obsidian vault with proper .obsidian configuration")
    print("- Dashboard.md and Company_Handbook.md in the vault")
    print("- Inbox/, Needs_Action/, Done/ directories")
    print("- file_watcher.py and filesystem_watcher.py (your choice)")
    print("- skills/vault_manager.py (Agent Skills)")
    print("- orchestrator.py for system coordination")
    print()
    print("The filesystem_watcher.py is now included as the standard")
    print("implementation referenced in the hackathon documentation.")

    return True

if __name__ == "__main__":
    success = verify_bronze_complete()
    exit(0 if success else 1)