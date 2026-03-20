#!/usr/bin/env python3
"""
WhatsApp Automation Script
Automatically monitors WhatsApp and sends messages.
"""

import os
import json
import time
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatsAppAutomation:
    """
    Automated WhatsApp monitoring and messaging.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.messages_dir = os.path.join(vault_path, "WhatsApp_Messages")
        self.session_path = os.path.join(vault_path, "whatsapp_session.json")
        self.logs_dir = os.path.join(vault_path, "Logs")
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.processed_messages = set()

        # Ensure directories exist
        for directory in [self.messages_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

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

        logger.info("Browser initialized")

    def login_to_whatsapp(self):
        """Login to WhatsApp Web."""
        try:
            self.page.goto("https://web.whatsapp.com/")
            logger.info("Navigated to WhatsApp Web")

            # Wait for WhatsApp Web to load
            logger.info("Waiting for WhatsApp Web to load...")
            time.sleep(15)  # Give page more time to load

            # Try to detect if already logged in by looking for common elements
            # This method looks for any elements that indicate the main chat window
            logged_in_indicators = [
                "[data-testid='conversation-panel-input']",
                "[data-testid='chat']",
                "._3Uu1_",  # Input area
                "div[tabindex='-1']",  # Chat list area
                "._1Eohw",  # Chat item
            ]

            # First, wait a bit to see if we can detect logged-in state
            for _ in range(10):  # Retry for up to 30 seconds
                for selector in logged_in_indicators:
                    try:
                        element = self.page.query_selector(selector)
                        if element:
                            logger.info("Already logged in to WhatsApp")
                            self.save_session()
                            return True
                    except:
                        pass
                time.sleep(3)

            # If we don't see indicators, assume we need to scan QR code
            logger.info("Please scan the QR code to login. Waiting 60 seconds...")
            time.sleep(60)

            # Check again after potential scan
            for _ in range(10):
                for selector in logged_in_indicators:
                    try:
                        element = self.page.query_selector(selector)
                        if element:
                            logger.info("Successfully logged in to WhatsApp")
                            self.save_session()
                            return True
                    except:
                        pass
                time.sleep(3)

            # If still not logged in after waiting, we'll continue anyway
            # as sometimes UI elements are hard to detect
            logger.info("Proceeding with WhatsApp (UI detection may vary)")
            self.save_session()
            return True

        except Exception as e:
            logger.error(f"Error during WhatsApp login: {e}")
            return False

    def save_session(self):
        """Save browser session for future use."""
        try:
            self.context.storage_state(path=self.session_path)
            logger.info("WhatsApp session saved")
        except Exception as e:
            logger.error(f"Could not save session: {e}")

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
            logger.error(f"Error getting unread chats: {e}")
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
                                'sender': chat_name,
                                'is_incoming': True
                            })

                except Exception as e:
                    logger.warning(f"Could not extract message: {e}")

            return recent_messages

        except Exception as e:
            logger.error(f"Error getting messages from {chat_name}: {e}")
            return []

    def send_whatsapp_message(self, contact_name, message):
        """Send a WhatsApp message to a contact."""
        try:
            # Search for contact - use multiple possible selectors
            search_box_selectors = [
                "[data-testid='search-input']",
                "[data-testid='chat-list-search']",
                "input[placeholder*='Search']",
                "._3Uu1_",  # Old class
                "._2MSJr"   # Search box class
            ]

            search_box = None
            for selector in search_box_selectors:
                try:
                    search_box = self.page.query_selector(selector)
                    if search_box:
                        break
                except:
                    continue

            if not search_box:
                logger.error("Could not find search box")
                return False

            search_box.click()
            search_box.fill(contact_name)
            time.sleep(3)

            # Try to click on the contact - multiple selector options
            contact_selectors = [
                f"[title*='{contact_name}']",
                f"[data-testid*='{contact_name}']",
                f"//span[contains(@title, '{contact_name}')]",
                f"//div[contains(@title, '{contact_name}')]",
                f"//span[contains(text(), '{contact_name}')]"
            ]

            contact = None
            for selector in contact_selectors:
                try:
                    if selector.startswith("//"):
                        contact = self.page.query_selector(f"xpath={selector}")
                    else:
                        contact = self.page.query_selector(selector)

                    if contact:
                        break
                except:
                    continue

            if not contact:
                logger.error(f"Could not find contact: {contact_name}")
                # Try again with partial match
                try:
                    # Look for any contact element and check its title
                    all_contacts = self.page.query_selector_all("span[title]")
                    for potential_contact in all_contacts:
                        title = potential_contact.get_attribute("title")
                        if title and contact_name.lower() in title.lower():
                            contact = potential_contact
                            logger.info(f"Found contact with partial match: {title}")
                            break
                except:
                    pass

            if not contact:
                logger.error(f"Could not find contact '{contact_name}' after searching")
                return False

            contact.click()
            time.sleep(3)

            # Type message - also try multiple selectors
            message_box_selectors = [
                "[data-testid='conversation-compose-box-input']",
                "[data-testid='conversation-compose-box-text-input']",
                "div[contenteditable='true'][tabindex='0']",
                "._3Uu1_",
                "._13NKt"
            ]

            message_box = None
            for selector in message_box_selectors:
                try:
                    message_box = self.page.query_selector(selector)
                    if message_box and message_box.is_enabled():
                        break
                except:
                    continue

            if not message_box:
                logger.error("Could not find message input box")
                return False

            message_box.click()
            message_box.fill(message)  # Use fill instead of type for better reliability
            time.sleep(1)

            # Send message - try multiple selectors
            send_button_selectors = [
                "[data-testid='send']",
                "[data-icon='send']",
                "button[data-testid*='send']",
                "._3y5o_"
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.page.query_selector(selector)
                    if send_button:
                        break
                except:
                    continue

            if not send_button:
                logger.error("Could not find send button")
                return False

            send_button.click()
            logger.info(f"Message sent to {contact_name}")
            return True

        except Exception as e:
            logger.error(f"Error sending message to {contact_name}: {e}")
            return False

    def process_new_message(self, message):
        """Process a new WhatsApp message."""
        # Analyze message content
        priority = self.analyze_message_priority(message)

        # Create message file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"WHATSAPP_{priority}_{timestamp}_{message['id']}.json"
        file_path = os.path.join(self.messages_dir, filename)

        # Add metadata
        message.update({
            "priority": priority,
            "processed_at": datetime.now().isoformat(),
            "suggested_actions": self.get_suggested_actions(message['text'])
        })

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(message, f, indent=2)

        logger.info(f"Processed WhatsApp message from {message['sender']}")
        return file_path

    def analyze_message_priority(self, message):
        """Analyze message priority."""
        text = message['text'].lower()

        # High priority keywords
        high_priority_keywords = [
            'urgent', 'asap', 'emergency', 'critical', 'important',
            'deadline', 'expiring', 'expires', 'help', 'assistance'
        ]

        # Medium priority keywords
        medium_priority_keywords = [
            'meeting', 'appointment', 'schedule', 'reminder',
            'invoice', 'payment', 'order', 'delivery', 'quote'
        ]

        # Check for priority keywords
        if any(keyword in text for keyword in high_priority_keywords):
            return "HIGH"
        elif any(keyword in text for keyword in medium_priority_keywords):
            return "MEDIUM"

        return "LOW"

    def get_suggested_actions(self, message_text):
        """Get suggested actions based on message content."""
        text = message_text.lower()
        actions = ["Read message", "Check sender profile"]

        if 'meeting' in text or 'schedule' in text:
            actions.append("Check calendar availability")
        elif 'invoice' in text or 'payment' in text:
            actions.append("Check payment status")
        elif 'order' in text or 'delivery' in text:
            actions.append("Check order status")
        elif 'price' in text or 'cost' in text or 'quote' in text:
            actions.append("Prepare pricing information")

        actions.append("Respond appropriately")
        return actions

    def monitor_whatsapp(self, check_interval=30):
        """Monitor WhatsApp for new messages."""
        logger.info(f"Starting WhatsApp monitoring (interval: {check_interval} seconds)")

        while True:
            try:
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
                                self.process_new_message(message)
                                self.processed_messages.add(message['id'])
                else:
                    logger.info("No unread messages found")

                logger.info(f"Check complete. Sleeping for {check_interval} seconds...")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("WhatsApp monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in WhatsApp monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retry

    def auto_reply(self, keyword, reply_message, contacts=None):
        """Auto-reply to messages containing a specific keyword."""
        # Monitor for messages
        while True:
            try:
                unread_chats = self.get_unread_chats()

                for chat in unread_chats:
                    messages = self.get_chat_messages(chat['element'], chat['name'])

                    for message in messages:
                        if (message['id'] not in self.processed_messages and
                            keyword.lower() in message['text'].lower()):

                            # Check if contact is in allowed list
                            if contacts is None or chat['name'] in contacts:
                                # Send reply
                                self.send_whatsapp_message(chat['name'], reply_message)
                                logger.info(f"Auto-replied to {chat['name']}")

                            self.processed_messages.add(message['id'])

                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in auto-reply: {e}")
                time.sleep(60)

def main():
    """Main function for standalone WhatsApp automation."""
    import argparse

    parser = argparse.ArgumentParser(description="WhatsApp Automation Tool")
    parser.add_argument("--vault", default="./", help="Vault directory path")
    parser.add_argument("--send", nargs=2, metavar=("CONTACT", "MESSAGE"), help="Send a message")
    parser.add_argument("--monitor", action="store_true", help="Monitor for new messages")
    parser.add_argument("--check", action="store_true", help="Check once for messages")
    parser.add_argument("--auto-reply", nargs=2, metavar=("KEYWORD", "REPLY"), help="Auto-reply to messages containing keyword")
    parser.add_argument("--contacts", help="File with list of allowed contacts for auto-reply")

    args = parser.parse_args()

    whatsapp = WhatsAppAutomation(vault_path=args.vault)

    # Setup browser
    whatsapp.setup_browser()

    # Login to WhatsApp
    if not whatsapp.login_to_whatsapp():
        print("Failed to login to WhatsApp")
        return 1

    if args.send:
        # Send message
        contact, message = args.send
        success = whatsapp.send_whatsapp_message(contact, message)
        if success:
            print(f"✅ Message sent to {contact}")
        else:
            print(f"[ERROR] Failed to send message to {contact}")
    elif args.monitor:
        # Monitor messages
        whatsapp.monitor_whatsapp()
    elif args.check:
        # Check once
        unread_chats = whatsapp.get_unread_chats()
        if unread_chats:
            print(f"Found {len(unread_chats)} chats with unread messages")
            for chat in unread_chats:
                print(f"- {chat['name']}: {chat['unread_count']} unread")
        else:
            print("No unread messages")
    elif args.auto_reply:
        # Auto-reply setup
        keyword, reply = args.auto_reply
        contacts = None
        if args.contacts:
            with open(args.contacts, 'r') as f:
                contacts = [line.strip() for line in f if line.strip()]
        print(f"Auto-reply setup for keyword '{keyword}'")
        print("Press Ctrl+C to stop")
        whatsapp.auto_reply(keyword, reply, contacts)
    else:
        # Default: check once
        unread_chats = whatsapp.get_unread_chats()
        if unread_chats:
            print(f"Found {len(unread_chats)} chats with unread messages")
        else:
            print("No unread messages")

    # Cleanup
    whatsapp.browser.close()
    whatsapp.playwright.stop()

if __name__ == "__main__":
    main()