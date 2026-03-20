"""
Gmail Watcher Skill for AI Employee
Monitors Gmail for new emails and creates action files for important messages.
"""

import os
import time
import json
import logging
from datetime import datetime
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

class GmailWatcher:
    """
    Gmail watcher that monitors for new emails and creates action files.
    """

    def __init__(self, vault_path="./", credentials_path="credentials.json", token_path="token.json"):
        self.vault_path = vault_path
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.needs_action_dir = os.path.join(vault_path, "Needs_Action")
        self.service = None
        self.last_history_id = None

        # Ensure directories exist
        os.makedirs(self.needs_action_dir, exist_ok=True)

    def authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Gmail credentials file not found: {self.credentials_path}")
                    logger.info("Please download credentials.json from Google Cloud Console")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")
        return True

    def get_unread_emails(self, max_results=10):
        """Get unread emails from Gmail."""
        try:
            # Query for unread emails
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

            # Extract body if available
            body = self.extract_body(message['payload'])
            email_data['body'] = body

            return email_data

        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return None

    def extract_body(self, payload):
        """Extract email body from payload."""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                        # Simple HTML tag removal (in production, use BeautifulSoup)
                        import re
                        body += re.sub('<[^<]+?>', '', html)
                elif 'parts' in part:
                    body += self.extract_body(part)
        else:
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        return body.strip()

    def analyze_email_priority(self, email_data):
        """Analyze email to determine priority and action needed."""
        priority = "Low"
        action_type = "general_email"
        keywords = []

        # Extract relevant fields
        subject = email_data['headers'].get('subject', '').lower()
        from_email = email_data['headers'].get('from', '').lower()
        body = email_data.get('body', '').lower()
        snippet = email_data.get('snippet', '').lower()

        # Priority keywords
        high_priority_keywords = [
            'urgent', 'asap', 'emergency', 'critical', 'important',
            'deadline', 'expiring', 'expires', 'overdue'
        ]

        medium_priority_keywords = [
            'meeting', 'appointment', 'schedule', 'reminder',
            'invoice', 'payment', 'billing', 'contract'
        ]

        # Check for priority keywords
        content_to_check = subject + " " + body + " " + snippet

        if any(keyword in content_to_check for keyword in high_priority_keywords):
            priority = "High"
        elif any(keyword in content_to_check for keyword in medium_priority_keywords):
            priority = "Medium"

        # Determine action type based on content
        if 'invoice' in content_to_check or 'payment' in content_to_check:
            action_type = "invoice_payment"
            keywords.append("invoice_payment")
        elif 'meeting' in content_to_check or 'schedule' in content_to_check:
            action_type = "meeting_request"
            keywords.append("meeting_request")
        elif 'support' in content_to_check or 'help' in content_to_check:
            action_type = "support_request"
            keywords.append("support_request")
        elif 'proposal' in content_to_check or 'quote' in content_to_check:
            action_type = "business_proposal"
            keywords.append("business_proposal")

        return priority, action_type, keywords

    def should_auto_reply(self, email_data):
        """Determine if email should get an auto-reply."""
        # Simple rules for auto-reply
        subject = email_data['headers'].get('subject', '').lower()
        body = email_data.get('body', '').lower()

        # Auto-reply triggers
        auto_reply_keywords = [
            'out of office', 'vacation', 'away until', 'not available',
            'automatic reply', 'auto-reply', 'on leave'
        ]

        # Check if it's an auto-reply to avoid reply loops
        if any(keyword in subject + body for keyword in auto_reply_keywords):
            return False

        # Check if it's a newsletter or marketing email
        unsubscribe_indicators = ['unsubscribe', 'opt-out', 'manage preferences']
        if any(indicator in body for indicator in unsubscribe_indicators):
            return False

        return True

    def create_action_file(self, email_data, priority, action_type, keywords):
        """Create an action file for the email."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_id = email_data['id'][:8]  # Use first 8 chars of message ID
        filename = f"GMAIL_{action_type.upper()}_{timestamp}_{message_id}.md"

        # Extract email details
        from_email = email_data['headers'].get('from', 'Unknown')
        subject = email_data['headers'].get('subject', 'No Subject')
        body = email_data.get('body', '')
        snippet = email_data.get('snippet', '')

        action_content = f"""# Gmail {action_type.replace('_', ' ').title()}

**Type:** {action_type}
**From:** {from_email}
**Subject:** {subject}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** {priority}
**Message ID:** {email_data['id']}

## Email Content
{body[:500]}{'...' if len(body) > 500 else ''}

## Keywords Detected
{', '.join(keywords) if keywords else 'None'}

## Suggested Actions
- [ ] Review email content
- [ ] Draft appropriate response
- [ ] {self.get_suggested_action(action_type)}

## Auto-Reply Eligible
{'Yes' if self.should_auto_reply(email_data) else 'No'}

---
*Detected by Gmail Watcher*
"""

        file_path = os.path.join(self.needs_action_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(action_content)

        logger.info(f"Created action file: {filename}")
        return file_path

    def get_suggested_action(self, action_type):
        """Get suggested action based on email type."""
        suggestions = {
            "invoice_payment": "Process invoice/payment request",
            "meeting_request": "Check calendar and respond",
            "support_request": "Provide support or escalate",
            "business_proposal": "Review and prepare response",
            "general_email": "Respond appropriately"
        }
        return suggestions.get(action_type, "Respond appropriately")

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

    def run(self):
        """Main run loop for Gmail watcher."""
        logger.info("Starting Gmail Watcher...")

        if not self.authenticate():
            return

        try:
            while True:
                logger.info("Checking Gmail for new emails...")

                # Get unread emails
                messages = self.get_unread_emails()

                if messages:
                    logger.info(f"Found {len(messages)} unread emails")

                    for message in messages:
                        email_data = self.get_email_details(message['id'])

                        if email_data:
                            # Analyze email
                            priority, action_type, keywords = self.analyze_email_priority(email_data)

                            # Create action file
                            self.create_action_file(email_data, priority, action_type, keywords)

                            # Mark as read to avoid reprocessing
                            self.mark_email_as_read(message['id'])

                else:
                    logger.info("No new unread emails")

                logger.info(f"Check complete. Sleeping for 60 seconds...")
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Gmail Watcher stopped by user")
        except Exception as e:
            logger.error(f"Error in Gmail Watcher: {str(e)}")

    def run_single_check(self):
        """Run a single check (useful for testing)."""
        logger.info("Running single Gmail check...")

        if not self.authenticate():
            return

        try:
            messages = self.get_unread_emails()

            if messages:
                logger.info(f"Found {len(messages)} unread emails")

                for message in messages:
                    email_data = self.get_email_details(message['id'])

                    if email_data:
                        priority, action_type, keywords = self.analyze_email_priority(email_data)
                        self.create_action_file(email_data, priority, action_type, keywords)
                        self.mark_email_as_read(message['id'])

            else:
                logger.info("No unread emails found")

        except Exception as e:
            logger.error(f"Error during single check: {str(e)}")

if __name__ == "__main__":
    # For testing
    watcher = GmailWatcher()
    watcher.run_single_check()