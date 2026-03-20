"""
Email Sender Skill for AI Employee - Silver Tier
Sends emails using MCP (Model Context Protocol) integration.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_sender.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailSender:
    """
    Email sender that uses MCP (Model Context Protocol) for sending emails.
    Can use either external MCP servers or local SMTP.
    """

    def __init__(self, vault_path="./", mcp_config_path="mcp_config.json"):
        self.vault_path = vault_path
        self.mcp_config_path = mcp_config_path
        self.sent_dir = os.path.join(vault_path, "Sent")
        self.drafts_dir = os.path.join(vault_path, "Drafts")
        self.templates_dir = os.path.join(vault_path, "Templates")
        self.needs_action_dir = os.path.join(vault_path, "Needs_Action")

        # Ensure directories exist
        for directory in [self.sent_dir, self.drafts_dir, self.templates_dir, self.needs_action_dir]:
            os.makedirs(directory, exist_ok=True)

        # Load MCP configuration
        self.mcp_config = self.load_mcp_config()

        # Email templates
        self.email_templates = {
            "follow_up": {
                "subject": "Follow-up: {topic}",
                "body": """Hi {name},\n\nI wanted to follow up on our recent conversation about {topic}.\n\n{main_content}\n\nPlease let me know if you have any questions or would like to discuss this further.\n\nBest regards,\n{sender_name}"""
            },
            "meeting_request": {
                "subject": "Meeting Request: {topic}",
                "body": """Hi {name},\n\nI hope this email finds you well. I'd like to schedule a meeting to discuss {topic}.\n\n{main_content}\n\nWould you be available for a {duration} meeting sometime this week?\n\nLooking forward to your response.\n\nBest regards,\n{sender_name}"""
            },
            "proposal": {
                "subject": "Proposal: {topic}",
                "body": """Hi {name},\n\nThank you for your interest in our services. As discussed, please find our proposal for {topic} below:\n\n{main_content}\n\nWe're excited about the opportunity to work together. Please review and let us know if you have any questions.\n\nBest regards,\n{sender_name}"""
            },
            "invoice": {
                "subject": "Invoice #{invoice_number} - {amount}",
                "body": """Hi {name},\n\nPlease find attached invoice #{invoice_number} for {amount}.\n\n{main_content}\n\nPayment terms: {payment_terms}\n\nThank you for your business!\n\nBest regards,\n{sender_name}"""
            }
        }

    def load_mcp_config(self) -> Dict:
        """Load MCP configuration from file."""
        default_config = {
            "mcp_enabled": True,
            "servers": {
                "email": {
                    "enabled": True,
                    "endpoint": "http://localhost:8080/mcp/email",
                    "api_key": "",
                    "timeout": 30
                }
            },
            "smtp_fallback": {
                "enabled": True,
                "host": "smtp.gmail.com",
                "port": 587,
                "username": "",
                "password": "",
                "use_tls": True
            }
        }

        if os.path.exists(self.mcp_config_path):
            try:
                with open(self.mcp_config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading MCP config: {e}")
                return default_config
        else:
            # Create default config file
            try:
                with open(self.mcp_config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default MCP config at {self.mcp_config_path}")
            except Exception as e:
                logger.error(f"Error creating MCP config: {e}")
            return default_config

    def create_email_draft(self, recipient: str, subject: str, body: str,
                          template_name: str = None, variables: Dict = None) -> str:
        """Create an email draft."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_filename = f"email_draft_{timestamp}.md"
        draft_path = os.path.join(self.drafts_dir, draft_filename)

        # Use template if specified
        if template_name and template_name in self.email_templates:
            template = self.email_templates[template_name]
            if variables:
                subject = template["subject"].format(**variables)
                body = template["body"].format(**variables)

        draft_content = f"""# Email Draft

**To:** {recipient}
**Subject:** {subject}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** Draft

## Email Body
{body}

## Sending Options
- [ ] Send immediately
- [ ] Schedule for later
- [ ] Request approval (recommended for external emails)

## Tracking
- [ ] Track delivery
- [ ] Track opens (if supported)
- [ ] Track clicks (if supported)
"""

        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)

        logger.info(f"Created email draft: {draft_filename}")
        return draft_path

    def create_approval_request(self, recipient: str, subject: str, body: str,
                               reason: str = "External email requires approval") -> str:
        """Create approval request for sensitive emails."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_filename = f"APPROVAL_EMAIL_{timestamp}.md"
        approval_path = os.path.join(self.needs_action_dir, approval_filename)

        approval_content = f"""# Email Approval Required

**Type:** Email
**To:** {recipient}
**Subject:** {subject}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** Medium
**Reason:** {reason}

## Email Content
{body}

## Approval Decision
- [ ] **APPROVE** - Move this file to `/Approved` folder to send
- [ ] **REJECT** - Move this file to `/Rejected` folder
- [ ] **MODIFY** - Edit content and re-submit

## Safety Check
- [ ] Recipient is correct
- [ ] Content is appropriate
- [ ] No sensitive information disclosed
- [ ] Aligns with company policies

## Next Steps
Once approved, the email will be sent automatically via MCP server.
"""

        with open(approval_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        logger.info(f"Created email approval request: {approval_filename}")
        return approval_path

    def send_email_via_mcp(self, recipient: str, subject: str, body: str,
                          cc: List[str] = None, bcc: List[str] = None,
                          attachments: List[str] = None) -> bool:
        """Send email using MCP server."""
        if not self.mcp_config.get("mcp_enabled", False):
            logger.error("MCP is disabled in configuration")
            return False

        email_server = self.mcp_config.get("servers", {}).get("email", {})
        if not email_server.get("enabled", False):
            logger.error("Email MCP server is disabled")
            return False

        endpoint = email_server.get("endpoint")
        api_key = email_server.get("api_key")
        timeout = email_server.get("timeout", 30)

        if not endpoint:
            logger.error("No MCP email endpoint configured")
            return False

        # Prepare email payload
        payload = {
            "jsonrpc": "2.0",
            "method": "send_email",
            "params": {
                "to": recipient,
                "subject": subject,
                "body": body,
                "body_type": "text/plain"
            },
            "id": 1
        }

        if cc:
            payload["params"]["cc"] = cc
        if bcc:
            payload["params"]["bcc"] = bcc
        if attachments:
            payload["params"]["attachments"] = attachments

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            logger.info(f"Sending email via MCP to {recipient}")
            response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)

            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    logger.error(f"MCP server error: {result['error']}")
                    return False
                else:
                    logger.info(f"Email sent successfully via MCP")
                    return True
            else:
                logger.error(f"MCP request failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending email via MCP: {e}")
            return False

    def send_email_via_smtp(self, recipient: str, subject: str, body: str,
                           cc: List[str] = None, bcc: List[str] = None) -> bool:
        """Fallback to SMTP if MCP fails."""
        smtp_config = self.mcp_config.get("smtp_fallback", {})
        if not smtp_config.get("enabled", False):
            logger.error("SMTP fallback is disabled")
            return False

        try:
            host = smtp_config.get("host")
            port = smtp_config.get("port", 587)
            username = smtp_config.get("username")
            password = smtp_config.get("password")
            use_tls = smtp_config.get("use_tls", True)

            if not all([host, username, password]):
                logger.error("Incomplete SMTP configuration")
                return False

            # Create message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = recipient
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            logger.info(f"Sending email via SMTP to {recipient}")
            server = smtplib.SMTP(host, port)

            if use_tls:
                server.starttls()

            server.login(username, password)
            recipients = [recipient]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully via SMTP")
            return True

        except Exception as e:
            logger.error(f"Error sending email via SMTP: {e}")
            return False

    def send_email(self, recipient: str, subject: str, body: str,
                  cc: List[str] = None, bcc: List[str] = None,
                  attachments: List[str] = None, require_approval: bool = True) -> bool:
        """Send email with approval workflow if required."""
        if require_approval:
            # Create approval request
            approval_path = self.create_approval_request(recipient, subject, body)
            logger.info(f"Email requires approval. Request created: {approval_path}")
            return False

        # Try MCP first
        if self.send_email_via_mcp(recipient, subject, body, cc, bcc, attachments):
            self.log_sent_email(recipient, subject, body, "MCP")
            return True

        # Fallback to SMTP
        logger.info("MCP failed, trying SMTP fallback")
        if self.send_email_via_smtp(recipient, subject, body, cc, bcc):
            self.log_sent_email(recipient, subject, body, "SMTP")
            return True

        logger.error("Failed to send email via both MCP and SMTP")
        return False

    def log_sent_email(self, recipient: str, subject: str, body: str, method: str):
        """Log sent email for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"sent_email_{timestamp}.md"
        log_path = os.path.join(self.sent_dir, log_filename)

        log_content = f"""# Sent Email Log

**To:** {recipient}
**Subject:** {subject}
**Sent:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Method:** {method}

## Content
{body}

## Delivery Status
- [ ] Delivered (check email provider)
- [ ] Opened (if tracking enabled)
- [ ] Replied (monitor for responses)
"""

        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(log_content)

        logger.info(f"Logged sent email: {log_filename}")

    def process_approved_email(self, approval_file_path: str) -> bool:
        """Process an approved email and send it."""
        try:
            # Read approval file
            with open(approval_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract email details (simple parsing)
            lines = content.split('\n')
            recipient = ""
            subject = ""
            body = ""

            for line in lines:
                if line.startswith('**To:**'):
                    recipient = line.replace('**To:**', '').strip()
                elif line.startswith('**Subject:**'):
                    subject = line.replace('**Subject:**', '').strip()
                elif line.startswith('## Email Content'):
                    # Get content after this line
                    body_start = lines.index(line) + 1
                    body = '\n'.join(lines[body_start:]).strip()
                    break

            if not all([recipient, subject, body]):
                logger.error("Could not extract email details from approval file")
                return False

            # Send the email
            return self.send_email(recipient, subject, body, require_approval=False)

        except Exception as e:
            logger.error(f"Error processing approved email: {e}")
            return False

    def create_email_template(self, name: str, subject: str, body: str):
        """Create a new email template."""
        template = {
            "name": name,
            "subject": subject,
            "body": body
        }

        template_path = os.path.join(self.templates_dir, f"{name}.json")
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)

        logger.info(f"Created email template: {name}")

    def run(self):
        """Monitor for approved emails to send."""
        logger.info("Starting Email Sender service...")

        approved_dir = os.path.join(self.vault_path, "Approved")
        os.makedirs(approved_dir, exist_ok=True)

        while True:
            try:
                # Check for approved email files
                for filename in os.listdir(approved_dir):
                    if filename.startswith("APPROVAL_EMAIL_") and filename.endswith(".md"):
                        file_path = os.path.join(approved_dir, filename)

                        logger.info(f"Processing approved email: {filename}")

                        if self.process_approved_email(file_path):
                            # Move to sent folder
                            sent_path = os.path.join(self.sent_dir, filename.replace("APPROVAL_EMAIL_", "SENT_EMAIL_"))
                            os.rename(file_path, sent_path)
                            logger.info(f"Email sent and moved to sent folder")
                        else:
                            # Move to error folder
                            error_dir = os.path.join(self.vault_path, "Errors")
                            os.makedirs(error_dir, exist_ok=True)
                            error_path = os.path.join(error_dir, filename)
                            os.rename(file_path, error_path)
                            logger.error(f"Failed to send email, moved to error folder")

                time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                logger.info("Email Sender stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in Email Sender: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    # For testing
    sender = EmailSender()

    # Test creating a draft
    draft_path = sender.create_email_draft(
        recipient="test@example.com",
        subject="Test Email",
        body="This is a test email from the AI Employee Email Sender."
    )
    print(f"Created draft: {draft_path}")

    # Test creating approval request
    approval_path = sender.create_approval_request(
        recipient="client@example.com",
        subject="Project Proposal",
        body="Please find attached our proposal for the AI automation project."
    )
    print(f"Created approval request: {approval_path}")