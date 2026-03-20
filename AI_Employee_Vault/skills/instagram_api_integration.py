"""
Instagram API Integration Skill for AI Employee - Gold Tier
Integrates with Instagram Graph API for real posting and engagement.
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
        logging.FileHandler('instagram_api_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InstagramAPIIntegration:
    """
    Skill to integrate with Instagram Graph API for real posting and engagement.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.instagram_dir = os.path.join(vault_path, "Instagram_Posts")
        self.social_media_dir = os.path.join(vault_path, "Social_Media")
        self.credentials_file = os.path.join(vault_path, "credentials.json")

        # Ensure directories exist
        os.makedirs(self.instagram_dir, exist_ok=True)
        os.makedirs(self.social_media_dir, exist_ok=True)

        # Load credentials
        self.credentials = self.load_credentials()
        self.access_token = self.credentials.get("access_token", "")
        self.instagram_account_id = self.credentials.get("account_id", "")
        self.graph_api_url = "https://graph.facebook.com/v18.0"

    def load_credentials(self) -> Dict[str, Any]:
        """Load Instagram credentials from file."""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
                # Return only Instagram-specific credentials
                return credentials.get("instagram", {})
        else:
            # The main credentials file should already exist
            logger.warning(f"[WARNING] Main credentials.json file not found at {self.credentials_file}")
            logger.info("Please create credentials.json with proper Instagram API credentials")
            return {
                "access_token": "",
                "account_id": ""
            }

    def _make_api_request(self, endpoint: str, method: str = "GET", data: Dict = None, params: Dict = None) -> Dict:
        """Make a request to Instagram Graph API."""
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
            logger.error(f"[ERROR] Instagram API request failed: {e}")
            return {"error": str(e)}

    def create_media_container(self, caption: str, image_url: str, media_type: str = "IMAGE") -> str:
        """Create a media container for Instagram post."""
        if not self.access_token or not self.instagram_account_id:
            logger.error("[ERROR] Instagram credentials not configured properly")
            return None

        try:
            params = {
                "caption": caption,
                "image_url": image_url,  # For images
                "media_type": media_type
            }

            if media_type == "VIDEO":
                params["video_url"] = image_url  # For videos, use video_url

            result = self._make_api_request(f"{self.instagram_account_id}/media", "POST", data=params)

            if "id" in result:
                logger.info(f"[OK] Created media container: {result['id']}")
                return result["id"]
            else:
                logger.error(f"[ERROR] Failed to create media container: {result.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            logger.error(f"[ERROR] Error creating media container: {e}")
            return None

    def publish_media(self, container_id: str) -> bool:
        """Publish the media container to Instagram."""
        if not self.access_token:
            logger.error("[ERROR] Instagram access token not configured")
            return False

        try:
            params = {
                "creation_id": container_id
            }

            result = self._make_api_request(f"{self.instagram_account_id}/media_publish", "POST", data=params)

            if "id" in result:
                logger.info(f"[OK] Successfully published Instagram post: {result['id']}")

                # Save post record
                post_record = {
                    "platform": "instagram",
                    "post_id": result["id"],
                    "container_id": container_id,
                    "timestamp": datetime.now().isoformat(),
                    "status": "published"
                }

                # Save to vault
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                post_file = os.path.join(self.instagram_dir, f"instagram_post_{timestamp}.json")
                with open(post_file, 'w', encoding='utf-8') as f:
                    json.dump(post_record, f, indent=2)

                return True
            else:
                logger.error(f"[ERROR] Failed to publish Instagram post: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error publishing Instagram post: {e}")
            return False

    def post_to_instagram(self, caption: str, image_url: str, media_type: str = "IMAGE") -> bool:
        """Post content to Instagram using Graph API."""
        if not self.access_token or not self.instagram_account_id:
            logger.error("[ERROR] Instagram credentials not configured properly")
            return False

        # Create media container
        container_id = self.create_media_container(caption, image_url, media_type)
        if not container_id:
            return False

        # Publish the media
        return self.publish_media(container_id)

    def create_album(self, caption: str, image_urls: List[str]) -> bool:
        """Create an album (carousel) post on Instagram."""
        if not self.access_token or not self.instagram_account_id:
            logger.error("[ERROR] Instagram credentials not configured properly")
            return False

        try:
            # Create individual media containers for each image
            container_ids = []
            for image_url in image_urls:
                params = {
                    "caption": f"{caption} (Part of album)",
                    "image_url": image_url,
                    "media_type": "IMAGE"
                }

                result = self._make_api_request(f"{self.instagram_account_id}/media", "POST", data=params)

                if "id" in result:
                    container_ids.append(result["id"])
                else:
                    logger.error(f"[ERROR] Failed to create media container: {result.get('error', 'Unknown error')}")
                    return False

            # Create album container with child IDs
            album_params = {
                "caption": caption,
                "media_type": "CAROUSEL",
                "children": ",".join(container_ids)
            }

            album_result = self._make_api_request(f"{self.instagram_account_id}/media", "POST", data=album_params)

            if "id" in album_result:
                # Publish the album
                publish_params = {
                    "creation_id": album_result["id"]
                }

                final_result = self._make_api_request(f"{self.instagram_account_id}/media_publish", "POST", data=publish_params)

                if "id" in final_result:
                    logger.info(f"[OK] Successfully published Instagram album: {final_result['id']}")
                    return True
                else:
                    logger.error(f"[ERROR] Failed to publish Instagram album: {final_result.get('error', 'Unknown error')}")
                    return False
            else:
                logger.error(f"[ERROR] Failed to create Instagram album container: {album_result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error creating Instagram album: {e}")
            return False

    def comment_on_media(self, media_id: str, comment: str) -> bool:
        """Comment on an Instagram media."""
        if not self.access_token:
            logger.error("[ERROR] Instagram access token not configured")
            return False

        try:
            comment_data = {
                "message": comment
            }

            result = self._make_api_request(f"{media_id}/comments", "POST", data=comment_data)

            if "id" in result:
                logger.info(f"[OK] Successfully commented on Instagram media {media_id}: {result['id']}")

                comment_record = {
                    "platform": "instagram",
                    "media_id": media_id,
                    "comment_id": result["id"],
                    "comment": comment,
                    "timestamp": datetime.now().isoformat(),
                    "status": "published"
                }

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                comment_file = os.path.join(self.instagram_dir, f"instagram_comment_{timestamp}.json")
                with open(comment_file, 'w', encoding='utf-8') as f:
                    json.dump(comment_record, f, indent=2)

                return True
            else:
                logger.error(f"[ERROR] Failed to comment on Instagram media: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error commenting on Instagram media: {e}")
            return False

    def get_account_media(self, limit: int = 10) -> List[Dict]:
        """Get media from the Instagram account."""
        if not self.access_token or not self.instagram_account_id:
            logger.error("[ERROR] Instagram credentials not configured properly")
            return []

        try:
            params = {
                "fields": "id,caption,media_type,media_url,permalink,timestamp,comments_count,likes_count",
                "limit": limit
            }

            result = self._make_api_request(f"{self.instagram_account_id}/media", "GET", params=params)

            if "data" in result:
                logger.info(f"[OK] Retrieved {len(result['data'])} media items from Instagram account")
                return result["data"]
            else:
                logger.error(f"[ERROR] Failed to get Instagram media: {result.get('error', 'Unknown error')}")
                return []

        except Exception as e:
            logger.error(f"[ERROR] Error getting Instagram media: {e}")
            return []

    def like_media(self, media_id: str) -> bool:
        """Like an Instagram media."""
        if not self.access_token:
            logger.error("[ERROR] Instagram access token not configured")
            return False

        try:
            params = {
                "like": "true"
            }

            result = self._make_api_request(f"{media_id}/likes", "POST", params=params)

            if "success" in result and result["success"]:
                logger.info(f"[OK] Successfully liked Instagram media {media_id}")
                return True
            else:
                logger.error(f"[ERROR] Failed to like Instagram media: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error liking Instagram media: {e}")
            return False

    def generate_and_post(self, topic: str, image_url: str = None) -> bool:
        """Generate content based on topic and post to Instagram."""
        caption = f"Exciting insights on {topic}! 🚀 Follow for more business and tech updates. #business #ai #automation #tech #innovation"

        if not image_url:
            # Use a default image or generate one if needed
            image_url = "https://via.placeholder.com/1080x1080.png?text=AI+Employee+Content"

        return self.post_to_instagram(caption, image_url)

    def run_single_check(self):
        """Run single check for Instagram API integration."""
        logger.info("Running Instagram API integration check...")

        if self.access_token and self.instagram_account_id:
            # Get recent media to verify connection
            media = self.get_account_media(5)
            logger.info(f"[OK] Instagram API check completed. Recent media: {len(media)}")
            return True
        else:
            logger.warning("[WARNING] Instagram credentials not configured - API access unavailable")
            return False

if __name__ == "__main__":
    # For testing
    ig_api = InstagramAPIIntegration()

    # Test connection by getting account media
    media = ig_api.get_account_media(3)
    print(f"Retrieved {len(media)} media items from Instagram account")

    # The actual posting would require real credentials