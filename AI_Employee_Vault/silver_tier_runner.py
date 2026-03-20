"""
Silver Tier Runner for AI Employee
Orchestrates all Silver Tier skills and provides unified interface.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'skills'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('silver_tier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SilverTierRunner:
    """
    Main runner for Silver Tier AI Employee skills.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.config_path = os.path.join(vault_path, "silver_tier_config.json")
        self.status_path = os.path.join(vault_path, "silver_tier_status.json")

        # Ensure directories exist
        os.makedirs(vault_path, exist_ok=True)

        # Load configuration
        self.config = self.load_config()

        # Skill instances
        self.skills = {}
        self.running = False

        # Initialize skills on startup
        self.initialize_skills()

    def load_config(self) -> Dict:
        """Load Silver Tier configuration."""
        default_config = {
            "version": "1.0.0",
            "tier": "silver",
            "enabled_skills": {
                "gmail_watcher": True,
                "whatsapp_watcher": True,
                "linkedin_watcher": True,
                "linkedin_poster": True,
                "email_sender": True,
                "approval_workflow": True,
                "scheduler": True,
                "plan_generator": True
            },
            "settings": {
                "check_interval": 60,
                "approval_timeout": 24,
                "max_concurrent_tasks": 5,
                "log_level": "INFO"
            },
            "integrations": {
                "mcp_enabled": True,
                "browser_automation": True,
                "api_integrations": True
            }
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config
            try:
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default config at {self.config_path}")
            except Exception as e:
                logger.error(f"Error creating config: {e}")
            return default_config

    def initialize_skills(self):
        """Initialize all Silver Tier skills."""
        logger.info("Initializing Silver Tier skills...")

        enabled_skills = self.config.get("enabled_skills", {})

        # Initialize Gmail Watcher
        if enabled_skills.get("gmail_watcher", False):
            try:
                from gmail_watcher import GmailWatcher
                self.skills["gmail_watcher"] = GmailWatcher(vault_path=self.vault_path)
                logger.info("[OK] Gmail Watcher initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize Gmail Watcher: {e}")

        # Initialize WhatsApp Watcher
        if enabled_skills.get("whatsapp_watcher", False):
            try:
                from whatsapp_watcher import WhatsAppWatcher
                self.skills["whatsapp_watcher"] = WhatsAppWatcher(vault_path=self.vault_path)
                logger.info("[OK] WhatsApp Watcher initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize WhatsApp Watcher: {e}")

        # Initialize LinkedIn Watcher
        if enabled_skills.get("linkedin_watcher", False):
            try:
                from linkedin_watcher import LinkedInWatcher
                self.skills["linkedin_watcher"] = LinkedInWatcher(vault_path=self.vault_path)
                logger.info("[OK] LinkedIn Watcher initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize LinkedIn Watcher: {e}")

        # Initialize LinkedIn Poster
        if enabled_skills.get("linkedin_poster", False):
            try:
                from linkedin_poster import LinkedInPoster
                self.skills["linkedin_poster"] = LinkedInPoster(vault_path=self.vault_path)
                logger.info("[OK] LinkedIn Poster initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize LinkedIn Poster: {e}")

        # Initialize Email Sender
        if enabled_skills.get("email_sender", False):
            try:
                from email_sender import EmailSender
                self.skills["email_sender"] = EmailSender(vault_path=self.vault_path)
                logger.info("[OK] Email Sender initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize Email Sender: {e}")

        # Initialize Approval Workflow
        if enabled_skills.get("approval_workflow", False):
            try:
                from approval_workflow import ApprovalWorkflow
                self.skills["approval_workflow"] = ApprovalWorkflow(vault_path=self.vault_path)
                logger.info("[OK] Approval Workflow initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize Approval Workflow: {e}")

        # Initialize Scheduler
        if enabled_skills.get("scheduler", False):
            try:
                from scheduler import Scheduler
                self.skills["scheduler"] = Scheduler(vault_path=self.vault_path)
                logger.info("[OK] Scheduler initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize Scheduler: {e}")

        # Initialize Plan Generator
        if enabled_skills.get("plan_generator", False):
            try:
                from plan_generator import PlanGenerator
                self.skills["plan_generator"] = PlanGenerator(vault_path=self.vault_path)
                logger.info("[OK] Plan Generator initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize Plan Generator: {e}")

    def run_skill(self, skill_name: str, method: str = "run", *args, **kwargs):
        """Run a specific skill method."""
        if skill_name not in self.skills:
            logger.error(f"Skill '{skill_name}' not initialized")
            return False

        try:
            skill = self.skills[skill_name]
            if hasattr(skill, method):
                logger.info(f"Running {skill_name}.{method}()")
                result = getattr(skill, method)(*args, **kwargs)
                logger.info(f"[OK] {skill_name}.{method}() completed successfully")
                return result
            else:
                logger.error(f"Skill '{skill_name}' does not have method '{method}'")
                return False
        except Exception as e:
            logger.error(f"Error running {skill_name}.{method}(): {e}")
            return False

    def run_single_check(self):
        """Run a single check of all watcher skills."""
        logger.info("Running single check of all enabled skills...")

        # Run watchers
        if "gmail_watcher" in self.skills:
            self.run_skill("gmail_watcher", "run_single_check")

        if "whatsapp_watcher" in self.skills:
            self.run_skill("whatsapp_watcher", "run_single_check")

        if "linkedin_watcher" in self.skills:
            self.run_skill("linkedin_watcher", "run_single_check")

        # Process pending actions
        if "approval_workflow" in self.skills:
            self.run_skill("approval_workflow", "check_timeout_approvals")

        logger.info("Single check completed")

    def start_continuous_mode(self):
        """Start continuous monitoring mode."""
        logger.info("Starting Silver Tier in continuous mode...")
        self.running = True

        # Start approval workflow watcher
        if "approval_workflow" in self.skills:
            approval_thread = threading.Thread(target=self.run_skill, args=("approval_workflow", "run"))
            approval_thread.daemon = True
            approval_thread.start()

        # Start scheduler
        if "scheduler" in self.skills:
            scheduler_thread = threading.Thread(target=self.run_skill, args=("scheduler", "run_scheduler"))
            scheduler_thread.daemon = True
            scheduler_thread.start()

        try:
            while self.running:
                # Run periodic checks
                self.run_single_check()

                # Wait for next check interval
                check_interval = self.config.get("settings", {}).get("check_interval", 60)
                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("Silver Tier runner stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Error in continuous mode: {e}")
            self.running = False

    def create_plan(self, task_description: str) -> str:
        """Create a plan for a task using the plan generator."""
        if "plan_generator" in self.skills:
            return self.run_skill("plan_generator", "create_plan", task_description)
        else:
            logger.error("Plan Generator not available")
            return None

    def generate_linkedin_post(self, topic: str = "business automation") -> str:
        """Generate a LinkedIn post."""
        if "linkedin_poster" in self.skills:
            poster = self.skills["linkedin_poster"]
            draft_path, content = poster.create_post_draft(topic=topic)
            return draft_path, content
        else:
            logger.error("LinkedIn Poster not available")
            return None, None

    def send_email(self, recipient: str, subject: str, body: str, require_approval: bool = True) -> bool:
        """Send an email."""
        if "email_sender" in self.skills:
            sender = self.skills["email_sender"]
            return sender.send_email(recipient, subject, body, require_approval=require_approval)
        else:
            logger.error("Email Sender not available")
            return False

    def get_status(self) -> Dict:
        """Get current status of all skills."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "tier": "silver",
            "running": self.running,
            "skills": {}
        }

        for skill_name, skill in self.skills.items():
            status["skills"][skill_name] = {
                "initialized": True,
                "running": getattr(skill, 'running', False) if hasattr(skill, 'running') else None
            }

        # Save status
        try:
            with open(self.status_path, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving status: {e}")

        return status

    def install_requirements(self):
        """Install required Python packages."""
        import subprocess

        requirements = [
            "selenium",
            "playwright",
            "google-auth",
            "google-auth-oauthlib",
            "google-auth-httplib2",
            "google-api-python-client",
            "schedule",
            "croniter",
            "watchdog",
            "requests"
        ]

        logger.info("Installing required packages...")
        for req in requirements:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", req])
                logger.info(f"✓ Installed {req}")
            except Exception as e:
                logger.error(f"✗ Failed to install {req}: {e}")

    def setup(self):
        """Run initial setup for Silver Tier."""
        logger.info("Running Silver Tier setup...")

        # Install requirements
        self.install_requirements()

        # Create directory structure
        directories = [
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

        for directory in directories:
            dir_path = os.path.join(self.vault_path, directory)
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"✓ Created directory: {directory}")

        # Initialize skills
        self.initialize_skills()

        logger.info("Silver Tier setup completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Employee - Silver Tier Runner")
    parser.add_argument("--vault", default="./", help="Vault directory path")
    parser.add_argument("--setup", action="store_true", help="Run initial setup")
    parser.add_argument("--single", action="store_true", help="Run single check")
    parser.add_argument("--continuous", action="store_true", help="Run in continuous mode")
    parser.add_argument("--skill", help="Run specific skill (e.g., gmail_watcher)")
    parser.add_argument("--method", default="run", help="Method to call on skill")
    parser.add_argument("--plan", help="Create plan for task description")
    parser.add_argument("--linkedin-post", help="Generate LinkedIn post on topic")
    parser.add_argument("--email", nargs=3, metavar=("RECIPIENT", "SUBJECT", "BODY"), help="Send email")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    # Create runner
    runner = SilverTierRunner(vault_path=args.vault)

    # Handle commands
    if args.setup:
        runner.setup()
    elif args.single:
        runner.run_single_check()
    elif args.continuous:
        runner.start_continuous_mode()
    elif args.skill:
        runner.run_skill(args.skill, args.method)
    elif args.plan:
        plan_path = runner.create_plan(args.plan)
        if plan_path:
            print(f"Plan created: {plan_path}")
    elif args.linkedin_post:
        draft_path, content = runner.generate_linkedin_post(args.linkedin_post)
        if draft_path:
            print(f"LinkedIn post draft created: {draft_path}")
    elif args.email:
        recipient, subject, body = args.email
        success = runner.send_email(recipient, subject, body)
        print(f"Email {'sent' if success else 'failed'}")
    elif args.status:
        status = runner.get_status()
        print(json.dumps(status, indent=2))
    else:
        print("AI Employee - Silver Tier")
        print("Use --help for command options")
        print("\nQuick start:")
        print("  python silver_tier_runner.py --setup        # Initial setup")
        print("  python silver_tier_runner.py --single       # Run single check")
        print("  python silver_tier_runner.py --continuous   # Run continuously")