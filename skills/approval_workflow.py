"""
Approval Workflow Skill for AI Employee
Implements human-in-the-loop approval for sensitive actions.
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApprovalWorkflow:
    """
    Human-in-the-loop approval workflow for sensitive actions.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.pending_dir = os.path.join(vault_path, "Pending_Approval")
        self.approved_dir = os.path.join(vault_path, "Approved")
        self.rejected_dir = os.path.join(vault_path, "Rejected")
        self.approval_log = os.path.join(vault_path, "approval_log.json")

        # Ensure directories exist
        for directory in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            os.makedirs(directory, exist_ok=True)

        # Approval rules
        self.approval_rules = self.load_approval_rules()

    def load_approval_rules(self) -> Dict:
        """Load approval rules from configuration."""
        rules_file = os.path.join(self.vault_path, "approval_rules.json")

        default_rules = {
            "sensitive_actions": {
                "financial_transactions": {
                    "threshold": 500,  # USD
                    "requires_approval": True,
                    "approvers": ["human"],
                    "timeout_hours": 24
                },
                "email_sending": {
                    "external_domains": True,
                    "requires_approval": True,
                    "approvers": ["human"],
                    "timeout_hours": 2
                },
                "social_media_posting": {
                    "business_accounts": True,
                    "requires_approval": True,
                    "approvers": ["human"],
                    "timeout_hours": 4
                },
                "data_deletion": {
                    "any": True,
                    "requires_approval": True,
                    "approvers": ["human"],
                    "timeout_hours": 1
                }
            },
            "approval_workflow": {
                "notification_methods": ["file", "log"],
                "escalation_after_hours": 48,
                "auto_approve_on_timeout": False
            }
        }

        try:
            if os.path.exists(rules_file):
                with open(rules_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default rules
                with open(rules_file, 'w') as f:
                    json.dump(default_rules, f, indent=2)
                return default_rules
        except Exception as e:
            logger.error(f"Error loading approval rules: {str(e)}")
            return default_rules

    def requires_approval(self, action_type: str, details: Dict) -> bool:
        """Check if an action requires approval based on rules."""
        rules = self.approval_rules.get("sensitive_actions", {})

        if action_type in rules:
            rule = rules[action_type]

            # Check specific conditions
            if action_type == "financial_transactions":
                amount = details.get("amount", 0)
                return amount > rule.get("threshold", 0)
            elif action_type == "email_sending":
                return rule.get("external_domains", False) and not details.get("internal", False)
            elif action_type == "social_media_posting":
                return rule.get("business_accounts", False)
            elif action_type == "data_deletion":
                return rule.get("any", False)

        return False

    def create_approval_request(self, action_type: str, details: Dict, requester: str = "AI") -> str:
        """Create an approval request file."""
        approval_id = datetime.now().strftime("APPROVAL_%Y%m%d_%H%M%S")
        filename = f"{approval_id}_{action_type}.md"
        filepath = os.path.join(self.pending_dir, filename)

        # Calculate expiration time
        rule = self.approval_rules.get("sensitive_actions", {}).get(action_type, {})
        timeout_hours = rule.get("timeout_hours", 24)
        expires_at = datetime.now() + timedelta(hours=timeout_hours)

        approval_content = f"""# Approval Required: {action_type.replace('_', ' ').title()}

**Approval ID:** {approval_id}
**Action Type:** {action_type}
**Requested By:** {requester}
**Requested At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Expires At:** {expires_at.strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** {details.get('priority', 'Normal')}

## Action Details
{json.dumps(details, indent=2)}

## Why This Requires Approval
{self.get_approval_reason(action_type, details)}

## Approval Options
1. **APPROVE** - Move this file to `/Approved` folder
2. **REJECT** - Move this file to `/Rejected` folder
3. **MODIFY** - Edit the details and re-submit

## Approval Instructions
1. Review the action details above
2. Consider the business impact and risks
3. Make your decision within {timeout_hours} hours
4. Move this file to the appropriate folder

## Business Impact
{self.assess_business_impact(action_type, details)}

## Risk Assessment
{self.assess_risk(action_type, details)}

## Approval Checklist
- [ ] I have reviewed the action details
- [ ] I understand the business implications
- [ ] I have verified the request is legitimate
- [ ] I am comfortable with the associated risks

## Decision
**Decision:** [ ] APPROVE [ ] REJECT [ ] MODIFY
**Reason:** ________________________________
**Approved By:** ____________________________
**Date:** ___________________________________

---
*Approval request generated by AI Employee*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        # Log approval request
        self.log_approval_request(approval_id, action_type, details, requester)

        logger.info(f"Created approval request: {filename}")
        return filepath

    def get_approval_reason(self, action_type: str, details: Dict) -> str:
        """Get the reason why approval is required."""
        reasons = {
            "financial_transactions": "This financial transaction exceeds the automatic approval threshold.",
            "email_sending": "This email will be sent to external recipients and requires human review.",
            "social_media_posting": "This will be posted to business social media accounts and affects company image.",
            "data_deletion": "This involves deleting data which is irreversible and requires careful consideration."
        }
        return reasons.get(action_type, "This action requires human approval based on configured rules.")

    def assess_business_impact(self, action_type: str, details: Dict) -> str:
        """Assess the business impact of the action."""
        impacts = {
            "financial_transactions": "- Direct financial impact\n- Affects cash flow\n- May have tax implications",
            "email_sending": "- Represents company to external parties\n- Affects professional relationships\n- May contain sensitive information",
            "social_media_posting": "- Public representation of company\n- Affects brand image\n- Potentially viral reach",
            "data_deletion": "- Permanent loss of information\n- May affect compliance\n- Could impact business operations"
        }
        return impacts.get(action_type, "- Moderate business impact\n- Requires careful consideration")

    def assess_risk(self, action_type: str, details: Dict) -> str:
        """Assess the risk of the action."""
        risks = {
            "financial_transactions": "- Financial loss risk\n- Fraud possibility\n- Accounting errors",
            "email_sending": "- Information disclosure\n- Professional reputation risk\n- Legal compliance issues",
            "social_media_posting": "- Reputational damage\n- Public backlash\n- Competitive disadvantage",
            "data_deletion": "- Data loss\n- Compliance violations\n- Operational disruption"
        }
        return risks.get(action_type, "- Standard operational risk\n- Mitigated by approval process")

    def log_approval_request(self, approval_id: str, action_type: str, details: Dict, requester: str):
        """Log approval request for audit trail."""
        log_entry = {
            "approval_id": approval_id,
            "action_type": action_type,
            "requester": requester,
            "requested_at": datetime.now().isoformat(),
            "details": details,
            "status": "pending"
        }

        # Load existing log
        log_data = []
        if os.path.exists(self.approval_log):
            with open(self.approval_log, 'r') as f:
                log_data = json.load(f)

        # Add new entry
        log_data.append(log_entry)

        # Save log
        with open(self.approval_log, 'w') as f:
            json.dump(log_data, f, indent=2)

    def process_approval_decision(self, file_path: str, decision: str):
        """Process an approval decision."""
        filename = os.path.basename(file_path)
        approval_id = filename.split('_')[0]

        if decision == "approved":
            new_path = os.path.join(self.approved_dir, filename)
            shutil.move(file_path, new_path)
            self.update_approval_log(approval_id, "approved", datetime.now().isoformat())
            logger.info(f"Approved: {filename}")

        elif decision == "rejected":
            new_path = os.path.join(self.rejected_dir, filename)
            shutil.move(file_path, new_path)
            self.update_approval_log(approval_id, "rejected", datetime.now().isoformat())
            logger.info(f"Rejected: {filename}")

        elif decision == "modified":
            logger.info(f"Modified: {filename} - requires re-review")
            # Keep in pending but log modification
            self.update_approval_log(approval_id, "modified", datetime.now().isoformat())

    def update_approval_log(self, approval_id: str, status: str, timestamp: str):
        """Update approval log with decision."""
        if os.path.exists(self.approval_log):
            with open(self.approval_log, 'r') as f:
                log_data = json.load(f)

            # Find and update the entry
            for entry in log_data:
                if entry.get("approval_id") == approval_id:
                    entry["status"] = status
                    entry["decision_at"] = timestamp
                    break

            with open(self.approval_log, 'w') as f:
                json.dump(log_data, f, indent=2)

    def check_expired_approvals(self):
        """Check for expired approval requests."""
        expired_approvals = []

        for filename in os.listdir(self.pending_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.pending_dir, filename)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract expiration time
                    if "**Expires At:**" in content:
                        import re
                        expires_match = re.search(r"\*\*Expires At:\*\* (.+)", content)
                        if expires_match:
                            expires_str = expires_match.group(1).strip()
                            expires_at = datetime.strptime(expires_str, '%Y-%m-%d %H:%M:%S')

                            if datetime.now() > expires_at:
                                expired_approvals.append(filepath)

                except Exception as e:
                    logger.error(f"Error checking expired approval {filename}: {str(e)}")

        return expired_approvals

    def handle_expired_approval(self, approval_path: str):
        """Handle expired approval based on rules."""
        # Default to rejection for safety
        filename = os.path.basename(approval_path)
        new_path = os.path.join(self.rejected_dir, f"EXPIRED_{filename}")
        shutil.move(approval_path, new_path)

        # Log expiration
        approval_id = filename.split('_')[0]
        self.update_approval_log(approval_id, "expired", datetime.now().isoformat())

        logger.warning(f"Expired approval moved to rejected: {filename}")

    def create_approval_summary(self) -> str:
        """Create a summary of current approval status."""
        pending_count = len([f for f in os.listdir(self.pending_dir) if f.endswith('.md')])
        approved_count = len([f for f in os.listdir(self.approved_dir) if f.endswith('.md')])
        rejected_count = len([f for f in os.listdir(self.rejected_dir) if f.endswith('.md')])

        summary = f"""# Approval Workflow Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Status
- **Pending Approval:** {pending_count}
- **Approved:** {approved_count}
- **Rejected:** {rejected_count}

## Pending Actions
"""

        # List pending approvals
        for filename in os.listdir(self.pending_dir):
            if filename.endswith('.md'):
                summary += f"- {filename}\n"

        if pending_count == 0:
            summary += "- No pending approvals\n"

        summary += f"""
## Recent Activity
Check the approval log for detailed history: {self.approval_log}

## Next Actions
1. Review pending approvals in {self.pending_dir}
2. Make approval decisions by moving files to appropriate folders
3. Monitor for expired approvals
"""

        return summary

    def monitor_approvals(self):
        """Monitor approval folder for changes."""
        class ApprovalHandler(FileSystemEventHandler):
            def __init__(self, approval_workflow):
                self.approval_workflow = approval_workflow

            def on_modified(self, event):
                if event.is_directory:
                    return

                # Check if it's a decision file
                if "APPROVED" in event.src_path or "REJECTED" in event.src_path:
                    # Process the decision
                    filename = os.path.basename(event.src_path)
                    if "APPROVED" in filename:
                        self.approval_workflow.process_approval_decision(event.src_path, "approved")
                    elif "REJECTED" in filename:
                        self.approval_workflow.process_approval_decision(event.src_path, "rejected")

        handler = ApprovalHandler(self)
        observer = Observer()
        observer.schedule(handler, self.vault_path, recursive=True)

        logger.info("Starting approval monitoring...")
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("Approval monitoring stopped")

        observer.join()

if __name__ == "__main__":
    # For testing
    approval_workflow = ApprovalWorkflow()

    # Test approval request
    test_details = {
        "action": "Send email to client@example.com",
        "subject": "Project proposal",
        "reason": "External domain requires approval"
    }

    approval_path = approval_workflow.create_approval_request(
        "email_sending",
        test_details,
        "AI Employee"
    )

    print(f"Created test approval request: {approval_path}")
    print("\nApproval Summary:")
    print(approval_workflow.create_approval_summary())