"""
Approval Workflow Skill for AI Employee - Silver Tier
Manages human-in-the-loop approval system for sensitive actions.
"""

import os
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('approval_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ApprovalWorkflow:
    """
    Manages the approval workflow for sensitive AI Employee actions.
    Watches for files in Needs_Action folder and handles approval process.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.needs_action_dir = os.path.join(vault_path, "Needs_Action")
        self.approved_dir = os.path.join(vault_path, "Approved")
        self.rejected_dir = os.path.join(vault_path, "Rejected")
        self.pending_dir = os.path.join(vault_path, "Pending")
        self.approval_log_dir = os.path.join(vault_path, "Approval_Logs")

        # Ensure directories exist
        for directory in [self.needs_action_dir, self.approved_dir, self.rejected_dir,
                         self.pending_dir, self.approval_log_dir]:
            os.makedirs(directory, exist_ok=True)

        # Approval settings
        self.approval_settings = self.load_approval_settings()
        self.pending_approvals = {}

    def load_approval_settings(self) -> Dict:
        """Load approval settings from configuration file."""
        config_path = os.path.join(self.vault_path, "approval_config.json")
        default_settings = {
            "auto_approve_low_risk": True,
            "approval_timeout_hours": 24,
            "notification_methods": ["file", "log"],
            "risk_categories": {
                "low": ["internal_communication", "draft_review"],
                "medium": ["external_email", "social_media_post", "data_export"],
                "high": ["financial_transaction", "delete_operation", "confidential_share"]
            },
            "approval_rules": {
                "linkedin_post": {
                    "requires_approval": True,
                    "min_approvers": 1,
                    "approver_roles": ["manager", "marketing"]
                },
                "external_email": {
                    "requires_approval": True,
                    "min_approvers": 1,
                    "approver_roles": ["manager"]
                },
                "invoice_send": {
                    "requires_approval": True,
                    "min_approvers": 2,
                    "approver_roles": ["manager", "finance"]
                }
            }
        }

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except Exception as e:
                logger.error(f"Error loading approval settings: {e}")
                return default_settings
        else:
            # Create default config
            try:
                with open(config_path, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                logger.info(f"Created default approval settings at {config_path}")
            except Exception as e:
                logger.error(f"Error creating approval settings: {e}")
            return default_settings

    def analyze_action_risk(self, action_type: str, content: str) -> Dict:
        """Analyze the risk level of an action."""
        risk_categories = self.approval_settings.get("risk_categories", {})

        # Determine risk level
        risk_level = "low"
        risk_reasons = []

        # Check action type
        for level, actions in risk_categories.items():
            if action_type in actions:
                risk_level = level
                risk_reasons.append(f"Action type '{action_type}' is categorized as {level} risk")

        # Content analysis
        high_risk_keywords = [
            "confidential", "private", "sensitive", "financial", "payment",
            "delete", "remove", "terminate", "cancel", "refund"
        ]
        medium_risk_keywords = [
            "external", "client", "customer", "public", "social media",
            "linkedin", "twitter", "facebook", "post", "share"
        ]

        content_lower = content.lower()
        found_high_risk = [kw for kw in high_risk_keywords if kw in content_lower]
        found_medium_risk = [kw for kw in medium_risk_keywords if kw in content_lower]

        if found_high_risk:
            risk_level = "high"
            risk_reasons.append(f"Contains high-risk keywords: {', '.join(found_high_risk)}")
        elif found_medium_risk:
            if risk_level == "low":
                risk_level = "medium"
            risk_reasons.append(f"Contains medium-risk keywords: {', '.join(found_medium_risk)}")

        return {
            "level": risk_level,
            "reasons": risk_reasons,
            "requires_approval": self.requires_approval(action_type, risk_level)
        }

    def requires_approval(self, action_type: str, risk_level: str) -> bool:
        """Determine if an action requires approval."""
        approval_rules = self.approval_settings.get("approval_rules", {})

        # Check specific rules for action type
        if action_type in approval_rules:
            return approval_rules[action_type].get("requires_approval", True)

        # Default based on risk level
        if risk_level == "high":
            return True
        elif risk_level == "medium":
            return True
        else:
            # Low risk - check auto-approve setting
            return not self.approval_settings.get("auto_approve_low_risk", False)

    def process_new_action(self, file_path: str) -> bool:
        """Process a new action file and determine approval requirements."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract action details
            lines = content.split('\n')
            action_type = ""
            priority = ""

            for line in lines:
                if line.startswith('**Type:**'):
                    action_type = line.replace('**Type:**', '').strip()
                elif line.startswith('**Priority:**'):
                    priority = line.replace('**Priority:**', '').strip()

            # Analyze risk
            risk_analysis = self.analyze_action_risk(action_type, content)

            if risk_analysis["requires_approval"]:
                # Move to pending and create approval request
                self.create_approval_request(file_path, action_type, risk_analysis)
                return True
            else:
                # Auto-approve
                logger.info(f"Auto-approved: {os.path.basename(file_path)}")
                self.auto_approve(file_path, action_type)
                return True

        except Exception as e:
            logger.error(f"Error processing action file: {e}")
            return False

    def create_approval_request(self, file_path: str, action_type: str, risk_analysis: Dict):
        """Create a detailed approval request."""
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Move file to pending
        pending_path = os.path.join(self.pending_dir, f"PENDING_{timestamp}_{filename}")
        shutil.move(file_path, pending_path)

        # Create approval record
        approval_record = {
            "original_file": filename,
            "pending_file": os.path.basename(pending_path),
            "action_type": action_type,
            "risk_level": risk_analysis["level"],
            "risk_reasons": risk_analysis["reasons"],
            "requested_at": datetime.now().isoformat(),
            "status": "pending",
            "approvals": [],
            "rejections": [],
            "timeout_at": (datetime.now() + timedelta(hours=self.approval_settings.get("approval_timeout_hours", 24))).isoformat()
        }

        # Save approval record
        record_path = os.path.join(self.approval_log_dir, f"APPROVAL_RECORD_{timestamp}.json")
        with open(record_path, 'w', encoding='utf-8') as f:
            json.dump(approval_record, f, indent=2)

        # Create human-readable approval request
        self.create_human_readable_request(pending_path, approval_record)

        logger.info(f"Created approval request for {action_type}: {os.path.basename(pending_path)}")

    def create_human_readable_request(self, pending_path: str, approval_record: Dict):
        """Create a human-readable approval request file."""
        request_content = f"""# APPROVAL REQUIRED - Action Request

**Action Type:** {approval_record['action_type']}
**Risk Level:** {approval_record['risk_level'].upper()}
**Requested:** {approval_record['requested_at']}
**Timeout:** {approval_record['timeout_at']}

## Risk Analysis
{"\n".join(f"- {reason}" for reason in approval_record['risk_reasons'])}

## Approval Instructions
To APPROVE this action:
1. Review the original request above
2. If approved, move this file to the `/Approved` folder
3. The AI Employee will execute the action automatically

To REJECT this action:
1. Move this file to the `/Rejected` folder
2. Optionally add a rejection reason in the file

## Approval Rules
{"\n".join(f"- {rule}: {details}" for rule, details in self.approval_settings.get('approval_rules', {}).get(approval_record['action_type'], {}).items())}

---
*This action requires human approval before execution*

## Original Request:
"""

        # Add original content
        with open(pending_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        request_content += original_content

        # Write approval request
        approval_path = pending_path.replace("PENDING_", "APPROVAL_REQUEST_")
        with open(approval_path, 'w', encoding='utf-8') as f:
            f.write(request_content)

        # Remove original pending file
        os.remove(pending_path)

    def auto_approve(self, file_path: str, action_type: str):
        """Auto-approve a low-risk action."""
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Move to approved
        approved_path = os.path.join(self.approved_dir, f"AUTO_APPROVED_{timestamp}_{filename}")
        shutil.move(file_path, approved_path)

        # Log approval
        log_entry = {
            "action_type": action_type,
            "filename": filename,
            "approved_at": datetime.now().isoformat(),
            "approval_type": "auto",
            "reason": "Low risk action auto-approved"
        }

        log_path = os.path.join(self.approval_log_dir, f"AUTO_APPROVAL_{timestamp}.json")
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2)

    def process_approval_decision(self, file_path: str, decision: str):
        """Process an approval decision (approve/reject)."""
        try:
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if decision == "approve":
                # Move to approved
                if filename.startswith("APPROVAL_REQUEST_"):
                    new_filename = filename.replace("APPROVAL_REQUEST_", "APPROVED_")
                else:
                    new_filename = f"APPROVED_{timestamp}_{filename}"

                approved_path = os.path.join(self.approved_dir, new_filename)
                shutil.move(file_path, approved_path)

                # Log approval
                self.log_approval_decision(filename, "approved")
                logger.info(f"Approved: {filename}")

            elif decision == "reject":
                # Move to rejected
                if filename.startswith("APPROVAL_REQUEST_"):
                    new_filename = filename.replace("APPROVAL_REQUEST_", "REJECTED_")
                else:
                    new_filename = f"REJECTED_{timestamp}_{filename}"

                rejected_path = os.path.join(self.rejected_dir, new_filename)
                shutil.move(file_path, rejected_path)

                # Log rejection
                self.log_approval_decision(filename, "rejected")
                logger.info(f"Rejected: {filename}")

        except Exception as e:
            logger.error(f"Error processing approval decision: {e}")

    def log_approval_decision(self, filename: str, decision: str):
        """Log approval decision."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Find the approval record
        for record_file in os.listdir(self.approval_log_dir):
            if record_file.startswith("APPROVAL_RECORD_") and record_file.endswith(".json"):
                record_path = os.path.join(self.approval_log_dir, record_file)
                with open(record_path, 'r', encoding='utf-8') as f:
                    record = json.load(f)

                if record.get("pending_file", "").endswith(filename):
                    # Update record
                    record["status"] = decision
                    record[f"{decision}_at"] = datetime.now().isoformat()

                    # Save updated record
                    with open(record_path, 'w', encoding='-utf-8') as f:
                        json.dump(record, f, indent=2)
                    break

    def check_timeout_approvals(self):
        """Check for approvals that have timed out."""
        now = datetime.now()
        timeout_hours = self.approval_settings.get("approval_timeout_hours", 24)

        for record_file in os.listdir(self.approval_log_dir):
            if record_file.startswith("APPROVAL_RECORD_") and record_file.endswith(".json"):
                record_path = os.path.join(self.approval_log_dir, record_file)
                with open(record_path, 'r', encoding='utf-8') as f:
                    record = json.load(f)

                if record.get("status") == "pending":
                    timeout_at = datetime.fromisoformat(record["timeout_at"])
                    if now > timeout_at:
                        # Timeout - auto-reject
                        pending_file = record.get("pending_file", "")
                        if pending_file:
                            pending_path = os.path.join(self.pending_dir, pending_file)
                            if os.path.exists(pending_path):
                                self.process_approval_decision(pending_path, "reject")
                                record["status"] = "timeout_rejected"
                                record["timeout_rejected_at"] = now.isoformat()

                                with open(record_path, 'w', encoding='utf-8') as f:
                                    json.dump(record, f, indent=2)

    def run(self):
        """Run the approval workflow system."""
        logger.info("Starting Approval Workflow system...")

        # Set up file watcher
        event_handler = ApprovalFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.needs_action_dir, recursive=False)
        observer.start()

        try:
            while True:
                # Check for timeout approvals every hour
                self.check_timeout_approvals()
                time.sleep(3600)  # Check every hour

        except KeyboardInterrupt:
            logger.info("Approval Workflow stopped by user")
            observer.stop()
        except Exception as e:
            logger.error(f"Error in Approval Workflow: {e}")
            observer.stop()

        observer.join()

class ApprovalFileHandler(FileSystemEventHandler):
    """File system event handler for approval workflow."""

    def __init__(self, approval_workflow: ApprovalWorkflow):
        self.approval_workflow = approval_workflow

    def on_created(self, event):
        if not event.is_directory:
            # Wait a moment for file to be fully written
            time.sleep(0.5)
            self.approval_workflow.process_new_action(event.src_path)

    def on_moved(self, event):
        """Handle file moves (approvals/rejections)."""
        if not event.is_directory:
            # Check if moved to approved/rejected folder
            if event.dest_path.startswith(self.approval_workflow.approved_dir):
                self.approval_workflow.process_approval_decision(event.dest_path, "approve")
            elif event.dest_path.startswith(self.approval_workflow.rejected_dir):
                self.approval_workflow.process_approval_decision(event.dest_path, "reject")

if __name__ == "__main__":
    # For testing
    workflow = ApprovalWorkflow()

    # Create a test action file
    test_content = """# Test Action

**Type:** external_email
**Priority:** Medium

This is a test action that requires approval.
"""

    test_file = os.path.join(workflow.needs_action_dir, "TEST_ACTION.md")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)

    print(f"Created test action file: {test_file}")
    print("Approval workflow will process this file automatically.")