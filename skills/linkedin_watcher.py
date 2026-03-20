"""
LinkedIn Watcher Skill for AI Employee
Monitors LinkedIn for messages, connection requests, and content opportunities.
Creates action files for detected activities.
"""

import os
import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkedInWatcher:
    """
    LinkedIn watcher that monitors for messages, notifications, and content opportunities.
    """

    def __init__(self, vault_path="./", check_interval=300):
        self.vault_path = vault_path
        self.needs_action_dir = os.path.join(vault_path, "Needs_Action")
        self.check_interval = check_interval
        self.driver = None
        self.logged_in = False

        # Ensure directories exist
        os.makedirs(self.needs_action_dir, exist_ok=True)

    def setup_driver(self):
        """Setup Chrome driver with LinkedIn-specific options."""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Use existing Chrome profile if available
        chrome_options.add_argument("--user-data-dir=C:/Users/" + os.getenv("USERNAME") + "/AppData/Local/Google/Chrome/User Data")
        chrome_options.add_argument("--profile-directory=Default")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def login(self):
        """Login to LinkedIn (assumes saved credentials in browser)."""
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)

            # Check if already logged in
            if "feed" in self.driver.current_url:
                self.logged_in = True
                logger.info("Already logged in to LinkedIn")
                return True

            # If login page appears, wait for manual login
            logger.info("Please login to LinkedIn manually. Waiting 60 seconds...")
            time.sleep(60)

            if "feed" in self.driver.current_url:
                self.logged_in = True
                logger.info("Successfully logged in to LinkedIn")
                return True

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False

    def check_messages(self):
        """Check for new LinkedIn messages."""
        try:
            self.driver.get("https://www.linkedin.com/messaging/")
            time.sleep(3)

            # Look for unread messages
            unread_messages = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-unread-badge]")

            for message in unread_messages:
                try:
                    # Get sender name
                    sender_elem = message.find_element(By.XPATH, "../../..").find_element(By.CSS_SELECTOR, "[data-test-presence-name]")
                    sender = sender_elem.text

                    # Get message preview
                    preview_elem = message.find_element(By.XPATH, "../../..").find_element(By.CSS_SELECTOR, "[data-test-message-preview]")
                    preview = preview_elem.text

                    # Create action file
                    self.create_action_file("linkedin_message", sender, preview)

                except Exception as e:
                    logger.warning(f"Could not extract message details: {str(e)}")

        except Exception as e:
            logger.error(f"Error checking messages: {str(e)}")

    def check_notifications(self):
        """Check for LinkedIn notifications."""
        try:
            # Click on notification bell
            notification_bell = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-notification-bell]"))
            )
            notification_count = notification_bell.find_elements(By.CSS_SELECTOR, "[data-test-notification-count]")

            if notification_count:
                count = int(notification_count[0].text)
                if count > 0:
                    notification_bell.click()
                    time.sleep(2)

                    # Get notification details
                    notifications = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-notification-item]")

                    for notification in notifications[:5]:  # Process first 5
                        try:
                            notification_text = notification.text
                            self.create_action_file("linkedin_notification", "LinkedIn", notification_text)
                        except:
                            pass

        except Exception as e:
            logger.error(f"Error checking notifications: {str(e)}")

    def check_connection_requests(self):
        """Check for new connection requests."""
        try:
            # Look for connection request indicator
            my_network = self.driver.find_element(By.CSS_SELECTOR, "[data-test-global-nav-link='mynetwork']")

            # Check for pending requests badge
            badge = my_network.find_elements(By.CSS_SELECTOR, "[data-test-notification-count]")
            if badge:
                my_network.click()
                time.sleep(2)

                # Look for connection requests
                invitations = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-invitation-card]")

                for invitation in invitations[:3]:  # Process first 3
                    try:
                        name_elem = invitation.find_element(By.CSS_SELECTOR, "[data-test-invitation-name]")
                        name = name_elem.text

                        note_elem = invitation.find_element(By.CSS_SELECTOR, "[data-test-invitation-note]")
                        note = note_elem.text

                        self.create_action_file("linkedin_connection", name, note)

                    except Exception as e:
                        logger.warning(f"Could not extract invitation details: {str(e)}")

        except Exception as e:
            logger.error(f"Error checking connection requests: {str(e)}")

    def create_action_file(self, action_type, sender, content):
        """Create an action file for detected LinkedIn activity."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"LINKEDIN_{action_type.upper()}_{timestamp}.md"

        action_content = f"""# LinkedIn {action_type.replace('_', ' ').title()}

**Type:** {action_type}
**From:** {sender}
**Detected At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** Medium

## Content
{content}

## Suggested Actions
- [ ] Review and respond appropriately
- [ ] Check sender's profile for context
- [ ] Draft response if needed

---
*Auto-detected by LinkedIn Watcher*
"""

        file_path = os.path.join(self.needs_action_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(action_content)

        logger.info(f"Created action file: {filename}")

    def run(self):
        """Main run loop for the LinkedIn watcher."""
        logger.info("Starting LinkedIn Watcher...")

        try:
            self.setup_driver()

            if not self.login():
                logger.error("Failed to login to LinkedIn")
                return

            logger.info("LinkedIn Watcher started successfully")

            while True:
                logger.info("Checking LinkedIn for new activity...")

                self.check_messages()
                self.check_notifications()
                self.check_connection_requests()

                logger.info(f"Check complete. Sleeping for {self.check_interval} seconds...")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("LinkedIn Watcher stopped by user")
        except Exception as e:
            logger.error(f"Error in LinkedIn Watcher: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

    def run_single_check(self):
        """Run a single check (useful for testing)."""
        logger.info("Running single LinkedIn check...")

        try:
            self.setup_driver()

            if self.login():
                self.check_messages()
                self.check_notifications()
                self.check_connection_requests()

            logger.info("Single check completed")

        except Exception as e:
            logger.error(f"Error during single check: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    # For testing
    watcher = LinkedInWatcher()
    watcher.run_single_check()