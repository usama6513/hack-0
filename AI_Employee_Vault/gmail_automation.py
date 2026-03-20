#!/usr/bin/env python3
"""
Gmail Automation Script
Automatically monitors Gmail and sends emails using your credentials.
"""

import os
import json
import time
import logging
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gmail_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.compose']

class GmailAutomation:
    """
    Automated Gmail monitoring and sending.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.sent_dir = os.path.join(vault_path, "Sent")
        self.drafts_dir = os.path.join(vault_path, "Drafts")
        self.logs_dir = os.path.join(vault_path, "Logs")
        self.service = None

        # Ensure directories exist
        for directory in [self.sent_dir, self.drafts_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

        # Load email templates
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

    def authenticate(self):
        """Authenticate with Gmail API using existing credentials."""
        creds = None
        token_path = os.path.join(self.vault_path, "token.json")
        credentials_path = "../credentials.json"

        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    logger.error(f"Gmail credentials file not found: {credentials_path}")
                    logger.info("Please ensure credentials.json is in the parent directory")
                    return False

                logger.info("Starting Gmail authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")
        return True

    def get_unread_emails(self, max_results=10):
        """Get unread emails from Gmail."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            return messages
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return []

    def get_email_details(self, message_id):
        """Get detailed information about an email."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract email details
            email_data = {
                'id': message_id,
                'snippet': message.get('snippet', ''),
                'headers': {}
            }

            # Extract headers
            headers = message['payload'].get('headers', [])
            for header in headers:
                name = header['name'].lower()
                value = header['value']
                email_data['headers'][name] = value

            return email_data
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return None

    def send_email(self, to, subject, body, cc=None, bcc=None, attachments=None):
        """Send an email directly through Gmail."""
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = 'me'  # Use authenticated account
            message['subject'] = subject

            if cc:
                message['cc'] = ', '.join(cc) if isinstance(cc, list) else cc
            if bcc:
                message['bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc

            # Add body
            message.attach(MIMEText(body, 'plain'))

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send email
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"Email sent successfully. Message ID: {send_message['id']}")

            # Log sent email
            self.log_sent_email(to, subject, body, send_message['id'])

            return True

        except HttpError as error:
            logger.error(f'An error occurred while sending email: {error}')
            return False

    def log_sent_email(self, to, subject, body, message_id):
        """Log sent email for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.sent_dir, f"sent_email_{timestamp}.json")

        log_data = {
            "message_id": message_id,
            "to": to,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now().isoformat()
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)

    def monitor_inbox(self, check_interval=300):
        """Monitor Gmail inbox for new emails."""
        logger.info(f"Starting Gmail inbox monitoring (interval: {check_interval} seconds)")

        while True:
            try:
                logger.info("Checking Gmail for new emails...")

                # Get unread emails
                messages = self.get_unread_emails()

                if messages:
                    logger.info(f"Found {len(messages)} unread emails")

                    for message in messages:
                        email_data = self.get_email_details(message['id'])

                        if email_data:
                            # Process email
                            self.process_new_email(email_data)

                            # Mark as read
                            self.mark_email_as_read(message['id'])
                else:
                    logger.info("No new unread emails")

                logger.info(f"Check complete. Sleeping for {check_interval} seconds...")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Gmail monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in Gmail monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retry

    def process_new_email(self, email_data):
        """Process a new email and create action file."""
        from_email = email_data['headers'].get('from', 'Unknown')
        subject = email_data['headers'].get('subject', 'No Subject')
        snippet = email_data.get('snippet', '')

        # Analyze email priority
        priority = self.analyze_email_priority(email_data)

        # Create action file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"GMAIL_{priority}_{timestamp}_{email_data['id'][:8]}.json"
        file_path = os.path.join(self.vault_path, "Needs_Action", filename)

        action_data = {
            "type": "gmail_email",
            "priority": priority,
            "from": from_email,
            "subject": subject,
            "snippet": snippet,
            "message_id": email_data['id'],
            "received_at": datetime.now().isoformat(),
            "status": "unread",
            "suggested_actions": [
                "Review email content",
                "Draft response if needed",
                "Categorize by priority"
            ]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(action_data, f, indent=2)

        logger.info(f"Created action file for email: {filename}")

    def analyze_email_priority(self, email_data):
        """Analyze email priority."""
        subject = email_data['headers'].get('subject', '').lower()
        from_email = email_data['headers'].get('from', '').lower()
        snippet = email_data.get('snippet', '').lower()

        # High priority keywords
        high_priority_keywords = ['urgent', 'asap', 'emergency', 'critical', 'important']

        # Check for high priority
        if any(keyword in subject + snippet for keyword in high_priority_keywords):
            return "HIGH"

        # Medium priority for business emails
        if any(domain in from_email for domain in ['@company.com', '@client.com']):
            return "MEDIUM"

        return "LOW"

    def mark_email_as_read(self, message_id):
        """Mark an email as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Marked email {message_id} as read")
        except HttpError as error:
            logger.error(f'Error marking email as read: {error}')

    def create_draft_email(self, to, subject, body):
        """Create a draft email."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = os.path.join(self.drafts_dir, f"email_draft_{timestamp}.json")

        draft_data = {
            "to": to,
            "subject": subject,
            "body": body,
            "created_at": datetime.now().isoformat(),
            "status": "draft"
        }

        with open(draft_file, 'w', encoding='utf-8') as f:
            json.dump(draft_data, f, indent=2)

        logger.info(f"Email draft created: {draft_file}")
        return draft_file

    def send_bulk_emails(self, recipients, subject, body, delay_seconds=2):
        """Send emails to multiple recipients."""
        logger.info(f"Starting bulk email send to {len(recipients)} recipients")

        for i, recipient in enumerate(recipients):
            try:
                success = self.send_email(recipient, subject, body)
                if success:
                    logger.info(f"Email {i+1}/{len(recipients)} sent to {recipient}")
                else:
                    logger.error(f"Failed to send email {i+1} to {recipient}")

                # Delay between sends
                if i < len(recipients) - 1:
                    time.sleep(delay_seconds)

            except Exception as e:
                logger.error(f"Error sending email {i+1} to {recipient}: {e}")

    def auto_reply_to_emails(self, query, reply_subject, reply_body):
        """Auto-reply to emails matching a query."""
        try:
            # Search for emails
            results = self.service.users().messages().list(
                userId='me',
                q=query
            ).execute()

            messages = results.get('messages', [])

            for message in messages:
                email_data = self.get_email_details(message['id'])
                if email_data:
                    from_email = email_data['headers'].get('from', '')

                    # Send auto-reply
                    self.send_email(from_email, reply_subject, reply_body)

                    # Mark as read
                    self.mark_email_as_read(message['id'])

                    logger.info(f"Auto-replied to email from {from_email}")

        except HttpError as error:
            logger.error(f'Error in auto-reply: {error}')

def main():
    """Main function for standalone Gmail automation."""
    import argparse

    parser = argparse.ArgumentParser(description="Gmail Automation Tool")
    parser.add_argument("--vault", default="./", help="Vault directory path")
    parser.add_argument("--send", nargs=3, metavar=("TO", "SUBJECT", "BODY"), help="Send an email")
    parser.add_argument("--monitor", action="store_true", help="Monitor inbox continuously")
    parser.add_argument("--check", action="store_true", help="Check inbox once")
    parser.add_argument("--bulk", nargs=3, metavar=("RECIPIENTS_FILE", "SUBJECT", "BODY"), help="Send bulk emails")
    parser.add_argument("--auto-reply", nargs=3, metavar=("QUERY", "SUBJECT", "BODY"), help="Auto-reply to emails matching query")

    args = parser.parse_args()

    gmail = GmailAutomation(vault_path=args.vault)

    # Authenticate first
    if not gmail.authenticate():
        print("Failed to authenticate with Gmail")
        return 1

    if args.send:
        # Send single email
        to, subject, body = args.send
        success = gmail.send_email(to, subject, body)
        if success:
            print(f"[OK] Email sent to {to}")
        else:
            print(f"[ERROR] Failed to send email to {to}")
    elif args.monitor:
        # Monitor inbox
        gmail.monitor_inbox()
    elif args.check:
        # Check inbox once
        messages = gmail.get_unread_emails()
        if messages:
            print(f"Found {len(messages)} unread emails")
            for msg in messages[:3]:  # Show first 3
                email_data = gmail.get_email_details(msg['id'])
                if email_data:
                    from_clean = email_data['headers'].get('from', 'Unknown').encode('ascii', 'ignore').decode('ascii')
                    subject_clean = email_data['headers'].get('subject', 'No Subject').encode('ascii', 'ignore').decode('ascii')
                    snippet_clean = email_data['snippet'][:50].encode('ascii', 'ignore').decode('ascii')
                    print(f"- From: {from_clean}")
                    print(f"  Subject: {subject_clean}")
                    print(f"  Snippet: {snippet_clean}...")
        else:
            print("No unread emails")
    elif args.bulk:
        # Send bulk emails
        recipients_file, subject, body = args.bulk
        with open(recipients_file, 'r') as f:
            recipients = [line.strip() for line in f if line.strip()]
        gmail.send_bulk_emails(recipients, subject, body)
    elif args.auto_reply:
        # Auto-reply to emails
        query, subject, body = args.auto_reply
        gmail.auto_reply_to_emails(query, subject, body)
    else:
        # Default: check inbox once
        messages = gmail.get_unread_emails()
        if messages:
            print(f"Found {len(messages)} unread emails")
        else:
            print("No unread emails")

if __name__ == "__main__":
    main()