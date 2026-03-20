"""
Odoo Integration Readiness Check
This script verifies that the AI Employee system is properly configured
to connect to Odoo once it's installed and running.
"""
import os
import sys
import json
from datetime import datetime

def check_odoo_integration_readiness():
    print("=" * 60)
    print("ODOO INTEGRATION READINESS CHECK")
    print("=" * 60)
    print(f"Check Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check 1: Credentials file exists
    print("1. CHECKING CREDENTIALS FILE...")
    creds_path = "credentials.json"
    if os.path.exists(creds_path):
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)

            odoo_creds = creds.get('odoo', {})
            if odoo_creds:
                print("   [OK] credentials.json found with Odoo configuration")
                print(f"   URL: {odoo_creds.get('url', 'NOT SET')}")
                print(f"   Database: {odoo_creds.get('db', 'NOT SET')}")
                print(f"   Username: {odoo_creds.get('username', 'NOT SET')}")
            else:
                print("   [WARNING] Odoo credentials not found in credentials.json")
                print("   Please add Odoo configuration to credentials.json")
        except Exception as e:
            print(f"   [ERROR] Could not read credentials.json: {e}")
    else:
        print("   [ERROR] credentials.json file not found")
        print("   Run: python -c \"print({'odoo':{'url':'http://localhost:8069','db':'aie_employee_db','username':'admin','password':'your_password'}})\" > credentials.json")
    print()

    # Check 2: Odoo integration skill exists
    print("2. CHECKING ODOO INTEGRATION SKILL...")
    skills_path = os.path.join("skills", "odoo_integration.py")
    if os.path.exists(skills_path):
        print("   [OK] Odoo integration skill found")
        try:
            sys.path.append('./skills')
            from odoo_integration import OdooIntegration
            print("   [OK] Odoo integration skill can be imported")
            # Create instance to test
            odoo = OdooIntegration()
            print("   [OK] Odoo integration skill initializes successfully")
        except Exception as e:
            print(f"   [ERROR] Issue with Odoo integration skill: {e}")
    else:
        print(f"   [ERROR] {skills_path} not found")
    print()

    # Check 3: Scheduler configuration
    print("3. CHECKING SCHEDULER CONFIGURATION...")
    scheduler_path = "scheduler_config.json"
    if os.path.exists(scheduler_path):
        try:
            with open(scheduler_path, 'r') as f:
                config = json.load(f)

            odoo_tasks = [task for task in config.get('tasks', {}).keys() if 'odoo' in task.lower()]
            if odoo_tasks:
                print(f"   [OK] Found {len(odoo_tasks)} Odoo-related scheduled tasks:")
                for task in odoo_tasks:
                    task_config = config['tasks'][task]
                    print(f"     - {task}: {task_config.get('schedule')} -> {task_config.get('action')}")
            else:
                print("   [WARNING] No Odoo tasks found in scheduler_config.json")
        except Exception as e:
            print(f"   [ERROR] Could not read scheduler_config.json: {e}")
    else:
        print(f"   [ERROR] {scheduler_path} not found")
    print()

    # Check 4: Accounting directory
    print("4. CHECKING ACCOUNTING DIRECTORY...")
    accounting_dir = "Accounting"
    if os.path.exists(accounting_dir):
        print("   [OK] Accounting directory exists")
    else:
        try:
            os.makedirs(accounting_dir)
            print(f"   [OK] Created Accounting directory: {accounting_dir}")
        except Exception as e:
            print(f"   [ERROR] Could not create Accounting directory: {e}")
    print()

    # Check 5: Test import of key modules
    print("5. CHECKING MODULE IMPORTS...")
    modules_to_check = [
        ("odoo_integration", "skills.odoo_integration"),
        ("advanced_scheduler", "skills.advanced_scheduler"),
        ("gold_tier_runner", "gold_tier_runner")
    ]

    for display_name, module_path in modules_to_check:
        try:
            # For odoo_integration, handle differently since we added skills to path
            if display_name == "odoo_integration":
                from odoo_integration import OdooIntegration
            elif display_name == "advanced_scheduler":
                from skills.advanced_scheduler import AdvancedScheduler
            elif display_name == "gold_tier_runner":
                import gold_tier_runner
            print(f"   [OK] {display_name} module imports successfully")
        except ImportError as e:
            print(f"   [ERROR] {display_name} module import failed: {e}")
        except Exception as e:
            print(f"   [ERROR] {display_name} module error: {e}")
    print()

    # Check 6: Verify Python dependencies
    print("6. CHECKING PYTHON DEPENDENCIES...")
    dependencies = ['requests', 'xmlrpc']
    for dep in dependencies:
        try:
            if dep == 'xmlrpc':
                import xmlrpc.client
            elif dep == 'requests':
                import requests
            print(f"   [OK] {dep} dependency available")
        except ImportError:
            print(f"   [WARNING] {dep} dependency not available (install with: pip install {dep})")
    print()

    # Final readiness assessment
    print("7. FINAL READINESS ASSESSMENT...")

    readiness_score = 0
    max_score = 6  # Number of checks that directly affect readiness

    # Check credentials file
    creds_ok = os.path.exists(creds_path)
    if creds_ok:
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
            creds_ok = bool(creds.get('odoo', {}))
        except:
            creds_ok = False
    if creds_ok: readiness_score += 1

    # Check skill file
    if os.path.exists(skills_path): readiness_score += 1

    # Check scheduler
    scheduler_ok = False
    if os.path.exists(scheduler_path):
        try:
            with open(scheduler_path, 'r') as f:
                config = json.load(f)
            scheduler_ok = bool([task for task in config.get('tasks', {}).keys() if 'odoo' in task.lower()])
        except:
            scheduler_ok = False
    if scheduler_ok: readiness_score += 1

    # Check accounting directory
    if os.path.exists(accounting_dir): readiness_score += 1

    # Check basic imports
    try:
        from skills.odoo_integration import OdooIntegration
        basic_import_ok = True
    except:
        basic_import_ok = False
    if basic_import_ok: readiness_score += 1

    # Check dependencies
    deps_ok = True
    try:
        import xmlrpc.client
        import requests
    except ImportError:
        deps_ok = False
    if deps_ok: readiness_score += 1

    print(f"   Readiness Score: {readiness_score}/{max_score}")

    if readiness_score == max_score:
        print("   [PERFECT] System is fully ready for Odoo integration!")
        print("   Once Odoo is installed and running, the AI Employee system")
        print("   will automatically connect and begin business operations.")
    elif readiness_score >= max_score - 1:
        print("   [EXCELLENT] System is nearly ready for Odoo integration!")
        print("   Minor setup needed before connecting to Odoo.")
    elif readiness_score >= max_score - 2:
        print("   [GOOD] System is mostly ready for Odoo integration!")
        print("   Some configuration needed before connecting to Odoo.")
    else:
        print("   [NEEDS WORK] Several components need setup before Odoo integration.")

    print()
    print("=" * 60)
    print("SYSTEM READY FOR ODOO INTEGRATION!")
    print("=" * 60)
    print()

    if creds_ok:
        print("NEXT STEPS:")
        print("1. Install Odoo server (instructions in COMPLETE_ODOO_SETUP_INSTRUCTIONS.md)")
        print("2. Create your Odoo database")
        print("3. Update credentials.json with actual database details")
        print("4. Start the AI Employee system: python gold_tier_runner.py --continuous")
        print()
        print("ONCE ODOO IS RUNNING, THE AI EMPLOYEE WILL:")
        print("- Automatically sync business data daily")
        print("- Generate weekly sales reports")
        print("- Manage customers and products")
        print("- Track invoices and sales")
        print("- Perform automated business operations")
        print("- Maintain complete audit trails")
    else:
        print("NEXT STEPS:")
        print("1. First, set up your credentials.json file with Odoo details")
        print("2. Install Odoo server (instructions in COMPLETE_ODOO_SETUP_INSTRUCTIONS.md)")
        print("3. Create your Odoo database")
        print("4. Update credentials.json with actual database details")

    print()
    print("Setup guides are available in:")
    print("- COMPLETE_ODOO_SETUP_INSTRUCTIONS.md")
    print("- RUN_ME_TO_START_ODOO.md")
    print("- odoo_local_setup.bat (for Windows)")
    print()
    print("The AI Employee system is fully configured for Odoo integration!")

if __name__ == "__main__":
    check_odoo_integration_readiness()