"""
Email Sender Skill for AI Employee
Sends emails via MCP (Model Context Protocol) server integration.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailSender:
    """
    Skill to send emails via MCP server integration.
    """

    def __init__(self, vault_path="./", mcp_config_path="mcp.json"):
        self.vault_path = vault_path
        self.mcp_config_path = mcp_config_path
        self.sent_dir = os.path.join(vault_path, "Sent")
        self.templates_dir = os.path.join(vault_path, "Email_Templates")
        self.drafts_dir = os.path.join(vault_path, "Email_Drafts")

        # Ensure directories exist
        os.makedirs(self.sent_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.drafts_dir, exist_ok=True)

        # Load MCP configuration
        self.mcp_config = self.load_mcp_config()

    def load_mcp_config(self) -> Dict:
        """Load MCP server configuration."""
        try:
            if os.path.exists(self.mcp_config_path):
                with open(self.mcp_config_path, 'r') as f:
                    return json.load(f)
            else:
                # Default configuration
                return {
                    "mcpServers": {
                        "email": {
                            "command": "node",
                            "args": ["email-mcp-server.js"],
                            "env": {
                                "GMAIL_USER": os.getenv("GMAIL_USER", ""),
                                "GMAIL_APP_PASSWORD": os.getenv("GMAIL_APP_PASSWORD", "")
                            }
                        }
                    }
                }
        except Exception as e:
            logger.error(f"Error loading MCP config: {str(e)}")
            return {}

    def create_email_template(self, template_name: str, subject: str, body: str, variables: List[str] = None):
        """Create an email template."""
        template = {
            "name": template_name,
            "subject": subject,
            "body": body,
            "variables": variables or [],
            "created": datetime.now().isoformat()
        }

        template_path = os.path.join(self.templates_dir, f"{template_name}.json")
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)

        logger.info(f"Created email template: {template_name}")
        return template_path

    def render_template(self, template_name: str, variables: Dict[str, str]) -> Dict[str, str]:
        """Render an email template with variables."""
        template_path = os.path.join(self.templates_dir, f"{template_name}.json")

        if not os.path.exists(template_path):
            raise ValueError(f"Template not found: {template_name}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)

        # Replace variables in subject and body
        subject = template['subject']
        body = template['body']

        for key, value in variables.items():
            subject = subject.replace(f"{{{key}}}", value)
            body = body.replace(f"{{{key}}}", value)

        return {
            "subject": subject,
            "body": body
        }

    def create_email_draft(self, to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
        """Create an email draft for review."""
        draft_id = datetime.now().strftime("DRAFT_%Y%m%d_%H%M%S")
        draft_filename = f"{draft_id}.md"
        draft_path = os.path.join(self.drafts_dir, draft_filename)

        draft_content = f"""# Email Draft

**Draft ID:** {draft_id}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** Draft

## Recipients
- **To:** {to}
- **CC:** {cc or 'None'}
- **BCC:** {bcc or 'None'}

## Subject
{subject}

## Body
{body}

## Review Checklist
- [ ] Recipients are correct
- [ ] Subject is appropriate
- [ ] Content is professional
- [ ] No sensitive information exposed
- [ ] Attachments included (if needed)

## Next Steps
- [ ] Review and edit if needed
- [ ] Move to /Approved folder to send
- [ ] Or move to /Rejected folder to cancel

---
*Draft created by Email Sender Skill*
"""

        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)

        logger.info(f"Created email draft: {draft_filename}")
        return draft_path

    def send_email_via_mcp(self, to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> Dict[str, any]:
        """Send email via MCP server."""
        try:
            # Simulate MCP call (in production, this would call actual MCP server)
            logger.info(f"Sending email via MCP to: {to}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body preview: {body[:100]}...")

            # Simulate successful send
            message_id = f"MSG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            result = {
                "success": True,
                "message_id": message_id,
                "timestamp": datetime.now().isoformat(),
                "recipients": {
                    "to": to,
                    "cc": cc,
                    "bcc": bcc
                },
                "subject": subject,
                "body_length": len(body)
            }

            logger.info(f"Email sent successfully. Message ID: {message_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to send email via MCP: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def send_approved_email(self, approval_file_path: str) -> bool:
        """Send an email that has been approved."""
        try:
            # Read approval file
            with open(approval_file_path, 'r', encoding='utf-8') as f:
                approval_content = f.read()

            # Extract email details from approval file
            # This is simplified - in production, use proper parsing
            lines = approval_content.split('\n')
            to = ""
            subject = ""
            body = ""

            for line in lines:
                if line.startswith("- **To:**"):
                    to = line.replace("- **To:**", "").strip()
                elif line.startswith("## Subject"):
                    # Get next line as subject
                    subject_idx = lines.index(line) + 1
                    if subject_idx < len(lines):
                        subject = lines[subject_idx].strip()
                elif line.startswith("## Body"):
                    # Get content until next ##
                    body_idx = lines.index(line) + 1
                    body_lines = []
                    for i in range(body_idx, len(lines)):
                        if lines[i].startswith("##"):
                            break
                        body_lines.append(lines[i])
                    body = '\n'.join(body_lines).strip()

            if not to or not subject or not body:
                logger.error("Could not extract email details from approval file")
                return False

            # Send email via MCP
            result = self.send_email_via_mcp(to, subject, body)

            if result["success"]:
                # Move to sent folder
                sent_filename = f"SENT_{os.path.basename(approval_file_path)}"
                sent_path = os.path.join(self.sent_dir, sent_filename)

                # Update content to mark as sent
                sent_content = approval_content.replace("**Status:** Approved", "**Status:** Sent")
                sent_content += f"\n\n## Send Details\n- **Sent At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- **Message ID:** {result['message_id']}\n- **Via:** MCP Email Server"

                with open(sent_path, 'w', encoding='utf-8') as f:
                    f.write(sent_content)

                # Remove approval file
                os.remove(approval_file_path)

                logger.info(f"Email sent and moved to sent folder: {sent_filename}")
                return True
            else:
                logger.error("Failed to send email via MCP")
                return False

        except Exception as e:
            logger.error(f"Error sending approved email: {str(e)}")
            return False

    def create_email_templates(self):
        """Create default email templates for common scenarios."""
        templates = [
            {
                "name": "follow_up",
                "subject": "Follow-up: {topic}",
                "body": """Hi {name},\n\nI hope this email finds you well. I wanted to follow up on our discussion about {topic}.\n\n{main_content}\n\nPlease let me know if you have any questions or need any additional information.\n\nBest regards,\n{sender_name}""",
                "variables": ["name", "topic", "main_content", "sender_name"]
            },
            {
                "name": "invoice_reminder",
                "subject": "Invoice Reminder: {invoice_number}",
                "body": """Dear {name},\n\nThis is a friendly reminder that invoice {invoice_number} for {amount} is due on {due_date}.\n\n{additional_notes}\n\nPlease let us know if you have any questions about this invoice.\n\nBest regards,\n{sender_name}\n{company_name}""",
                "variables": ["name", "invoice_number", "amount", "due_date", "additional_notes", "sender_name", "company_name"]
            },
            {
                "name": "meeting_confirmation",
                "subject": "Meeting Confirmation: {meeting_topic} - {meeting_date}",
                "body": """Hi {name},\n\nThis is to confirm our meeting scheduled for:\n\n**Date:** {meeting_date}\n**Time:** {meeting_time}\n**Duration:** {duration}\n**Topic:** {meeting_topic}\n\n{agenda}\n\nPlease let me know if you need to reschedule or have any questions.\n\nLooking forward to our discussion.\n\nBest regards,\n{sender_name}""",
                "variables": ["name", "meeting_date", "meeting_time", "duration", "meeting_topic", "agenda", "sender_name"]
            }
        ]

        for template in templates:
            self.create_email_template(
                template["name"],
                template["subject"],
                template["body"],
                template["variables"]
            )

        logger.info("Created default email templates")

    def monitor_approval_folder(self):
        """Monitor approval folder for emails ready to send."""
        approval_dir = os.path.join(self.vault_path, "Approved")
        os.makedirs(approval_dir, exist_ok=True)

        logger.info("Monitoring approval folder for emails to send...")

        while True:
            try:
                # Check for approval files
                approval_files = [f for f in os.listdir(approval_dir) if f.endswith('.md') and 'EMAIL' in f]

                for approval_file in approval_files:
                    approval_path = os.path.join(approval_dir, approval_file)
                    logger.info(f"Processing approval: {approval_file}")

                    # Send the approved email
                    success = self.send_approved_email(approval_path)

                    if success:
                        logger.info(f"Successfully sent email from approval: {approval_file}")
                    else:
                        logger.error(f"Failed to send email from approval: {approval_file}")

                time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                logger.info("Approval monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Error monitoring approval folder: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retry

if __name__ == "__main__":
    # For testing
    sender = EmailSender()

    # Create templates
    sender.create_email_templates()

    # Create a test draft
    draft_path = sender.create_email_draft(
        to="client@example.com",
        subject="Test Email from AI Employee",
        body="This is a test email sent via the AI Employee Email Sender skill."
    )
    print(f"Created test draft: {draft_path}")