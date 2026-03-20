#!/usr/bin/env python3
"""
Simple LinkedIn credential test
"""

import json

def test_credentials():
    # Load credentials
    try:
        with open('linkedin_credentials.json', 'r') as f:
            creds = json.load(f)

        print("LinkedIn Credentials Loaded:")
        print(f"Email: {creds.get('email', 'Not found')}")
        print(f"Profile URL: {creds.get('profile_url', 'Not found')}")

        if creds.get('password'):
            print("Password: [OK] Present")
        else:
            print("Password: [ERROR] Missing")

        return creds

    except FileNotFoundError:
        print("[ERROR] Error: linkedin_credentials.json file not found!")
        return None
    except json.JSONDecodeError:
        print("[ERROR] Error: Invalid JSON in linkedin_credentials.json!")
        return None

if __name__ == "__main__":
    credentials = test_credentials()
    if credentials:
        print("\n[OK] Credentials file is properly formatted")
        print("Now try logging in manually to LinkedIn with these credentials first:")
        print("1. Go to https://www.linkedin.com")
        print("2. Login with your email and password")
        print("3. Complete any security verification if needed")
        print("4. Then we can try the automation again")
    else:
        print("\n[ERROR] Please check your linkedin_credentials.json file")