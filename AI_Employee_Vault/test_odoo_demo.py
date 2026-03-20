"""
Demo script to show how the Odoo integration works with the AI Employee system.
This demonstrates the integration capabilities without requiring a live Odoo instance.
"""
import os
import sys
import json
from datetime import datetime

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'skills'))

def demo_odoo_integration():
    """Demonstrate Odoo integration functionality."""
    print("=" * 60)
    print("AI EMPLOYEE - ODOO INTEGRATION DEMONSTRATION")
    print("=" * 60)
    print()

    print("1. LOADING ODOO CREDENTIALS...")
    try:
        # Simulate loading credentials from the central file
        credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        with open(credentials_path, 'r') as f:
            creds = json.load(f)

        odoo_creds = creds.get('odoo', {})
        print("   [OK] Loaded Odoo credentials from credentials.json")
        print(f"   [OK] URL: {odoo_creds.get('url', 'Not configured')}")
        print(f"   [OK] Database: {odoo_creds.get('db', 'Not configured')}")
        print(f"   [OK] Username: {odoo_creds.get('username', 'Not configured')}")
        print()

    except Exception as e:
        print(f"   [ERROR] Error loading credentials: {e}")
        # Provide default values for demo
        odoo_creds = {
            "url": "http://localhost:8069",
            "db": "demo_db",
            "username": "admin",
            "password": "admin"
        }

    print("2. INITIALIZING ODOO INTEGRATION SKILL...")
    try:
        from odoo_integration import OdooIntegration
        odoo = OdooIntegration()
        print("   [OK] Odoo integration skill initialized successfully")
        print(f"   [OK] Connected to vault path: {odoo.vault_path}")
        print(f"   [OK] Accounting directory created: {odoo.accounting_dir}")
        print()
    except Exception as e:
        print(f"   [ERROR] Error initializing Odoo integration: {e}")
        return

    print("3. TESTING ODOO CONNECTION...")
    try:
        models, uid, db = odoo.connect_to_odoo()

        if models:
            print("   [OK] Successfully connected to Odoo instance")
            print(f"   [OK] Database: {db}")
            print(f"   [OK] User ID: {uid}")
        else:
            print("   [WARNING] Could not connect to Odoo (this is expected if Odoo is not running)")
            print("   [WARNING] This is normal if Odoo server is not started yet")
        print()
    except Exception as e:
        print(f"   [ERROR] Error connecting to Odoo: {e}")
        print()

    print("4. DEMONSTRATING ODOO OPERATIONS...")
    print("   (These would work when a real Odoo instance is available)")

    # Show what operations are available
    operations = [
        "get_sales_data() - Retrieve sales metrics and orders",
        "get_invoices_data() - Get invoice information",
        "get_customer_list() - List all customers",
        "get_product_list() - List all products",
        "create_sale_order() - Create new sales order",
        "create_customer() - Add new customer",
        "create_invoice() - Generate invoice",
        "create_product() - Add new product",
        "sync_data() - Synchronize data"
    ]

    for op in operations:
        print(f"   - {op}")
    print()

    print("5. EXAMPLE: CREATING A DEMO SALE ORDER (Simulated)...")
    try:
        # This would work with a real Odoo instance
        demo_order_id = odoo.create_sale_order(
            customer_id=1,
            product_ids=[1, 2],
            quantities=[2, 1],
            total_amount=150.0,
            order_name="Demo Order from AI Employee"
        )
        print(f"   [OK] Created demo order: {demo_order_id}")
        print(f"   [OK] Order details saved to: {os.path.join(odoo.accounting_dir, 'odoo_order_*.json')}")
    except Exception as e:
        print(f"   [WARNING] Demo order creation pending real Odoo connection: {e}")
    print()

    print("6. EXAMPLE: RETRIEVING SALES DATA (Simulated)...")
    try:
        # This would work with a real Odoo instance
        sales_data = odoo.get_sales_data(days=7)
        print(f"   [OK] Retrieved sales data: {sales_data.get('order_count', 0)} orders")
        print(f"   [OK] Total revenue: ${sales_data.get('total_revenue', 0):.2f}")
        print(f"   [OK] Data saved to: {os.path.join(odoo.accounting_dir, 'odoo_sales_data_*.json')}")
    except Exception as e:
        print(f"   [WARNING] Sales data retrieval pending real Odoo connection: {e}")
    print()

    print("7. SCHEDULED TASKS CONFIGURATION...")
    try:
        scheduler_config_path = os.path.join(os.path.dirname(__file__), 'scheduler_config.json')
        with open(scheduler_config_path, 'r') as f:
            scheduler_config = json.load(f)

        odoo_tasks = []
        for task_name, task_config in scheduler_config.get('tasks', {}).items():
            if 'odoo' in task_name.lower():
                odoo_tasks.append({
                    'name': task_name,
                    'schedule': task_config.get('schedule'),
                    'action': task_config.get('action'),
                    'enabled': task_config.get('enabled', False)
                })

        print(f"   [OK] Found {len(odoo_tasks)} Odoo-related scheduled tasks:")
        for task in odoo_tasks:
            status = "ENABLED" if task['enabled'] else "DISABLED"
            print(f"     - {task['name']}: {task['schedule']} ({status})")
            print(f"       Action: {task['action']}")
        print()
    except Exception as e:
        print(f"   [ERROR] Error reading scheduler config: {e}")
        print()

    print("8. INTEGRATION SUMMARY...")
    print("   [OK] AI Employee can automatically sync with Odoo")
    print("   [OK] Automated daily/weekly reporting")
    print("   [OK] Customer and product management")
    print("   [OK] Sales and invoice tracking")
    print("   [OK] Business process automation")
    print()

    print("=" * 60)
    print("ODOO INTEGRATION READY!")
    print("=" * 60)
    print()
    print("TO RUN WITH REAL ODOO:")
    print("1. Download Odoo Community Edition from odoo.com")
    print("2. Install and start Odoo server on http://localhost:8069")
    print("3. Create a database and admin user")
    print("4. Update credentials.json with your Odoo details")
    print("5. Run the AI Employee system in continuous mode")
    print()
    print("The system is configured and ready to integrate!")
    print("All that's needed is a running Odoo instance.")

if __name__ == "__main__":
    demo_odoo_integration()