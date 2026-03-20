"""
Twitter Integration Skill for AI Employee - Gold Tier
Integrates with Twitter (X) for posting and content management.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterIntegration:
    """
    Skill to integrate with Twitter (X) for posting and content management.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.twitter_dir = os.path.join(vault_path, "Twitter_Posts")
        self.social_media_dir = os.path.join(vault_path, "Social_Media")
        self.credentials_file = os.path.join(vault_path, "twitter_credentials.json")

        # Ensure directories exist
        os.makedirs(self.twitter_dir, exist_ok=True)
        os.makedirs(self.social_media_dir, exist_ok=True)

        # Load or create credentials
        self.credentials = self.load_credentials()

    def load_credentials(self) -> Dict[str, Any]:
        """Load Twitter credentials from file."""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        else:
            # Create template
            template = {
                "api_key": "",
                "api_secret": "",
                "access_token": "",
                "access_token_secret": "",
                "bearer_token": ""
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(template, f, indent=2)
            logger.info(f"[OK] Created Twitter credentials template: {self.credentials_file}")
            logger.info("Please fill in your Twitter credentials")
            return template

    def generate_content(self, topic: str) -> Dict[str, str]:
        """Generate engaging Twitter (X) post content."""
        # Twitter has a character limit, so we need to be concise
        content = {
            "tweet": f"Exploring {topic} today! Our AI Employee is here to help automate your business operations. #AI #Automation #Business #Innovation",
            "hashtags": "#AI #Automation #Business #Innovation #Tech #AIEmployee #DigitalTransformation"
        }
        return content

    def post_to_twitter(self, topic: str = "business automation") -> bool:
        """Post content to Twitter (X) (simulated - would use Twitter API in production)."""
        try:
            # Generate content
            content = self.generate_content(topic)

            # Create post data
            post_data = {
                "content": content,
                "topic": topic,
                "posted_at": datetime.now().isoformat(),
                "status": "simulated_success"  # In production, this would be actual API response
            }

            # Save post to vault
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            post_file = os.path.join(self.twitter_dir, f"twitter_post_{timestamp}.json")

            with open(post_file, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2)

            logger.info(f"[OK] Twitter post created and saved: {post_file}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Error creating Twitter post: {e}")
            return False

    def get_post_summary(self, days: int = 7) -> Dict[str, Any]:
        """Generate summary of Twitter posts."""
        try:
            post_files = [f for f in os.listdir(self.twitter_dir) if f.startswith("twitter_post_")]
            post_count = len(post_files)

            summary = {
                "period": f"Last {days} days",
                "posts_created": post_count,
                "avg_posts_per_day": round(post_count / days, 2) if days > 0 else 0,
                "last_updated": datetime.now().isoformat()
            }

            summary_file = os.path.join(self.social_media_dir, f"twitter_summary_{datetime.now().strftime('%Y%m%d')}.json")
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"[OK] Twitter summary generated: {summary_file}")
            return summary

        except Exception as e:
            logger.error(f"[ERROR] Error generating Twitter summary: {e}")
            return {}

    def run_single_check(self):
        """Run single check for Twitter integration."""
        logger.info("Running Twitter integration check...")
        summary = self.get_post_summary()
        logger.info(f"[OK] Twitter check completed. Posts: {summary.get('posts_created', 0)}")
        return True

if __name__ == "__main__":
    # For testing
    tw = TwitterIntegration()
    success = tw.post_to_twitter("AI in business automation")
    if success:
        print("[OK] Twitter post created successfully")
    else:
        print("[ERROR] Failed to create Twitter post")