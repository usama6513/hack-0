"""
LinkedIn Poster Skill for AI Employee
Automatically creates and posts business content on LinkedIn to generate sales.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkedInPoster:
    """
    Skill to automatically create and post business content on LinkedIn.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.content_dir = os.path.join(vault_path, "Content")
        self.posted_dir = os.path.join(vault_path, "Posted")
        self.driver = None

        # Ensure directories exist
        os.makedirs(self.content_dir, exist_ok=True)
        os.makedirs(self.posted_dir, exist_ok=True)

    def setup_driver(self):
        """Setup Chrome driver."""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def generate_business_content(self, topic="AI automation"):
        """Generate business-focused content for LinkedIn."""
        content_templates = [
            {
                "hook": "🚀 The future of business is here, and it's powered by AI.",
                "body": "I've been helping companies automate their workflows with AI employees. The results? 40% reduction in operational costs and 3x faster processing times.\n\nThe key is not replacing humans, but augmenting them with AI that handles repetitive tasks while your team focuses on strategy and creativity.\n\nWhat's one process in your business you'd love to automate?",
                "hashtags": "#AIAutomation #BusinessEfficiency #DigitalTransformation"
            },
            {
                "hook": "💡 Small businesses: You're sitting on a goldmine of efficiency.",
                "body": "Most small businesses I work with are drowning in manual tasks that could be automated. Email follow-ups, invoice processing, social media scheduling...\n\nHere's what happens when you implement AI automation:\n✅ Save 15+ hours per week\n✅ Reduce errors by 90%\n✅ Scale without hiring\n\nThe best part? You don't need a tech team. Modern AI tools are designed for business owners, not developers.\n\nReady to explore what's possible? Let's chat.",
                "hashtags": "#SmallBusiness #Automation #Productivity"
            },
            {
                "hook": "⚡ The 80/20 rule applies to automation too.",
                "body": "After implementing AI solutions for 50+ businesses, I've noticed a pattern:\n\n20% of automation efforts yield 80% of the results.\n\nThe key is identifying the right processes to automate:\n1. Repetitive tasks (data entry, scheduling)\n2. Rule-based decisions (invoice approvals, email sorting)\n3. High-volume, low-complexity work (report generation)\n\nStart with these, and you'll see immediate impact.\n\nWhat's your 20%?",
                "hashtags": "#Automation #BusinessStrategy #Efficiency"
            }
        ]

        # Select template based on day of week for variety
        import datetime
        template_index = datetime.datetime.now().weekday() % len(content_templates)
        return content_templates[template_index]

    def create_post_draft(self, content=None, topic=None):
        """Create a LinkedIn post draft."""
        if not content:
            content = self.generate_business_content(topic)

        post_content = f"""{content['hook']}

{content['body']}

{content['hashtags']}

#AIEmployee #BusinessAutomation #Consulting"""

        # Save draft
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_filename = f"linkedin_post_draft_{timestamp}.md"
        draft_path = os.path.join(self.content_dir, draft_filename)

        draft_metadata = f"""# LinkedIn Post Draft

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Topic:** {topic or 'Business Automation'}
**Status:** Draft

## Post Content
{post_content}

## Metrics to Track
- [ ] Views
- [ ] Likes
- [ ] Comments
- [ ] Shares
- [ ] Profile visits
- [ ] Connection requests

## Next Steps
- [ ] Review content
- [ ] Schedule post
- [ ] Monitor engagement
"""

        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(draft_metadata)

        logger.info(f"Created LinkedIn post draft: {draft_filename}")
        return draft_path, post_content

    def schedule_post(self, content, schedule_time=None):
        """Schedule a LinkedIn post for later."""
        if not schedule_time:
            schedule_time = datetime.now() + timedelta(hours=2)

        # Create scheduled file
        timestamp = schedule_time.strftime("%Y%m%d_%H%M%S")
        schedule_filename = f"linkedin_scheduled_{timestamp}.md"
        schedule_path = os.path.join(self.content_dir, schedule_filename)

        schedule_content = f"""# Scheduled LinkedIn Post

**Schedule Time:** {schedule_time.strftime('%Y-%m-%d %H:%M:%S')}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** Scheduled

## Post Content
{content}

## Automation Notes
- Post will be automatically published at scheduled time
- Metrics will be tracked and logged
- Engagement will trigger follow-up actions
"""

        with open(schedule_path, 'w', encoding='utf-8') as f:
            f.write(schedule_content)

        logger.info(f"Scheduled LinkedIn post for {schedule_time}")
        return schedule_path

    def post_to_linkedin(self, content, post_now=True):
        """Post content to LinkedIn."""
        try:
            if not self.driver:
                self.setup_driver()

            # Navigate to LinkedIn
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)

            # Click on start a post
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-share-box-open]"))
            )
            post_button.click()
            time.sleep(2)

            # Find the text area
            text_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-share-box-textarea]"))
            )

            # Clear and enter content
            text_area.clear()
            text_area.send_keys(content)

            if post_now:
                # Click post button
                post_submit = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-share-box-submit]"))
                )
                post_submit.click()
                time.sleep(3)

                logger.info("Successfully posted to LinkedIn")
                return True
            else:
                # Save as draft
                logger.info("Content prepared for LinkedIn (draft mode)")
                return True

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {str(e)}")
            return False

    def auto_generate_and_post(self, topic="business automation"):
        """Automatically generate and post content."""
        logger.info(f"Auto-generating LinkedIn content on topic: {topic}")

        # Generate content
        draft_path, content = self.create_post_draft(topic=topic)

        # Move to approval workflow
        approval_path = self.create_approval_request(content, topic)

        logger.info(f"Created approval request: {approval_path}")
        return approval_path

    def create_approval_request(self, content, topic):
        """Create approval request for LinkedIn post."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_filename = f"APPROVAL_LINKEDIN_POST_{timestamp}.md"
        approval_path = os.path.join(self.vault_path, "Needs_Action", approval_filename)

        approval_content = f"""# LinkedIn Post Approval Required

**Type:** Social Media Post
**Platform:** LinkedIn
**Topic:** {topic}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** Medium

## Post Content
{content}

## Approval Decision
- [ ] **APPROVE** - Move to /Approved folder
- [ ] **REJECT** - Move to /Rejected folder
- [ ] **MODIFY** - Edit content and re-submit

## Business Impact
This post is designed to:
- Generate leads for AI automation services
- Build thought leadership in business automation
- Drive traffic to company profile

## Safety Check
- [ ] Content is professional and appropriate
- [ ] No sensitive information disclosed
- [ ] Aligns with company messaging

## Next Steps
Once approved, the post will be automatically published to LinkedIn.
"""

        with open(approval_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        return approval_path

    def monitor_post_performance(self, post_id):
        """Monitor the performance of a LinkedIn post."""
        # This would integrate with LinkedIn API in production
        # For now, create a tracking file
        tracking_filename = f"linkedin_post_tracking_{post_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        tracking_path = os.path.join(self.vault_path, "Analytics", tracking_filename)

        # Ensure Analytics directory exists
        os.makedirs(os.path.dirname(tracking_path), exist_ok=True)

        tracking_content = f"""# LinkedIn Post Performance Tracking

**Post ID:** {post_id}
**Tracking Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Metrics to Track
- [ ] Views
- [ ] Reactions (Like, Celebrate, Support, Love, Insightful, Curious)
- [ ] Comments
- [ ] Shares
- [ ] Follows from post
- [ ] Profile visits
- [ ] Connection requests

## Engagement Analysis
- [ ] Calculate engagement rate
- [ ] Identify top commenters
- [ ] Note any lead generation

## Optimization Notes
- What worked well?
- What could be improved?
- Topic effectiveness?
- Timing analysis?
"""

        with open(tracking_path, 'w', encoding='utf-8') as f:
            f.write(tracking_content)

        logger.info(f"Created tracking file: {tracking_filename}")
        return tracking_path

    def run_automated_posting(self, interval_hours=24):
        """Run automated posting on a schedule."""
        logger.info(f"Starting automated LinkedIn posting (interval: {interval_hours} hours)")

        while True:
            try:
                # Generate and request approval for new content
                approval_path = self.auto_generate_and_post()

                logger.info(f"Created approval request: {approval_path}")
                logger.info(f"Next post scheduled in {interval_hours} hours")

                time.sleep(interval_hours * 3600)  # Convert hours to seconds

            except KeyboardInterrupt:
                logger.info("Automated posting stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in automated posting: {str(e)}")
                time.sleep(3600)  # Wait 1 hour before retry

if __name__ == "__main__":
    # For testing
    poster = LinkedInPoster()

    # Create a sample post
    draft_path, content = poster.create_post_draft(topic="business automation")
    print(f"Created draft: {draft_path}")

    # Create approval request
    approval_path = poster.create_approval_request(content, "business automation")
    print(f"Created approval request: {approval_path}")