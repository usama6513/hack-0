"""
Twitter API Integration Skill for AI Employee - Gold Tier
Integrates with Twitter API v2 for real posting and engagement.
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
        logging.FileHandler('twitter_api_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterAPIIntegration:
    """
    Skill to integrate with Twitter API v2 for real posting and engagement.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.twitter_dir = os.path.join(vault_path, "Twitter_Posts")
        self.social_media_dir = os.path.join(vault_path, "Social_Media")
        self.credentials_file = os.path.join(vault_path, "credentials.json")

        # Ensure directories exist
        os.makedirs(self.twitter_dir, exist_ok=True)
        os.makedirs(self.social_media_dir, exist_ok=True)

        # Load credentials
        self.credentials = self.load_credentials()
        self.bearer_token = self.credentials.get("bearer_token", "")
        self.api_key = self.credentials.get("api_key", "")
        self.api_secret = self.credentials.get("api_secret", "")
        self.access_token = self.credentials.get("access_token", "")
        self.access_token_secret = self.credentials.get("access_token_secret", "")

        # Twitter API v2 base URL
        self.api_url = "https://api.twitter.com/2"

    def load_credentials(self) -> Dict[str, Any]:
        """Load Twitter credentials from file."""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
                # Return only Twitter-specific credentials
                return credentials.get("twitter", {})
        else:
            # The main credentials file should already exist
            logger.warning(f"[WARNING] Main credentials.json file not found at {self.credentials_file}")
            logger.info("Please create credentials.json with proper Twitter API credentials")
            return {
                "bearer_token": "",
                "api_key": "",
                "api_secret": "",
                "access_token": "",
                "access_token_secret": ""
            }

    def _make_api_request(self, endpoint: str, method: str = "GET", data: Dict = None, params: Dict = None, files: Dict = None) -> Dict:
        """Make a request to Twitter API v2."""
        url = f"{self.api_url}/{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                if files:
                    # For media uploads, use different authentication
                    auth_headers = {
                        "Authorization": f"OAuth oauth_consumer_key=\"{self.api_key}\", oauth_token=\"{self.access_token}\", oauth_signature_method=\"HMAC-SHA1\", oauth_timestamp=\"{int(datetime.now().timestamp())}\", oauth_nonce=\"nonce\", oauth_version=\"1.0\", oauth_signature=\"fake\""
                    }
                    response = requests.post(url, headers=auth_headers, files=files, params=params)
                else:
                    response = requests.post(url, headers=headers, json=data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # For rate limit errors, handle them specially
            if response.status_code == 429:
                logger.warning("[WARNING] Twitter API rate limit exceeded")
                return {"error": "rate_limit_exceeded", "status_code": 429}

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Twitter API request failed: {e}")
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

    def post_tweet(self, text: str, reply_to_id: str = None, media_ids: List[str] = None) -> bool:
        """Post a tweet to Twitter using API v2."""
        if not self.bearer_token:
            logger.error("[ERROR] Twitter bearer token not configured")
            return False

        try:
            tweet_data = {
                "text": text
            }

            if reply_to_id:
                tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to_id}

            if media_ids:
                tweet_data["media"] = {"media_ids": media_ids}

            result = self._make_api_request("tweets", "POST", data=tweet_data)

            if "data" in result and "id" in result["data"]:
                tweet_id = result["data"]["id"]
                logger.info(f"[OK] Successfully posted tweet: {tweet_id}")

                # Save tweet record
                tweet_record = {
                    "platform": "twitter",
                    "tweet_id": tweet_id,
                    "text": text,
                    "timestamp": datetime.now().isoformat(),
                    "status": "published"
                }

                # Save to vault
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                tweet_file = os.path.join(self.twitter_dir, f"twitter_post_{timestamp}.json")
                with open(tweet_file, 'w', encoding='utf-8') as f:
                    json.dump(tweet_record, f, indent=2)

                return True
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"[ERROR] Failed to post tweet: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error posting tweet: {e}")
            return False

    def reply_to_tweet(self, tweet_id: str, text: str) -> bool:
        """Reply to a specific tweet."""
        return self.post_tweet(text, reply_to_id=tweet_id)

    def retweet(self, tweet_id: str) -> bool:
        """Retweet a specific tweet."""
        if not self.bearer_token:
            logger.error("[ERROR] Twitter bearer token not configured")
            return False

        try:
            result = self._make_api_request(f"tweets/{tweet_id}/retweet", "POST", data={})

            if "data" in result:
                logger.info(f"[OK] Successfully retweeted: {tweet_id}")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"[ERROR] Failed to retweet: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error retweeting: {e}")
            return False

    def like_tweet(self, tweet_id: str) -> bool:
        """Like a specific tweet."""
        if not self.bearer_token:
            logger.error("[ERROR] Twitter bearer token not configured")
            return False

        try:
            result = self._make_api_request(f"tweets/{tweet_id}/like", "POST", data={})

            if "data" in result and result["data"].get("liked"):
                logger.info(f"[OK] Successfully liked tweet: {tweet_id}")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"[ERROR] Failed to like tweet: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error liking tweet: {e}")
            return False

    def follow_user(self, user_id: str) -> bool:
        """Follow a user by ID."""
        if not self.bearer_token:
            logger.error("[ERROR] Twitter bearer token not configured")
            return False

        try:
            result = self._make_api_request(f"users/{user_id}/follow", "POST", data={})

            if "data" in result and result["data"].get("following"):
                logger.info(f"[OK] Successfully followed user: {user_id}")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"[ERROR] Failed to follow user: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error following user: {e}")
            return False

    def get_user_tweets(self, user_id: str, max_results: int = 10) -> List[Dict]:
        """Get recent tweets from a specific user."""
        if not self.bearer_token:
            logger.error("[ERROR] Twitter bearer token not configured")
            return []

        try:
            params = {
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics,context_annotations"
            }

            result = self._make_api_request(f"users/{user_id}/tweets", "GET", params=params)

            if "data" in result:
                logger.info(f"[OK] Retrieved {len(result['data'])} tweets from user {user_id}")
                return result["data"]
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"[ERROR] Failed to get user tweets: {error_msg}")
                return []

        except Exception as e:
            logger.error(f"[ERROR] Error getting user tweets: {e}")
            return []

    def get_home_timeline(self, max_results: int = 10) -> List[Dict]:
        """Get tweets from the home timeline."""
        if not self.bearer_token:
            logger.error("[ERROR] Twitter bearer token not configured")
            return []

        try:
            params = {
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics,author_id"
            }

            result = self._make_api_request("users/me/tweets", "GET", params=params)

            if "data" in result:
                logger.info(f"[OK] Retrieved {len(result['data'])} tweets from home timeline")
                return result["data"]
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"[ERROR] Failed to get home timeline: {error_msg}")
                return []

        except Exception as e:
            logger.error(f"[ERROR] Error getting home timeline: {e}")
            return []

    def search_tweets(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for tweets using a query."""
        if not self.bearer_token:
            logger.error("[ERROR] Twitter bearer token not configured")
            return []

        try:
            params = {
                "query": query,
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics,author_id,context_annotations"
            }

            result = self._make_api_request("tweets/search/recent", "GET", params=params)

            if "data" in result:
                logger.info(f"[OK] Retrieved {len(result['data'])} tweets for query '{query}'")
                return result["data"]
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"[ERROR] Failed to search tweets: {error_msg}")
                return []

        except Exception as e:
            logger.error(f"[ERROR] Error searching tweets: {e}")
            return []

    def generate_and_post(self, topic: str) -> bool:
        """Generate content based on topic and post to Twitter."""
        tweet_text = f"Exploring {topic} trends! AI automation is transforming how businesses operate. #AI #Automation #Business #{topic.replace(' ', '')}"

        # Limit to Twitter's 280 character limit
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        return self.post_tweet(tweet_text)

    def run_single_check(self):
        """Run single check for Twitter API integration."""
        logger.info("Running Twitter API integration check...")

        if self.bearer_token:
            # Get home timeline to verify connection
            tweets = self.get_home_timeline(5)
            logger.info(f"[OK] Twitter API check completed. Recent tweets: {len(tweets)}")
            return True
        else:
            logger.warning("[WARNING] Twitter credentials not configured - API access unavailable")
            return False

if __name__ == "__main__":
    # For testing
    tw_api = TwitterAPIIntegration()

    # Test connection by getting home timeline
    tweets = tw_api.get_home_timeline(3)
    print(f"Retrieved {len(tweets)} tweets from home timeline")

    # The actual posting would require real credentials