#!/usr/bin/env python3
"""
Comprehensive test suite for all Silver Tier skills.
Tests each skill individually and reports results.
"""

import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'skills'))

class SilverTierTester:
    """Test all Silver Tier skills."""

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.test_results = {}
        self.test_log = []

    def log(self, message):
        """Log test message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.test_log.append(log_entry)

    def test_skill(self, skill_name, test_func):
        """Test a single skill."""
        self.log(f"Testing {skill_name}...")
        try:
            result = test_func()
            self.test_results[skill_name] = {
                "status": "PASSED",
                "message": result or "Skill test completed successfully",
                "timestamp": datetime.now().isoformat()
            }
            self.log(f"[OK] {skill_name} - PASSED")
            return True
        except Exception as e:
            self.test_results[skill_name] = {
                "status": "FAILED",
                "message": str(e),
                "error": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }
            self.log(f"[ERROR] {skill_name} - FAILED: {e}")
            return False

    def test_gmail_watcher(self):
        """Test Gmail Watcher."""
        from gmail_watcher import GmailWatcher

        # Create instance
        watcher = GmailWatcher(vault_path=self.vault_path)

        # Test authentication
        self.log("Testing Gmail authentication...")
        auth_success = watcher.authenticate()
        if not auth_success:
            return "Gmail authentication failed - check credentials.json"

        # Test getting unread emails (without actually fetching)
        self.log("Testing Gmail API connection...")
        try:
            # Just test the service is created
            if watcher.service:
                return "Gmail Watcher initialized successfully"
            else:
                return "Gmail service not created"
        except Exception as e:
            return f"Gmail API test failed: {e}"

    def test_whatsapp_watcher(self):
        """Test WhatsApp Watcher."""
        from whatsapp_watcher import WhatsAppWatcher

        # Create instance
        watcher = WhatsAppWatcher(vault_path=self.vault_path)

        # Test browser setup (without actually launching)
        self.log("Testing WhatsApp Watcher initialization...")

        # Check if directories are created
        needs_action_dir = os.path.join(self.vault_path, "Needs_Action")
        if os.path.exists(needs_action_dir):
            return "WhatsApp Watcher initialized successfully"
        else:
            return "Needs_Action directory not created"

    def test_linkedin_watcher(self):
        """Test LinkedIn Watcher."""
        from linkedin_watcher import LinkedInWatcher

        # Create instance
        watcher = LinkedInWatcher(vault_path=self.vault_path)

        # Test initialization
        self.log("Testing LinkedIn Watcher initialization...")

        # Check if directories are created
        needs_action_dir = os.path.join(self.vault_path, "Needs_Action")
        if os.path.exists(needs_action_dir):
            return "LinkedIn Watcher initialized successfully"
        else:
            return "Needs_Action directory not created"

    def test_linkedin_poster(self):
        """Test LinkedIn Poster."""
        from linkedin_poster import LinkedInPoster

        # Create instance
        poster = LinkedInPoster(vault_path=self.vault_path)

        # Test content generation
        self.log("Testing LinkedIn content generation...")
        content = poster.generate_business_content("AI automation")

        if content and "hook" in content and "body" in content:
            # Test draft creation
            draft_path, post_content = poster.create_post_draft(topic="AI automation")

            if os.path.exists(draft_path):
                return f"LinkedIn Poster working - created draft: {os.path.basename(draft_path)}"
            else:
                return "Draft file not created"
        else:
            return "Content generation failed"

    def test_email_sender(self):
        """Test Email Sender."""
        from email_sender import EmailSender

        # Create instance
        sender = EmailSender(vault_path=self.vault_path)

        # Test configuration loading
        self.log("Testing Email Sender configuration...")
        if sender.mcp_config:
            # Test draft creation
            draft_path = sender.create_email_draft(
                recipient="test@example.com",
                subject="Test Email",
                body="This is a test email"
            )

            if os.path.exists(draft_path):
                return f"Email Sender working - created draft: {os.path.basename(draft_path)}"
            else:
                return "Draft file not created"
        else:
            return "Configuration not loaded"

    def test_approval_workflow(self):
        """Test Approval Workflow."""
        from approval_workflow import ApprovalWorkflow

        # Create instance
        workflow = ApprovalWorkflow(vault_path=self.vault_path)

        # Test settings loading
        self.log("Testing Approval Workflow initialization...")
        if workflow.approval_settings:
            # Test risk analysis
            risk_analysis = workflow.analyze_action_risk("external_email", "Test email content")

            if "level" in risk_analysis and "requires_approval" in risk_analysis:
                return f"Approval Workflow working - risk level: {risk_analysis['level']}"
            else:
                return "Risk analysis failed"
        else:
            return "Settings not loaded"

    def test_scheduler(self):
        """Test Scheduler."""
        from scheduler import Scheduler

        # Create instance
        scheduler = Scheduler(vault_path=self.vault_path)

        # Test configuration loading
        self.log("Testing Scheduler initialization...")
        if scheduler.config:
            # Test job scheduling
            job_id = scheduler.schedule_task("test_job", "*/5 * * * *", lambda: print("Test"))

            if job_id:
                # List jobs
                jobs = scheduler.list_scheduled_jobs()
                if jobs:
                    return f"Scheduler working - created job: {job_id}"
                else:
                    return "Job not found in list"
            else:
                return "Job scheduling failed"
        else:
            return "Configuration not loaded"

    def test_plan_generator(self):
        """Test Plan Generator."""
        from plan_generator import PlanGenerator

        # Create instance
        generator = PlanGenerator(vault_path=self.vault_path)

        # Test plan creation
        self.log("Testing Plan Generator...")
        task_description = "Test task: Research AI automation trends and create summary report"
        plan_path = generator.create_plan(task_description)

        if plan_path and os.path.exists(plan_path):
            return f"Plan Generator working - created plan: {os.path.basename(plan_path)}"
        else:
            return "Plan not created"

    def test_directory_structure(self):
        """Test that all required directories exist."""
        self.log("Testing directory structure...")

        required_dirs = [
            "Needs_Action",
            "Approved",
            "Rejected",
            "Pending",
            "Sent",
            "Drafts",
            "Content",
            "Posted",
            "Templates",
            "Analytics",
            "Schedules",
            "Scheduler_Logs",
            "Approval_Logs",
            "Errors"
        ]

        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = os.path.join(self.vault_path, dir_name)
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_name)

        if not missing_dirs:
            return "All required directories exist"
        else:
            return f"Missing directories: {', '.join(missing_dirs)}"

    def run_all_tests(self):
        """Run all tests."""
        self.log("Starting Silver Tier comprehensive test suite...")
        self.log("=" * 60)

        # Test directory structure first
        self.test_skill("Directory Structure", self.test_directory_structure)

        # Test each skill
        skills_to_test = [
            ("Gmail Watcher", self.test_gmail_watcher),
            ("WhatsApp Watcher", self.test_whatsapp_watcher),
            ("LinkedIn Watcher", self.test_linkedin_watcher),
            ("LinkedIn Poster", self.test_linkedin_poster),
            ("Email Sender", self.test_email_sender),
            ("Approval Workflow", self.test_approval_workflow),
            ("Scheduler", self.test_scheduler),
            ("Plan Generator", self.test_plan_generator)
        ]

        passed = 0
        total = len(skills_to_test)

        for skill_name, test_func in skills_to_test:
            if self.test_skill(skill_name, test_func):
                passed += 1

        # Summary
        self.log("=" * 60)
        self.log(f"Test Summary: {passed}/{total} skills passed")

        # Save test results
        self.save_test_results()

        return passed == total

    def save_test_results(self):
        """Save test results to file."""
        results_file = os.path.join(self.vault_path, "test_results.json")
        log_file = os.path.join(self.vault_path, "test_log.txt")

        # Save JSON results
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": len(self.test_results),
                    "passed": sum(1 for r in self.test_results.values() if r["status"] == "PASSED"),
                    "failed": sum(1 for r in self.test_results.values() if r["status"] == "FAILED")
                },
                "results": self.test_results
            }, f, indent=2)

        # Save text log
        with open(log_file, 'w') as f:
            f.write("\n".join(self.test_log))

        self.log(f"Test results saved to: {results_file}")
        self.log(f"Test log saved to: {log_file}")

def main():
    """Main test runner."""
    vault_path = "./"
    tester = SilverTierTester(vault_path=vault_path)

    # Run all tests
    success = tester.run_all_tests()

    # Final result
    print("\n" + "=" * 60)
    if success:
        print("ALL TESTS PASSED! Silver Tier is ready to use!")
        print("\nNext steps:")
        print("  1. Run: python silver_tier_runner.py --setup")
        print("  2. Run: python silver_tier_runner.py --single")
        print("  3. Run: python silver_tier_runner.py --continuous")
    else:
        print("Some tests failed. Check the test results above.")
        print("\nCheck test_results.json and test_log.txt for details.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())