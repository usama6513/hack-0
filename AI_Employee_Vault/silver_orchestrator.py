#!/usr/bin/env python3
"""
Silver Tier Orchestrator Agent
Coordinates all Silver Tier watchers and implements the complete workflow:
Needs_Action → Plan → Pending_Approval → Approved → Sent

Human-in-the-loop: User only moves files from Pending_Approval to Approved
"""

import os
import sys
import time
import logging
import json
import shutil
import re
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Add skills directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills'))

from gmail_watcher import GmailWatcher
from whatsapp_watcher import WhatsAppWatcher
from linkedin_watcher import LinkedInWatcher
from plan_generator import PlanGenerator
from approval_workflow import ApprovalWorkflow
from email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('silver_orchestrator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SilverTierOrchestrator:
    """
    Silver Tier Orchestrator Agent
    Coordinates watchers and manages the complete workflow
    """

    def __init__(self, vault_path: str = "./"):
        self.vault_path = Path(vault_path)
        
        # Initialize components
        self.gmail_watcher = GmailWatcher(vault_path=str(vault_path))
        self.whatsapp_watcher = WhatsAppWatcher(vault_path=str(vault_path))
        self.linkedin_watcher = LinkedInWatcher(vault_path=str(vault_path))
        self.plan_generator = PlanGenerator(vault_path=str(vault_path))
        self.approval_workflow = ApprovalWorkflow(vault_path=str(vault_path))
        self.email_sender = EmailSender(vault_path=str(vault_path))
        
        # Directories
        self.inbox_dir = self.vault_path / "Inbox"
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.plans_dir = self.vault_path / "Plans"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_path / "Approved"
        self.sent_dir = self.vault_path / "Sent"
        
        # Ensure all directories exist
        for directory in [
            self.inbox_dir, self.needs_action_dir, self.plans_dir,
            self.pending_approval_dir, self.approved_dir, self.sent_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Workflow configuration
        self.workflow_config = self.load_workflow_config()
        
        # Keywords for important emails
        self.important_keywords = [
            'urgent', 'asap', 'important', 'deadline', 'invoice',
            'payment', 'meeting', 'proposal', 'client', 'project',
            'contract', 'agreement', 'review', 'approval', 'decision'
        ]
        
        logger.info("Silver Tier Orchestrator initialized")

    def load_workflow_config(self) -> Dict:
        """Load workflow configuration."""
        config_file = self.vault_path / "silver_tier_config.json"
        
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
            "max_emails_per_cycle": 5
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        return default_config

    def run_gmail_watcher(self) -> List[Dict]:
        """Run Gmail watcher to fetch new important emails."""
        logger.info("Running Gmail Watcher...")
        processed_emails = []
        
        try:
            if not self.gmail_watcher.authenticate():
                logger.error("Failed to authenticate with Gmail")
                return processed_emails
            
            messages = self.gmail_watcher.get_unread_emails(
                max_results=self.workflow_config.get('max_emails_per_cycle', 5)
            )
            
            if not messages:
                logger.info("No new unread emails found")
                return processed_emails
            
            logger.info(f"Found {len(messages)} unread emails")
            
            for message in messages:
                email_data = self.gmail_watcher.get_email_details(message['id'])
                
                if not email_data:
                    continue
                
                if self.is_email_important(email_data):
                    logger.info(f"Important email found: {email_data['headers'].get('subject', 'No Subject')}")
                    action_file = self.create_email_action_file(email_data)
                    processed_emails.append({
                        'type': 'email',
                        'action_file': action_file,
                        'email_data': email_data
                    })
                    self.gmail_watcher.mark_email_as_read(message['id'])
                else:
                    logger.info(f"Skipping non-important email")
                    self.gmail_watcher.mark_email_as_read(message['id'])
            
        except Exception as e:
            logger.error(f"Error in Gmail watcher: {e}")
        
        return processed_emails

    def is_email_important(self, email_data: Dict) -> bool:
        """Check if email contains important keywords."""
        subject = email_data['headers'].get('subject', '').lower()
        body = email_data.get('body', '').lower()
        snippet = email_data.get('snippet', '').lower()
        content = f"{subject} {body} {snippet}"
        
        for keyword in self.important_keywords:
            if keyword in content:
                logger.info(f"Found keyword '{keyword}' in email")
                return True
        
        return False

    def create_email_action_file(self, email_data: Dict) -> str:
        """Create an action file for the email in Needs_Action."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_id = email_data['id'][:8]
        subject = email_data['headers'].get('subject', 'No Subject')
        clean_subject = "".join(c if c.isalnum() or c in ' -_' else '' for c in subject)[:50]
        
        filename = f"GMAIL_{clean_subject}_{timestamp}_{message_id}.md"
        filepath = self.needs_action_dir / filename
        
        from_email = email_data['headers'].get('from', 'Unknown')
        body = email_data.get('body', '')
        
        content = f"""# Email Action Required

**Type:** email
**From:** {from_email}
**Subject:** {subject}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** High
**Message ID:** {email_data['id']}
**Status:** needs_action

## Email Content
{body[:1000]}{'...' if len(body) > 1000 else ''}

## Required Actions
- [ ] Generate AI reply
- [ ] Review and create plan
- [ ] Submit for approval
- [ ] Send after approval

## Workflow Status
Current: Needs_Action
Next: Plan Generation

---
*Created by Gmail Watcher*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created action file: {filename}")
        return str(filepath)

    def process_needs_action_files(self):
        """Process all files in Needs_Action directory."""
        logger.info("Processing Needs_Action files...")
        action_files = list(self.needs_action_dir.glob("GMAIL_*.md"))
        
        for action_file in action_files:
            try:
                with open(action_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip if already processed
                if "**Status:** plan_generated.com" in content or "**Status:** pending_approval" in content:
                    continue
                
                if "**Status:** needs_action" in content:
                    logger.info(f"Processing: {action_file.name}")
                    self.generate_ai_reply_and_plan(action_file)
                    
            except Exception as e:
                logger.error(f"Error processing {action_file.name}: {e}")

    def generate_ai_reply_and_plan(self, action_file: Path):
        """Generate AI reply and create plan for the email."""
        logger.info(f"Generating AI reply for {action_file.name}")
        
        try:
            with open(action_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract email information
            from_email = self.extract_field(content, 'From:')
            subject = self.extract_field(content, 'Subject:')
            email_content = self.extract_section(content, '## Email Content')
            
            # Generate AI reply
            reply_template = self.generate_email_reply(from_email, subject, email_content)
            
            # Create Plan file
            plan_file = self.create_plan_file(action_file.name, from_email, subject, reply_template)
            
            # Update action file status
            self.update_action_file_status(action_file, "plan_generated.com")
            
            logger.info(f"Created plan: {plan_file.name}")
            
            # Move to pending approval
            self.create_approval_request(plan_file, from_email, subject, reply_template)
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")

    def extract_field(self, content: str, field: str) -> str:
        """Extract a field from markdown content."""
        pattern = rf"\*\*{field}\*\*\s*(.+)"
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""

    def extract_section(self, content: str, section: str) -> str:
        """Extract section content from markdown."""
        pattern = rf"{section}\n(.*?)(?=\n##|\n---|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def generate_email_reply(self, from_email: str, subject: str, email_content: str) -> str:
        """Generate AI reply based on email content."""
        # Simple template-based reply generation
        # In production, this would call Claude Code API
        
        # Detect email type
        email_lower = email_content.lower()
        
        if 'invoice' in email_lower or 'payment' in email_lower:
            reply = f"""Dear {from_email.split()[0]},

Thank you for your email regarding the invoice/payment.

We have received your message and are processing it. Our team will review the details and get back to you within 24 hours.

If you have any urgent questions, please don't hesitate to contact us.

Best regards,
Accounts Team"""
        
        elif 'meeting' in email_lower or 'schedule' in email_lower:
            reply = f"""Dear {from_email.split()[0]},

Thank you for reaching out regarding the meeting.

I would be happy to schedule a time to discuss this further. Could you please provide me with your availability for next week?

Looking forward to our conversation.

Best regards,
[Your Name]"""
        
        elif 'proposal' in email_lower or 'project' in email_lower:
            reply = f"""Dear {from_email.split()[0]},

Thank you for your interest in our services.

We appreciate the opportunity to work with you. Our team is reviewing your requirements and we will send you a detailed proposal within the next 2 business days.

Please let me know if you have any immediate questions.

Best regards,
Business Development Team"""
        
        else:
            reply = f"""Dear {from_email.split()[0]},

Thank you for your email.

We have received your message and will review it shortly. Our team will get back to you with a detailed response within 24 hours.

If this is urgent, please let us know and we will prioritize your request.

Best regards,
[Your Name]"""
        
        return reply

    def create_plan_file(self, action_filename: str, from_email: str, subject: str, reply: str) -> Path:
        """Create a Plan file for the email."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_id = f"PLAN_{timestamp}"
        
        filename = f"{plan_id}.md"
        filepath = self.plans_dir / filename
        
        content = f"""# {plan_id}

## Task Overview
**Task:** Respond to Email
**From:** {from_email}
**Subject:** {subject}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** plan_generated
**Source File:** {action_filename}

## AI-Generated Reply
```
{reply}
```

## Execution Steps
### Step 1: Review ✅
- [x] AI has analyzed the email
- [x] Reply has been generated
- [ ] Human review required

### Step 2: Approval ⏳
- [ ] Submit for approval
- [ ] Human to approve reply
- [ ] Move to Approved folder

### Step 3: Send ⏳
- [ ] Send email via MCP/SMTP
- [ ] Log sent email
- [ ] Move to Sent folder

## Approval Required
**Type:** Email Reply
**Action:** Review and approve the generated reply
**Next:** File will be moved to Pending_Approval folder

---
*Plan generated by Silver Tier Orchestrator*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath

    def update_action_file_status(self, action_file: Path, status: str):
        """Update the status in action file."""
        with open(action_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace status
        content = content.replace("**Status:** needs_action", f"**Status:** {status}")
        
        with open(action_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Updated {action_file.name} status to {status}")

    def create_approval_request(self, plan_file: Path, from_email: str, subject: str, reply: str):
        """Create approval request in Pending_Approval folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_id = f"APPROVAL_{timestamp}"
        
        filename = f"{approval_id}_EMAIL_REPLY.md"
        filepath = self.pending_approval_dir / filename
        
        content = f"""# Email Reply Approval Required

**Approval ID:** {approval_id}
**Type:** Email Reply
**To:** {from_email}
**Subject:** {subject}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** pending_approval
**Plan File:** {plan_file.name}

## Generated Reply
```
{reply}
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

## What Happens Next?
✅ Once you move this file to **Approved** folder:
- Orchestrator will automatically send the email
- Email will be logged in Sent folder
- Task will be marked as complete

---
*Approval request created by Silver Tier Orchestrator*
*Your action: Move to Approved folder to send this email*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update plan file status
        self.update_plan_status(plan_file, "pending_approval")
        
        logger.info(f"Created approval request: {filename}")

    def update_plan_status(self, plan_file: Path, status: str):
        """Update status in plan file."""
        with open(plan_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("**Status:** plan_generated", f"**Status:** {status}")
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def process_approved_emails(self):
        """Process approved email replies and send them."""
        logger.info("Processing approved emails...")
        
        approved_files = list(self.approved_dir.glob("APPROVAL_*_EMAIL_REPLY.md"))
        
        for approved_file in approved_files:
            try:
                with open(approved_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract email details
                to_email = self.extract_field(content, '**To:**')
                subject = self.extract_field(content, '**Subject:**')
                reply = self.extract_reply(content)
                
                if to_email and subject and reply:
                    # Send the email
                    logger.info(f"Sending email to {to_email}")
                    success = self.send_email(to_email, subject, reply, approved_file)
                    
                    if success:
                        logger.info(f"Successfully sent email: {approved_file.name}")
                    else:
                        logger.error(f"Failed to send email: {approved_file.name}")
                else:
                    logger.error(f"Could not extract email details from {approved_file.name}")
                    
            except Exception as e:
                logger.error(f"Error processing approved file {approved_file.name}: {e}")

    def extract_reply(self, content: str) -> str:
        """Extract reply content from approval file."""
        pattern = r"## Generated Reply\n```\n(.*?)\n```"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def send_email(self, to: str, subject: str, body: str, approval_file: Path) -> bool:
        """Send email using EmailSender."""
        try:
            # Create draft first
            draft_path = self.email_sender.create_email_draft(to, subject, body)
            
            # Send via MCP/SMTP (simulated for now)
            result = self.email_sender.send_email_via_mcp(to, subject, body)
            
            if result.get('success'):
                # Move approval file to Sent
                sent_filename = f"SENT_{approval_file.name}"
                sent_path = self.sent_dir / sent_filename
                
                # Update content
                with open(approval_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = content.replace("**Status:** pending_approval", "**Status:** sent")
                content += f"\n\n## Sent Details\n- **Sent At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- **Message ID:** {result.get('message_id', 'N/A')}"
                
                with open(sent_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Remove original approval file
                approval_file.unlink()
                
                logger.info(f"Email sent and logged: {sent_filename}")
                return True
            else:
                logger.error(f"Email send failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def check_pending_approval_moves(self):
        """Check if user has moved any files to Approved folder."""
        # This is called periodically to check for user approvals
        self.process_approved_emails()

    def run_orchestration_cycle(self):
        """Run a complete orchestration cycle."""
        logger.info("=" * 50)
        logger.info("Starting Silver Tier Orchestration Cycle")
        logger.info("=" * 50)
        
        try:
            # Step 1: Run Gmail Watcher
            if self.workflow_config['enabled_watchers'].get('gmail', True):
                self.run_gmail_watcher()
            
            # Step 2: Process Needs_Action files
            self.process_needs_action_files()
            
            # Step 3: Check for approved emails and send
            self.check_pending_approval_moves()
            
            logger.info("Orchestration cycle completed")
            
        except Exception as e:
            logger.error(f"Error in orchestration cycle: {e}")

    def run(self, single_cycle: bool = False):
        """Run the orchestrator."""
        logger.info("Starting Silver Tier Orchestrator Agent...")
        
        if single_cycle:
            self.run_orchestration_cycle()
        else:
            interval = self.workflow_config.get('check_interval_seconds', 60)
            logger.info(f"Running continuously (check interval: {interval}s)")
            
            try:
                while True:
                    self.run_orchestration_cycle()
                    time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Orchestrator stopped by user")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Silver Tier Orchestrator Agent')
    parser.add_argument('--single', action='store_true', help='Run single cycle')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    orchestrator = SilverTierOrchestrator()
    
    if args.single:
        orchestrator.run_orchestration_cycle()
    else:
        orchestrator.run(single_cycle=False)


if __name__ == "__main__":
    main()
