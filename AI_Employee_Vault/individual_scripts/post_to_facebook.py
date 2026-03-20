"""
Individual script to post to Facebook
Usage: python post_to_facebook.py "Your message here"
"""
import sys
import os
import json
from datetime import datetime

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills'))

def post_to_facebook(message, image_url=None):
    """Post to Facebook individually."""
    try:
        from facebook_api_integration import FacebookAPIIntegration
        fb = FacebookAPIIntegration()

        # Check if credentials are configured
        if not fb.access_token or not fb.page_id:
            print("ERROR: Facebook credentials not configured!")
            print("Add your Facebook Page Access Token and Page ID to credentials.json")
            return False

        # Make the post
        success = fb.post_to_facebook(message, image_url=image_url)
        if success:
            print(f"[OK] Facebook post successful: {message[:50]}...")
            return True
        else:
            print("ERROR: Facebook post failed")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def comment_on_facebook_post(post_id, comment):
    """Comment on a Facebook post individually."""
    try:
        from facebook_api_integration import FacebookAPIIntegration
        fb = FacebookAPIIntegration()

        if not fb.access_token:
            print("ERROR: Facebook access token not configured!")
            return False

        success = fb.comment_on_post(post_id, comment)
        if success:
            print(f"[OK] Facebook comment successful on post {post_id}")
            return True
        else:
            print("ERROR: Facebook comment failed")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python post_to_facebook.py \"Your message here\" [post_id_for_comment]")
        print("Example: python post_to_facebook.py \"Hello World!\"")
        print("Example: python post_to_facebook.py \"Great post!\" \"123456789_987654321\"")
    else:
        message = sys.argv[1]

        if len(sys.argv) == 2:
            # Just post
            post_to_facebook(message)
        elif len(sys.argv) == 3:
            # Comment on post
            post_id = sys.argv[2]
            comment_on_facebook_post(post_id, message)