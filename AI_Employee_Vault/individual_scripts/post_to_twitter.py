"""
Individual script to post to Twitter
Usage: python post_to_twitter.py "Your tweet here"
"""
import sys
import os
import json
from datetime import datetime

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills'))

def post_to_twitter(tweet_text):
    """Post to Twitter individually."""
    try:
        from twitter_api_integration import TwitterAPIIntegration
        tw = TwitterAPIIntegration()

        # Check if credentials are configured
        if not tw.bearer_token:
            print("ERROR: Twitter credentials not configured!")
            print("Add your Twitter API credentials to credentials.json")
            return False

        # Make the tweet
        success = tw.post_tweet(tweet_text)
        if success:
            print(f"[OK] Twitter post successful: {tweet_text[:50]}...")
            return True
        else:
            print("ERROR: Twitter post failed")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def reply_to_tweet(tweet_id, reply_text):
    """Reply to a Twitter post individually."""
    try:
        from twitter_api_integration import TwitterAPIIntegration
        tw = TwitterAPIIntegration()

        if not tw.bearer_token:
            print("ERROR: Twitter credentials not configured!")
            return False

        success = tw.reply_to_tweet(tweet_id, reply_text)
        if success:
            print(f"[OK] Twitter reply successful to tweet {tweet_id}")
            return True
        else:
            print("ERROR: Twitter reply failed")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python post_to_twitter.py \"Your tweet here\" [tweet_id_for_reply]")
        print("Example: python post_to_twitter.py \"Hello Twitter!\"")
        print("Example: python post_to_twitter.py \"Thanks for sharing!\" \"1234567890123456789\"")
    else:
        tweet_text = sys.argv[1]

        if len(sys.argv) == 2:
            # Just tweet
            post_to_twitter(tweet_text)
        elif len(sys.argv) == 3:
            # Reply to tweet
            tweet_id = sys.argv[2]
            reply_to_tweet(tweet_id, tweet_text)