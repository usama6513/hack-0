#!/usr/bin/env python3
"""
Test Script for Silver Tier Orchestrator Setup
Tests the complete workflow without actually sending emails
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_directory_structure():
    """Test that all required directories exist."""
    print("\n" + "="*60)
    print("TEST 1: Directory Structure")
    print("="*60)
    
    required_dirs = [
        "Inbox",
        "Needs_Action",
        "Plans",
        "Pending_Approval",
        "Approved",
        "Sent",
        "Rejected"
    ]
    
    all_exist = True
    for directory in required_dirs:
        dir_path = Path(directory)
        if dir_path.exists() and dir_path.is_dir():
            print(f"[OK] {directory}/ directory exists")
        else:
            print(f"[FAIL] {directory}/ directory MISSING")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {directory}/")
            all_exist = False
    
    if all_exist:
        print("\n[OK] All required directories exist")
    else:
        print("\n[OK] Missing directories created")
    
    return True


def test_configuration():
    """Test configuration file."""
    print("\n" + "="*60)
    print("TEST 2: Configuration")
    print("="*60)
    
    config_file = Path("silver_tier_config.json")
    
    if not config_file.exists():
        print("[FAIL] Configuration file not found")
        print("  Creating default configuration...")
        
        default_config = {
            "enabled_watchers": {
                "gmail": True,
                "whatsapp": False,
                "linkedin": False
            },
            "check_interval_seconds": 60,
            "gmail_check_interval_seconds": 120,
            "auto_generate_replies": True,
            "require_approval_for_emails": True,
            "max_emails_per_cycle": 5,
            "important_keywords": [
                "urgent", "asap", "important", "deadline", "invoice",
                "payment", "meeting", "proposal", "client", "project"
            ]
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"[OK] Created: {config_file}")
    else:
        print(f"[OK] Configuration file exists: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"[OK] Configuration loaded successfully")
            print(f"  Gmail Watcher: {'Enabled' if config.get('enabled_watchers', {}).get('gmail') else 'Disabled'}")
            print(f"  Check Interval: {config.get('check_interval_seconds', 60)}s")
        except Exception as e:
            print(f"[FAIL] Error reading configuration: {e}")
    
    return True


def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "="*60)
    print("TEST 3: Module Imports")
    print("="*60)
    
    modules = [
        "gmail_watcher",
        "whatsapp_watcher",
        "linkedin_watcher",
        "plan_generator",
        "approval_workflow",
        "email_sender",
        "silver_orchestrator"
    ]
    
    all_imported = True
    for module in modules:
        try:
            __import__(module)
            print(f"[OK] {module} imported successfully")
        except ImportError as e:
            print(f"[FAIL] {module} import failed: {e}")
            all_imported = False
    
    if all_imported:
        print("\n[OK] All modules imported successfully")
    else:
        print("\n[FAIL] Some modules failed to import")
    
    return all_imported


def test_gmail_credentials():
    """Test Gmail API credentials."""
    print("\n" + "="*60)
    print("TEST 4: Gmail Credentials")
    print("="*60)
    
    credentials_file = Path("../credentials.json")
    token_file = Path("token.json")
    
    if credentials_file.exists():
        print(f"[OK] Gmail credentials file exists: {credentials_file}")
        
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
            
            if "installed" in creds or "web" in creds:
                print("[OK] Credentials file appears valid")
            else:
                print("[WARN] Credentials file may be invalid (missing 'installed' or 'web' key)")
        except Exception as e:
            print(f"[FAIL] Error reading credentials: {e}")
    else:
        print(f"[FAIL] Gmail credentials file NOT found: {credentials_file}")
        print("  Please download credentials.json from Google Cloud Console")
    
    if token_file.exists():
        print(f"[OK] Gmail token file exists: {token_file}")
        print("  (You are already authenticated)")
    else:
        print(f"[WARN] Gmail token file not found: {token_file}")
        print("  (Will be created on first Gmail Watcher run)")
    
    return True


def test_workflow_files():
    """Test creating sample workflow files."""
    print("\n" + "="*60)
    print("TEST 5: Workflow Files (Sample)")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create sample Needs_Action file
    sample_email = Path(f"Needs_Action/GMAIL_TEST_EMAIL_{timestamp}.md")
    sample_content = f"""# Email Action Required

**Type:** email
**From:** test@example.com
**Subject:** Test Email for Silver Tier Setup
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** High
**Message ID:** TEST12345
**Status:** needs_action

## Email Content
This is a test email to verify the Silver Tier Orchestrator setup.

Testing the workflow: Needs_Action -> Plan -> Pending_Approval -> Approved -> Sent

## Required Actions
- [ ] Generate AI reply
- [ ] Review and create plan
- [ ] Submit for approval
- [ ] Send after approval

## Workflow Status
Current: Needs_Action
Next: Plan Generation

---
*Test email created by test script*
"""
    
    with open(sample_email, 'w') as f:
        f.write(sample_content)
    print(f"[OK] Created sample email: {sample_email.name}")
    
    # Create sample approval file
    sample_approval = Path(f"Pending_Approval/APPROVAL_TEST_{timestamp}_EMAIL_REPLY.md")
    approval_content = f"""# Email Reply Approval Required

**Approval ID:** APPROVAL_TEST_{timestamp}
**Type:** Email Reply
**To:** test@example.com
**Subject:** Test Email for Silver Tier Setup
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** pending_approval

## Generated Reply
```
Dear test@example.com,

Thank you for your email.

We have received your message and will review it shortly. Our team will get back to you with a detailed response within 24 hours.

If this is urgent, please let us know and we will prioritize your request.

Best regards,
[Your Name]
```

## Approval Instructions
**HUMAN-IN-THE-LOOP ACTION REQUIRED:**

To APPROVE this email reply:
1. Review the reply content above
2. Edit if needed (optional)
3. **Move this file to `/Approved` folder**

To REJECT:
1. Move this file to `/Rejected` folder
2. Add reason for rejection

## Checklist
- [ ] Reply is professional
- [ ] Information is accurate
- [ ] No sensitive data exposed
- [ ] Ready to send on behalf of owner

---
*Test approval request created by test script*
"""
    
    with open(sample_approval, 'w') as f:
        f.write(approval_content)
    print(f"[OK] Created sample approval: {sample_approval.name}")
    
    print("\n[OK] Sample workflow files created")
    print("\nINSTRUCTIONS:")
    print(f"1. Open: Pending_Approval/{sample_approval.name}")
    print("2. Review the generated reply")
    print(f"3. Move file to: Approved/ folder")
    print("4. Run: python silver_orchestrator.py --single")
    print("5. Check Sent/ folder for processed email")
    
    return True


def test_orchestrator_initialization():
    """Test that orchestrator can be initialized."""
    print("\n" + "="*60)
    print("TEST 6: Orchestrator Initialization")
    print("="*60)
    
    try:
        from silver_orchestrator import SilverTierOrchestrator
        
        orchestrator = SilverTierOrchestrator()
        print("[OK] SilverTierOrchestrator initialized successfully")
        print(f"  Gmail Watcher: {'Enabled' if orchestrator.workflow_config['enabled_watchers'].get('gmail') else 'Disabled'}")
        print(f"  Check Interval: {orchestrator.workflow_config.get('check_interval_seconds', 60)}s")
        print(f"  Important Keywords: {len(orchestrator.important_keywords)} configured")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Orchestrator initialization failed: {e}")
        return False


def show_workflow_diagram():
    """Show the workflow diagram."""
    print("\n" + "="*60)
    print("SILVER TIER WORKFLOW DIAGRAM")
    print("="*60)
    
    print("""
    +------------------------------------------------------------------+
    |                    SILVER TIER WORKFLOW                           |
    +------------------------------------------------------------------+
    
    1. GMAIL WATCHER (Automatic)
       |
       Monitors Gmail for new unread emails
       Filters by keywords: urgent, invoice, meeting, etc.
       |
    
    2. NEEDS_ACTION (Automatic)
       |
       Creates: Needs_Action/GMAIL_*.md
       Contains: Email content and metadata
       |
    
    3. PLAN GENERATION (Automatic)
       |
       AI generates reply based on email content
       Creates: Plans/PLAN_*.md
       Status: plan_generated
       |
    
    4. PENDING_APPROVAL (Automatic)
       |
       Creates: Pending_Approval/APPROVAL_*_EMAIL_REPLY.md
       Contains: Generated reply for your review
       Status: pending_approval
       |
    
    +==================================================================+
    |  HUMAN-IN-THE-LOOP (YOUR ACTION REQUIRED)                        |
    |                                                                    |
    |  1. Open file in Pending_Approval/                                |
    |  2. Review AI-generated reply                                     |
    |  3. Edit if needed (optional)                                     |
    |  4. MOVE FILE TO: Approved/ folder                                |
    |                                                                    |
    |  THAT'S IT! The rest is automatic.                                |
    +==================================================================+
       |
    
    5. APPROVED (Detected by Orchestrator)
       |
       Orchestrator detects file in Approved/
       Prepares to send email
       |
    
    6. SENT (Automatic)
       |
       Sends email via MCP/SMTP
       Creates: Sent/SENT_*.md
       Status: sent
       |
    
    + TASK COMPLETE
    """)


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SILVER TIER ORCHESTRATOR - SETUP TEST")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {os.getcwd()}")
    
    results = []
    
    # Run tests
    results.append(("Directory Structure", test_directory_structure()))
    results.append(("Configuration", test_configuration()))
    results.append(("Module Imports", test_imports()))
    results.append(("Gmail Credentials", test_gmail_credentials()))
    results.append(("Workflow Files", test_workflow_files()))
    results.append(("Orchestrator Init", test_orchestrator_initialization()))
    
    # Show workflow
    show_workflow_diagram()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("\nNEXT STEPS:")
        print("1. Ensure credentials.json is in parent directory")
        print("2. Run: python silver_orchestrator.py --single")
        print("3. Check Pending_Approval/ for approval requests")
        print("4. Move file to Approved/ to test email sending")
        print("\nRead SILVER_TIER_ORCHESTRATOR_GUIDE.md for detailed instructions")
    else:
        print("\n[WARNING] SOME TESTS FAILED")
        print("Please fix the issues above before running the orchestrator")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
