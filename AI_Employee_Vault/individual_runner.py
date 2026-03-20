"""
Individual script runner for AI Employee system
Choose which individual service to run
"""

import os
import sys
import subprocess
from datetime import datetime

def display_menu():
    print("=" * 60)
    print("AI EMPLOYEE - INDIVIDUAL SERVICE RUNNER")
    print("=" * 60)
    print("Choose a service to run individually:")
    print()
    print("1. Post to Facebook")
    print("2. Post to Instagram")
    print("3. Post to Twitter")
    print("4. Create Odoo Invoice")
    print("5. Get Odoo Sales Report")
    print("6. Run all social media posts")
    print("7. Setup Guides")
    print("8. Check system status")
    print("0. Exit")
    print()

def run_facebook_post():
    """Run individual Facebook post."""
    print("\n--- FACEBOOK POST ---")
    message = input("Enter your Facebook post message: ")
    image_url = input("Enter image URL (or press Enter to skip): ").strip()

    if image_url:
        cmd = f'python individual_scripts\\post_to_facebook.py "{message}" "{image_url}"'
    else:
        cmd = f'python individual_scripts\\post_to_facebook.py "{message}"'

    os.system(cmd)

def run_instagram_post():
    """Run individual Instagram post."""
    print("\n--- INSTAGRAM POST ---")
    caption = input("Enter your Instagram caption: ")
    image_url = input("Enter image URL for Instagram: ").strip()

    if image_url:
        cmd = f'python individual_scripts\\post_to_instagram.py "{caption}" "{image_url}"'
        os.system(cmd)
    else:
        print("ERROR: Image URL is required for Instagram posts")

def run_twitter_post():
    """Run individual Twitter post."""
    print("\n--- TWITTER POST ---")
    tweet = input("Enter your Twitter post (max 280 characters): ")
    cmd = f'python individual_scripts\\post_to_twitter.py "{tweet}"'
    os.system(cmd)

def run_odoo_invoice():
    """Run individual Odoo invoice creation."""
    print("\n--- ODOO INVOICE CREATION ---")
    customer = input("Enter customer name: ")
    products = input("Enter products (comma separated): ")
    quantities = input("Enter quantities (comma separated, same order as products): ")
    prices = input("Enter prices (comma separated, same order as products): ")

    cmd = f'python individual_scripts\\create_odoo_invoice.py "{customer}" "{products}" "{quantities}" "{prices}"'
    os.system(cmd)

def run_odoo_report():
    """Run individual Odoo sales report."""
    print("\n--- ODOO SALES REPORT ---")
    days = input("Enter number of days to report (default 7): ").strip()
    if not days:
        days = "7"

    cmd = f'python individual_scripts\\create_odoo_invoice.py --sales {days}'
    os.system(cmd)

def run_all_social():
    """Run all social media posts."""
    print("\n--- POSTING TO ALL SOCIAL MEDIA ---")

    message = input("Enter your message for all platforms: ")
    image_url = input("Enter image URL (or press Enter to skip): ").strip()

    print("\nPosting to Facebook...")
    if image_url:
        os.system(f'python individual_scripts\\post_to_facebook.py "{message}" "{image_url}"')
    else:
        os.system(f'python individual_scripts\\post_to_facebook.py "{message}"')

    if image_url:
        print("\nPosting to Instagram...")
        os.system(f'python individual_scripts\\post_to_instagram.py "{message}" "{image_url}"')

    print("\nPosting to Twitter...")
    os.system(f'python individual_scripts\\post_to_twitter.py "{message}"')

def show_setup_guides():
    """Show available setup guides."""
    print("\n--- SETUP GUIDES ---")
    print("Available guides:")
    print("1. GET_API_TOKENS_GUIDE.md - How to get real social media tokens")
    print("2. ODOO_LOCAL_SETUP_GUIDE.md - How to set up Odoo locally")
    print("3. RUN_ME_TO_START_ODOO.md - Main run instructions")
    print()

    choice = input("Enter which guide to view (1-3) or 'all' to see all: ").strip().lower()

    if choice == "1":
        with open("GET_API_TOKENS_GUIDE.md", "r") as f:
            print("\n" + f.read())
    elif choice == "2":
        with open("ODOO_LOCAL_SETUP_GUIDE.md", "r") as f:
            print("\n" + f.read())
    elif choice == "3":
        with open("RUN_ME_TO_START_ODOO.md", "r") as f:
            print("\n" + f.read())
    elif choice == "all":
        for guide in ["GET_API_TOKENS_GUIDE.md", "ODOO_LOCAL_SETUP_GUIDE.md", "RUN_ME_TO_START_ODOO.md"]:
            if os.path.exists(guide):
                print(f"\n--- CONTENTS OF {guide} ---\n")
                with open(guide, "r") as f:
                    print(f.read())
    else:
        print("Invalid choice")

def check_system_status():
    """Check system status."""
    print("\n--- SYSTEM STATUS ---")

    # Check if main files exist
    files_to_check = [
        "credentials.json",
        "individual_scripts/post_to_facebook.py",
        "individual_scripts/post_to_instagram.py",
        "individual_scripts/post_to_twitter.py",
        "individual_scripts/create_odoo_invoice.py"
    ]

    print("Files status:")
    for file in files_to_check:
        status = "[OK]" if os.path.exists(file) else "[MISSING]"
        print(f"  {status} {file}")

    # Check credentials
    if os.path.exists("credentials.json"):
        try:
            import json
            with open("credentials.json", "r") as f:
                creds = json.load(f)

            print("\nCredentials status:")
            for platform in ["facebook", "instagram", "twitter", "odoo"]:
                if platform in creds and creds[platform]:
                    print(f"  [OK] {platform} - Configured")
                else:
                    print(f"  [NEEDS CONFIG] {platform} - Not configured")
        except:
            print("  [ERROR] Cannot read credentials.json")

def main():
    while True:
        display_menu()
        choice = input("Enter your choice (0-8): ").strip()

        if choice == "1":
            run_facebook_post()
        elif choice == "2":
            run_instagram_post()
        elif choice == "3":
            run_twitter_post()
        elif choice == "4":
            run_odoo_invoice()
        elif choice == "5":
            run_odoo_report()
        elif choice == "6":
            run_all_social()
        elif choice == "7":
            show_setup_guides()
        elif choice == "8":
            check_system_status()
        elif choice == "0":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()