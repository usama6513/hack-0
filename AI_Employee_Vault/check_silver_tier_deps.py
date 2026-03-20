#!/usr/bin/env python3
"""
Check Silver Tier dependencies and system readiness.
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print("[OK] Python {}.{}.{}".format(version.major, version.minor, version.micro))
        return True
    else:
        print("[ERROR] Python {}.{}.{} (requires 3.7+)".format(version.major, version.minor, version.micro))
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name

    try:
        importlib.import_module(import_name)
        print("[OK] {}".format(package_name))
        return True
    except ImportError:
        print("[ERROR] {} - NOT INSTALLED".format(package_name))
        return False

def check_external_dependencies():
    """Check external dependencies."""
    print("\nChecking external dependencies...")

    # Check Chrome
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    ]

    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print("[OK] Chrome browser found at: {}".format(path))
            chrome_found = True
            break

    if not chrome_found:
        print("[WARNING] Chrome browser not found - LinkedIn automation may not work")
        print("   Please install Chrome or update chrome paths in the script")

    # Check credentials
    print("\nChecking credentials...")
    credentials_path = "../credentials.json"
    if os.path.exists(credentials_path):
        print("[OK] Gmail credentials found at: {}".format(credentials_path))
    else:
        print("[ERROR] Gmail credentials NOT found at: {}".format(credentials_path))
        print("   Please ensure credentials.json is in the parent directory")

def check_playwright_browsers():
    """Check if Playwright browsers are installed."""
    print("\nChecking Playwright browsers...")
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # Check Chromium
            try:
                browser = p.chromium.launch()
                browser.close()
                print("[OK] Playwright Chromium")
            except Exception as e:
                print("[ERROR] Playwright Chromium - {}".format(e))

            # Check Firefox
            try:
                browser = p.firefox.launch()
                browser.close()
                print("[OK] Playwright Firefox")
            except Exception as e:
                print("[WARNING] Playwright Firefox - {}".format(e))

            # Check WebKit
            try:
                browser = p.webkit.launch()
                browser.close()
                print("[OK] Playwright WebKit")
            except Exception as e:
                print("[WARNING] Playwright WebKit - {}".format(e))

    except ImportError:
        print("[ERROR] Playwright not installed")

def check_selenium_driver():
    """Check Selenium WebDriver."""
    print("\nChecking Selenium WebDriver...")
    try:
        from selenium import webdriver
        print("[OK] Selenium WebDriver")

        # Note: ChromeDriver will be downloaded automatically when needed
        print("   Note: ChromeDriver will be downloaded automatically when needed")

    except ImportError:
        print("[ERROR] Selenium not installed")

def main():
    """Main check function."""
    print("Silver Tier Dependency Checker")
    print("=" * 50)

    all_good = True

    # Check Python version
    if not check_python_version():
        all_good = False

    # Required packages
    print("\nChecking required packages...")
    required_packages = [
        ("selenium", "selenium"),
        ("playwright", "playwright"),
        ("google-auth", "google.auth"),
        ("google-auth-oauthlib", "google_auth_oauthlib"),
        ("google-auth-httplib2", "httplib2"),  # google-auth-httplib2 provides transport adapter
        ("google-api-python-client", "googleapiclient"),
        ("schedule", "schedule"),
        ("croniter", "croniter"),
        ("watchdog", "watchdog"),
        ("requests", "requests")
    ]

    missing_packages = []
    for package, import_name in required_packages:
        if not check_package(package, import_name):
            all_good = False
            missing_packages.append(package)

    # Check external dependencies
    check_external_dependencies()

    # Check browsers
    check_playwright_browsers()
    check_selenium_driver()

    # Summary
    print("\n" + "=" * 50)
    if all_good and not missing_packages:
        print("[OK] All Silver Tier dependencies are installed!")
        print("\nYou can now run:")
        print("  python silver_tier_runner.py --setup")
        print("  python silver_tier_runner.py --single")
    else:
        print("[ERROR] Some dependencies are missing")
        if missing_packages:
            print("\nMissing packages: {}".format(', '.join(missing_packages)))
            print("\nTo install missing packages, run:")
            print("  pip install {}".format(' '.join(missing_packages)))
        print("\nOr run the setup command:")
        print("  python silver_tier_runner.py --setup")

if __name__ == "__main__":
    main()