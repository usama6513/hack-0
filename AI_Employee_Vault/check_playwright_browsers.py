#!/usr/bin/env python3
"""Check all Playwright browser installations."""

from playwright.sync_api import sync_playwright

def check_browsers():
    """Check all Playwright browsers."""
    with sync_playwright() as p:
        print("Playwright Browser Status:")
        print("-" * 40)

        # Check Chromium
        try:
            chromium_path = p.chromium.executable_path
            print(f"Chromium: {chromium_path}")
            if chromium_path and 'chromium' in chromium_path.lower():
                print("  [OK] Chromium is installed")
            else:
                print("  [ERROR] Chromium path looks incorrect")
        except Exception as e:
            print("  [ERROR] Chromium error: {}".format(e))

        # Check Firefox
        try:
            firefox_path = p.firefox.executable_path
            print("Firefox: {}".format(firefox_path))
            if firefox_path and 'firefox' in firefox_path.lower():
                print("  [OK] Firefox is installed")
            else:
                print("  [ERROR] Firefox path looks incorrect")
        except Exception as e:
            print("  [ERROR] Firefox error: {}".format(e))

        # Check WebKit
        try:
            webkit_path = p.webkit.executable_path
            print("WebKit: {}".format(webkit_path))
            if webkit_path and 'webkit' in webkit_path.lower():
                print("  [OK] WebKit is installed")
            else:
                print("  [ERROR] WebKit path looks incorrect")
        except Exception as e:
            print("  [ERROR] WebKit error: {}".format(e))

if __name__ == "__main__":
    check_browsers()