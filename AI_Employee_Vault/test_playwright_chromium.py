#!/usr/bin/env python3
"""Test Playwright Chromium installation."""

from playwright.sync_api import sync_playwright
import sys

def test_chromium():
    """Test if Playwright Chromium is properly installed."""
    try:
        with sync_playwright() as p:
            print("Testing Playwright Chromium installation...")

            # Check if Chromium executable exists
            chromium_path = p.chromium.executable_path
            print(f"Chromium executable path: {chromium_path}")

            # Try to launch Chromium
            browser = p.chromium.launch(headless=True)
            print("Successfully launched Chromium in headless mode")

            # Create a new page
            page = browser.new_page()
            print("Successfully created new page")

            # Navigate to a test page
            page.goto('https://example.com')
            print(f"Successfully navigated to: {page.url}")
            print(f"Page title: {page.title()}")

            # Close browser
            browser.close()
            print("Successfully closed browser")

            return True

    except Exception as e:
        print(f"[ERROR] Playwright Chromium issue: {e}")
        return False

if __name__ == "__main__":
    print("Playwright Chromium Installation Test")
    print("=" * 50)

    success = test_chromium()

    print("=" * 50)
    if success:
        print("[OK] Playwright Chromium is properly installed and working!")
        sys.exit(0)
    else:
        print("[ERROR] Playwright Chromium is not working properly")
        print("\nTo fix this, try running:")
        print("  playwright install chromium")
        sys.exit(1)