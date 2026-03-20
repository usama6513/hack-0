"""
WhatsApp Watcher Skill for AI Employee
Monitors WhatsApp for new messages using Playwright.
"""

import os
import time
import json
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WhatsAppWatcher:
    """
    WhatsApp watcher that monitors for new messages using Playwright.
    """

    def __init__(self, vault_path="./", session_path="whatsapp_session", check_interval=30):
        self.vault_path = vault_path
        self.session_path = session_path
        self.needs_action_dir = os.path.join(vault_path, "Needs_Action")
        self.check_interval = check_interval
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.processed_messages = set()

        # Ensure directories exist
        os.makedirs(self.needs_action_dir, exist_ok=True)
        os.makedirs(os.path.dirname(session_path), exist_ok=True)

    def setup_browser(self):
        """Setup Playwright browser for WhatsApp Web."""
        self.playwright = sync_playwright().start()

        # Launch browser
        self.browser = self.playwright.chromium.launch(
            headless=False,  # WhatsApp Web requires visible browser
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )

        # Create context with storage state
        context_options = {
            'viewport': {'width': 1280, 'height': 720},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # Load session if exists
        if os.path.exists(self.session_path):
            context_options['storage_state'] = self.session_path

        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()

        # Navigate to WhatsApp Web
        self.page.goto("https://web.whatsapp.com/")

        # Wait for QR code or chats to load
        logger.info("Waiting for WhatsApp Web to load...")

        # Check if already logged in (chats visible)
        try:
            self.page.wait_for_selector("[data-testid='chat-list']", timeout=30000)
            logger.info("WhatsApp Web loaded successfully")
            self.save_session()
            return True
        except:
            logger.info("Please scan QR code to login. Waiting 60 seconds...")
            time.sleep(60)

            # Check again
            try:
                self.page.wait_for_selector("[data-testid='chat-list']", timeout=30000)
                logger.info("Successfully logged in to WhatsApp")
                self.save_session()
                return True
            except:
                logger.error("Failed to login to WhatsApp")
                return False

    def save_session(self):
        """Save browser session for future use."""
        try:
            self.context.storage_state(path=self.session_path)
            logger.info("WhatsApp session saved")
        except Exception as e:
            logger.error(f"Could not save session: {str(e)}")

    def get_unread_chats(self):
        """Get list of chats with unread messages."""
        try:
            # Look for unread indicators
            unread_selectors = [
                "[data-testid='icon-unread-count']",
                "[aria-label*='unread']",
                ".unread-count"
            ]

            unread_chats = []

            for selector in unread_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    for element in elements:
                        # Get parent chat element
                        chat_elem = element
                        for _ in range(3):  # Go up 3 levels to find chat
                            chat_elem = chat_elem.query_selector("xpath=..")
                            if chat_elem:
                                # Get chat name
                                name_elem = chat_elem.query_selector("[data-testid='conversation-info'] span")
                                if name_elem:
                                    chat_name = name_elem.inner_text()
                                    unread_count = element.inner_text() if element else "1"
                                    unread_chats.append({
                                        'name': chat_name,
                                        'unread_count': unread_count,
                                        'element': chat_elem
                                    })
                                    break
                except:
                    continue

            return unread_chats

        except Exception as e:
            logger.error(f"Error getting unread chats: {str(e)}")
            return []

    def get_chat_messages(self, chat_elem, chat_name):
        """Get recent messages from a specific chat."""
        try:
            # Click on chat
            chat_elem.click()
            time.sleep(2)

            # Wait for messages to load
            self.page.wait_for_selector("[data-testid='message']", timeout=10000)

            # Get recent messages
            messages = self.page.query_selector_all("[data-testid='message']")
            recent_messages = []

            for message in messages[-10:]:  # Get last 10 messages
                try:
                    # Check if it's incoming (not from me)
                    incoming_selector = message.query_selector("[data-testid='msg-in']")
                    if incoming_selector:
                        # Get message text
                        text_elem = message.query_selector("[data-testid='message-text'] span")
                        if text_elem:
                            message_text = text_elem.inner_text()

                            # Get timestamp
                            time_elem = message.query_selector("[data-testid='msg-time']")
                            timestamp = time_elem.inner_text() if time_elem else ""

                            # Create unique ID
                            message_id = f"{chat_name}_{hash(message_text) % 10000}_{timestamp}"

                            recent_messages.append({
                                'id': message_id,
                                'text': message_text,
                                'timestamp': timestamp,
                                'sender': chat_name
                            })

                except Exception as e:
                    logger.warning(f"Could not extract message: {str(e)}")

            return recent_messages

        except Exception as e:
            logger.error(f"Error getting messages from {chat_name}: {str(e)}")
            return []

    def analyze_message(self, message_text, sender):
        """Analyze message to determine priority and action needed."""
        priority = "Low"
        action_type = "whatsapp_message"
        keywords = []

        # Convert to lowercase for analysis
        text_lower = message_text.lower()

        # Priority keywords
        high_priority_keywords = [
            'urgent', 'asap', 'emergency', 'critical', 'important',
            'deadline', 'expiring', 'expires', 'help'
        ]

        medium_priority_keywords = [
            'meeting', 'appointment', 'schedule', 'reminder',
            'invoice', 'payment', 'order', 'delivery'
        ]

        # Check for priority keywords
        if any(keyword in text_lower for keyword in high_priority_keywords):
            priority = "High"
        elif any(keyword in text_lower for keyword in medium_priority_keywords):
            priority = "Medium"

        # Determine action type based on content
        if 'invoice' in text_lower or 'payment' in text_lower:
            action_type = "payment_request"
            keywords.append("payment_request")
        elif 'meeting' in text_lower or 'schedule' in text_lower:
            action_type = "meeting_request"
            keywords.append("meeting_request")
        elif 'order' in text_lower or 'delivery' in text_lower:
            action_type = "order_inquiry"
            keywords.append("order_inquiry")
        elif any(word in text_lower for word in ['price', 'cost', 'quote', 'pricing']):
            action_type = "pricing_inquiry"
            keywords.append("pricing_inquiry")

        return priority, action_type, keywords

    def create_action_file(self, message, priority, action_type, keywords):
        """Create an action file for WhatsApp message."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_id = message['id']
        filename = f"WHATSAPP_{action_type.upper()}_{timestamp}_{message_id}.md"

        action_content = f"""# WhatsApp {action_type.replace('_', ' ').title()}

**Type:** {action_type}
**From:** {message['sender']}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** {priority}
**Message ID:** {message_id}

## Message Content
{message['text']}

## Keywords Detected
{', '.join(keywords) if keywords else 'None'}

## Suggested Actions
- [ ] Review message content
- [ ] Check customer/client history
- [ ] {self.get_suggested_action(action_type)}
- [ ] Respond appropriately

## Response Template
```
Hi {message['sender'].split()[0]},\n\nThank you for reaching out. I'll look into this and get back to you shortly.\n\nBest regards,\n[Your Name]
```

---
*Detected by WhatsApp Watcher*
"""

        file_path = os.path.join(self.needs_action_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(action_content)

        logger.info(f"Created action file: {filename}")
        self.processed_messages.add(message_id)

    def get_suggested_action(self, action_type):
        """Get suggested action based on message type."""
        suggestions = {
            "payment_request": "Check payment status and confirm",
            "meeting_request": "Check calendar availability",
            "order_inquiry": "Check order status and update customer",
            "pricing_inquiry": "Prepare quote or pricing information",
            "whatsapp_message": "Respond to customer inquiry"
        }
        return suggestions.get(action_type, "Respond appropriately")

    def run(self):
        """Main run loop for WhatsApp watcher."""
        logger.info("Starting WhatsApp Watcher...")

        try:
            if not self.setup_browser():
                logger.error("Failed to setup browser for WhatsApp")
                return

            logger.info("WhatsApp Watcher started successfully")

            while True:
                logger.info("Checking WhatsApp for new messages...")

                # Get unread chats
                unread_chats = self.get_unread_chats()

                if unread_chats:
                    logger.info(f"Found {len(unread_chats)} chats with unread messages")

                    for chat in unread_chats:
                        # Get messages from this chat
                        messages = self.get_chat_messages(chat['element'], chat['name'])

                        # Process each new message
                        for message in messages:
                            if message['id'] not in self.processed_messages:
                                # Analyze message
                                priority, action_type, keywords = self.analyze_message(
                                    message['text'],
                                    message['sender']
                                )

                                # Create action file
                                self.create_action_file(message, priority, action_type, keywords)

                else:
                    logger.info("No unread messages found")

                logger.info(f"Check complete. Sleeping for {self.check_interval} seconds...")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("WhatsApp Watcher stopped by user")
        except Exception as e:
            logger.error(f"Error in WhatsApp Watcher: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def run_single_check(self):
        """Run a single check (useful for testing)."""
        logger.info("Running single WhatsApp check...")

        try:
            if self.setup_browser():
                unread_chats = self.get_unread_chats()

                if unread_chats:
                    logger.info(f"Found {len(unread_chats)} chats with unread messages")

                    for chat in unread_chats:
                        messages = self.get_chat_messages(chat['element'], chat['name'])

                        for message in messages:
                            if message['id'] not in self.processed_messages:
                                priority, action_type, keywords = self.analyze_message(
                                    message['text'],
                                    message['sender']
                                )
                                self.create_action_file(message, priority, action_type, keywords)

                else:
                    logger.info("No unread messages found")

        except Exception as e:
            logger.error(f"Error during single check: {str(e)}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    # For testing
    watcher = WhatsAppWatcher()
    watcher.run_single_check()