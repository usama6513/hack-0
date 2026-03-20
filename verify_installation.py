#!/usr/bin/env python3
"""
Verification script for Silver Tier installation
Checks that all required packages and dependencies are properly installed.
"""

import sys
import importlib
import subprocess
import os

def check_package(package_name, display_name=None):
    """Check if a package is installed."""
    if display_name is None:
        display_name = package_name

    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"[OK] {display_name} installed (version: {version})")
        return True
    except ImportError:
        print(f"[FAIL] {display_name} not installed")
        return False

def check_external_tool(tool_name, command):
    """Check if an external tool is available."""
    try:
        result = subprocess.run([command, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            print(f"[OK] {tool_name} available ({version})")
            return True
        else:
            print(f"[WARN] {tool_name} may not be properly configured")
            return False
    except FileNotFoundError:
        print(f"[FAIL] {tool_name} not found in PATH")
        return False

def main():
    """Main verification function."""
    print("Silver Tier Installation Verification")
    print("=" * 50)
    print()

    all_good = True

    # Check Python version
    print("Python Version Check:")
    print(f"Python: {sys.version}")
    if sys.version_info >= (3, 13):
        print("[OK] Python 3.13+ detected")
    else:
        print("[WARN] Python version is below 3.13")
    print()

    # Check core packages
    print("Core Package Checks:")
    packages = [
        ("selenium", "Selenium WebDriver"),
        ("playwright", "Playwright"),
        ("google.auth", "Google Authentication"),
        ("googleapiclient", "Google API Client"),
        ("watchdog", "Watchdog File Monitor"),
        ("requests", "HTTP Requests"),
        ("datetime", "DateTime"),
        ("json", "JSON"),
        ("os", "OS Interface"),
        ("logging", "Logging"),
        ("subprocess", "Subprocess"),
        ("platform", "Platform"),
        ("time", "Time"),
        ("shutil", "Shell Utilities"),
        ("glob", "Glob"),
    ]

    for package, display_name in packages:
        if not check_package(package, display_name):
            all_good = False

    print()

    # Check optional packages
    print("Optional Package Checks:")
    optional_packages = [
        ("pandas", "Pandas Data Analysis"),
        ("beautifulsoup4", "BeautifulSoup HTML Parser"),
        ("lxml", "LXML XML Parser"),
        ("python_dotenv", "Python DotEnv"),
        ("aiohttp", "Async HTTP"),
        ("pytest", "PyTest Testing"),
        ("pyyaml", "PyYAML"),
        ("loguru", "Loguru Logging"),
    ]

    for package, display_name in optional_packages:
        check_package(package, display_name)

    print()

    # Check Playwright browsers
    print("Playwright Browser Check:")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browsers = ["chromium", "firefox", "webkit"]
            for browser in browsers:
                try:
                    browser_type = getattr(p, browser)
                    print(f"[OK] {browser.title()} browser available in Playwright")
                except:
                    print(f"[WARN] {browser.title()} browser not available")
    except Exception as e:
        print(f"[FAIL] Playwright browsers not properly installed: {e}")
        all_good = False

    print()

    # Check directory structure
    print("Directory Structure Check:")
    required_dirs = [
        "skills",
        "Inbox",
        "Needs_Action",
        "Done",
        "Drop",
        "Watched_Folder"
    ]

    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"[OK] {directory} directory exists")
        else:
            print(f"[WARN] {directory} directory missing")

    print()

    # Check for configuration files
    print("Configuration Files Check:")
    config_files = [
        ("mcp.json", "MCP Configuration"),
        ("credentials.json", "Google Credentials (placeholder)"),
    ]

    for filename, description in config_files:
        if os.path.exists(filename):
            print(f"[OK] {description} exists")
        else:
            print(f"[WARN] {description} missing")

    print()

    # Summary
    print("Installation Summary:")
    if all_good:
        print("[SUCCESS] All core Silver Tier requirements are installed!")
        print()
        print("Next steps:")
        print("1. Set up Gmail API credentials in credentials.json")
        print("2. Configure MCP servers in mcp.json")
        print("3. Test individual skills:")
        print("   python skills/vault_manager.py")
        print("   python skills/linkedin_watcher.py")
        print("   python skills/gmail_watcher.py")
        print("   python skills/whatsapp_watcher.py")
        print("   python skills/linkedin_poster.py")
        print("   python skills/plan_generator.py")
        print("   python skills/email_sender.py")
        print("   python skills/approval_workflow.py")
        print("   python skills/scheduler.py")
        print()
        print("4. Run the full system:")
        print("   python run_bronze.py")
    else:
        print("[WARNING] Some requirements are missing. Please install them before proceeding.")
        print("Run: pip install -r requirements_silver.txt")
        print("Or use: install_silver.bat (Windows) or install_silver.sh (Linux/Mac)")

if __name__ == "__main__":
    main()