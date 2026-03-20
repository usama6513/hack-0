"""
Individual script to post to Instagram
Usage: python post_to_instagram.py "Your caption here" "image_url"
"""
import sys
import os
import json
from datetime import datetime

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills'))

def post_to_instagram(caption, image_url):
    """Post to Instagram individually."""
    try:
        from instagram_api_integration import InstagramAPIIntegration
        ig = InstagramAPIIntegration()

        # Check if credentials are configured
        if not ig.access_token or not ig.instagram_account_id:
            print("ERROR: Instagram credentials not configured!")
            print("Add your Instagram Access Token and Account ID to credentials.json")
            return False

        # Make the post
        success = ig.post_to_instagram(caption, image_url)
        if success:
            print(f"[OK] Instagram post successful: {caption[:50]}...")
            return True
        else:
            print("ERROR: Instagram post failed")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def comment_on_instagram_media(media_id, comment):
    """Comment on an Instagram media individually."""
    try:
        from instagram_api_integration import InstagramAPIIntegration
        ig = InstagramAPIIntegration()

        if not ig.access_token:
            print("ERROR: Instagram access token not configured!")
            return False

        success = ig.comment_on_media(media_id, comment)
        if success:
            print(f"[OK] Instagram comment successful on media {media_id}")
            return True
        else:
            print("ERROR: Instagram comment failed")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python post_to_instagram.py \"Your caption\" \"image_url\"")
        print("Example: python post_to_instagram.py \"Amazing day!\" \"https://example.com/image.jpg\"")
        print("Example: python post_to_instagram.py \"Nice!\" \"comment\" \"media_id\"")
    else:
        if sys.argv[2] == "comment":
            # Comment on media
            media_id = sys.argv[3]
            comment = sys.argv[1]
            comment_on_instagram_media(media_id, comment)
        else:
            # Post to Instagram
            caption = sys.argv[1]
            image_url = sys.argv[2]
            post_to_instagram(caption, image_url)