"""
Facebook API Integration Skill for AI Employee - Gold Tier
Integrates with Facebook Graph API for real posting and commenting.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('facebook_api_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FacebookAPIIntegration:
    """
    Skill to integrate with Facebook Graph API for real posting and commenting.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.facebook_dir = os.path.join(vault_path, "Facebook_Posts")
        self.social_media_dir = os.path.join(vault_path, "Social_Media")
        self.credentials_file = os.path.join(vault_path, "credentials.json")

        # Ensure directories exist
        os.makedirs(self.facebook_dir, exist_ok=True)
        os.makedirs(self.social_media_dir, exist_ok=True)

        # Load credentials
        self.credentials = self.load_credentials()
        self.access_token = self.credentials.get("access_token", "")
        self.page_id = self.credentials.get("page_id", "")
        self.graph_api_url = "https://graph.facebook.com/v18.0"

    def load_credentials(self) -> Dict[str, Any]:
        """Load Facebook credentials from file."""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
                # Return only Facebook-specific credentials
                return credentials.get("facebook", {})
        else:
            # The main credentials file should already exist
            logger.warning(f"[WARNING] Main credentials.json file not found at {self.credentials_file}")
            logger.info("Please create credentials.json with proper Facebook API credentials")
            return {
                "access_token": "",
                "page_id": "",
                "app_id": "",
                "app_secret": ""
            }

    def _make_api_request(self, endpoint: str, method: str = "GET", data: Dict = None, params: Dict = None) -> Dict:
        """Make a request to Facebook Graph API."""
        url = f"{self.graph_api_url}/{endpoint}"

        if params is None:
            params = {}

        # Add access token to params
        params['access_token'] = self.access_token

        try:
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, data=data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Facebook API request failed: {e}")
            return {"error": str(e)}

    def post_to_facebook(self, message: str, link: str = None, image_url: str = None) -> bool:
        """Post content to Facebook Page using Graph API."""
        if not self.access_token or not self.page_id:
            logger.error("[ERROR] Facebook credentials not configured properly")
            return False

        try:
            # Prepare the post data
            post_data = {
                "message": message
            }

            if link:
                post_data["link"] = link
            if image_url:
                # For images, we need to make a different call
                # First upload the image
                image_params = {
                    "url": image_url,
                    "caption": message
                }
                result = self._make_api_request(f"{self.page_id}/photos", "POST", data=image_params)
            else:
                # Regular text post
                result = self._make_api_request(f"{self.page_id}/feed", "POST", data=post_data)

            if "error" not in result:
                logger.info(f"[OK] Successfully posted to Facebook: {result.get('id', 'unknown')}")

                # Save post record
                post_record = {
                    "platform": "facebook",
                    "post_id": result.get("id", "unknown"),
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "status": "published"
                }

                # Save to vault
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                post_file = os.path.join(self.facebook_dir, f"facebook_post_{timestamp}.json")
                with open(post_file, 'w', encoding='utf-8') as f:
                    json.dump(post_record, f, indent=2)

                return True
            else:
                logger.error(f"[ERROR] Failed to post to Facebook: {result['error']}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error posting to Facebook: {e}")
            return False

    def comment_on_post(self, post_id: str, comment: str) -> bool:
        """Comment on a Facebook post using Graph API."""
        if not self.access_token:
            logger.error("[ERROR] Facebook access token not configured")
            return False

        try:
            comment_data = {
                "message": comment
            }

            result = self._make_api_request(f"{post_id}/comments", "POST", data=comment_data)

            if "error" not in result:
                logger.info(f"[OK] Successfully commented on Facebook post {post_id}: {result.get('id', 'unknown')}")

                comment_record = {
                    "platform": "facebook",
                    "post_id": post_id,
                    "comment_id": result.get("id", "unknown"),
                    "comment": comment,
                    "timestamp": datetime.now().isoformat(),
                    "status": "published"
                }

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                comment_file = os.path.join(self.facebook_dir, f"facebook_comment_{timestamp}.json")
                with open(comment_file, 'w', encoding='utf-8') as f:
                    json.dump(comment_record, f, indent=2)

                return True
            else:
                logger.error(f"[ERROR] Failed to comment on Facebook post: {result['error']}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error commenting on Facebook post: {e}")
            return False

    def get_page_posts(self, limit: int = 10) -> List[Dict]:
        """Get recent posts from the Facebook Page."""
        if not self.access_token or not self.page_id:
            logger.error("[ERROR] Facebook credentials not configured properly")
            return []

        try:
            params = {
                "fields": "id,message,created_time,comments,likes,shares",
                "limit": limit
            }

            result = self._make_api_request(f"{self.page_id}/posts", "GET", params=params)

            if "data" in result:
                logger.info(f"[OK] Retrieved {len(result['data'])} posts from Facebook page")
                return result["data"]
            else:
                logger.error(f"[ERROR] Failed to get Facebook page posts: {result.get('error', 'Unknown error')}")
                return []

        except Exception as e:
            logger.error(f"[ERROR] Error getting Facebook page posts: {e}")
            return []

    def like_post(self, post_id: str) -> bool:
        """Like a Facebook post."""
        if not self.access_token:
            logger.error("[ERROR] Facebook access token not configured")
            return False

        try:
            result = self._make_api_request(f"{post_id}/likes", "POST")

            if "error" not in result:
                logger.info(f"[OK] Successfully liked Facebook post {post_id}")
                return True
            else:
                logger.error(f"[ERROR] Failed to like Facebook post: {result['error']}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error liking Facebook post: {e}")
            return False

    def generate_and_post(self, topic: str, link: str = None) -> bool:
        """Generate content based on topic and post to Facebook."""
        message = f"Exciting updates on {topic}! Check out this insightful content for business growth and innovation."

        return self.post_to_facebook(message, link)

    def run_single_check(self):
        """Run single check for Facebook API integration."""
        logger.info("Running Facebook API integration check...")

        if self.access_token and self.page_id:
            # Get recent posts to verify connection
            posts = self.get_page_posts(5)
            logger.info(f"[OK] Facebook API check completed. Recent posts: {len(posts)}")
            return True
        else:
            logger.warning("[WARNING] Facebook credentials not configured - API access unavailable")
            return False

if __name__ == "__main__":
    # For testing
    fb_api = FacebookAPIIntegration()

    # Test connection by getting page posts
    posts = fb_api.get_page_posts(3)
    print(f"Retrieved {len(posts)} posts from Facebook page")

    # The actual posting would require real credentials