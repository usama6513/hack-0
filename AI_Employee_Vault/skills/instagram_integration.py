"""
Instagram Integration Skill for AI Employee - Gold Tier
Integrates with Instagram for posting and content management.
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
        logging.FileHandler('instagram_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InstagramIntegration:
    """
    Skill to integrate with Instagram for posting and content management.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.instagram_dir = os.path.join(vault_path, "Instagram_Posts")
        self.social_media_dir = os.path.join(vault_path, "Social_Media")
        self.credentials_file = os.path.join(vault_path, "instagram_credentials.json")

        # Ensure directories exist
        os.makedirs(self.instagram_dir, exist_ok=True)
        os.makedirs(self.social_media_dir, exist_ok=True)

        # Load or create credentials
        self.credentials = self.load_credentials()

    def load_credentials(self) -> Dict[str, Any]:
        """Load Instagram credentials from file."""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        else:
            # Create template
            template = {
                "access_token": "",
                "user_id": "",
                "app_id": ""
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(template, f, indent=2)
            logger.info(f"[OK] Created Instagram credentials template: {self.credentials_file}")
            logger.info("Please fill in your Instagram credentials")
            return template

    def generate_content(self, topic: str) -> Dict[str, str]:
        """Generate engaging Instagram post content."""
        content = {
            "caption": f"Exploring {topic} today! Our AI Employee is working hard to bring you valuable insights. #AI #Automation #Business #Innovation",
            "hashtags": "#AI #Automation #Business #Innovation #Tech #Future #AIEmployee #DigitalTransformation"
        }
        return content

    def post_to_instagram(self, topic: str = "business automation") -> bool:
        """Post content to Instagram (simulated - would use Instagram API in production)."""
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
            post_file = os.path.join(self.instagram_dir, f"instagram_post_{timestamp}.json")

            with open(post_file, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2)

            logger.info(f"[OK] Instagram post created and saved: {post_file}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Error creating Instagram post: {e}")
            return False

    def get_post_summary(self, days: int = 7) -> Dict[str, Any]:
        """Generate summary of Instagram posts."""
        try:
            post_files = [f for f in os.listdir(self.instagram_dir) if f.startswith("instagram_post_")]
            post_count = len(post_files)

            summary = {
                "period": f"Last {days} days",
                "posts_created": post_count,
                "avg_posts_per_day": round(post_count / days, 2) if days > 0 else 0,
                "last_updated": datetime.now().isoformat()
            }

            summary_file = os.path.join(self.social_media_dir, f"instagram_summary_{datetime.now().strftime('%Y%m%d')}.json")
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"[OK] Instagram summary generated: {summary_file}")
            return summary

        except Exception as e:
            logger.error(f"[ERROR] Error generating Instagram summary: {e}")
            return {}

    def run_single_check(self):
        """Run single check for Instagram integration."""
        logger.info("Running Instagram integration check...")
        summary = self.get_post_summary()
        logger.info(f"[OK] Instagram check completed. Posts: {summary.get('posts_created', 0)}")
        return True

if __name__ == "__main__":
    # For testing
    ig = InstagramIntegration()
    success = ig.post_to_instagram("AI in business automation")
    if success:
        print("[OK] Instagram post created successfully")
    else:
        print("[ERROR] Failed to create Instagram post")