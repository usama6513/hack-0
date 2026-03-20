"""
Individual script to create Odoo invoices
Usage: python create_odoo_invoice.py "Customer Name" "Product1,Product2" "Qty1,Qty2" "Price1,Price2"
"""
import sys
import os
import json
from datetime import datetime

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills'))

def create_invoice(customer_name, product_names, quantities, prices):
    """Create an invoice in Odoo individually."""
    try:
        from odoo_integration import OdooIntegration
        odoo = OdooIntegration()

        # Check if credentials are configured
        with open(os.path.join(os.path.dirname(__file__), '..', 'credentials.json'), 'r') as f:
            creds = json.load(f)
            odoo_creds = creds.get('odoo', {})

        if not odoo_creds.get('url'):
            print("ERROR: Odoo credentials not configured!")
            print("Add your Odoo connection details to credentials.json")
            return False

        # Parse the inputs
        products = [p.strip() for p in product_names.split(',')]
        qties = [int(q.strip()) for q in quantities.split(',')]
        prices_list = [float(p.strip()) for p in prices.split(',')]

        # First, check if customer exists or create new customer
        # For this example, we'll simulate by getting a customer ID (in real setup you would look up or create)
        print(f"[INFO] Processing invoice creation for customer: {customer_name}")
        print(f"[INFO] Products: {products}")
        print(f"[INFO] Quantities: {qties}")
        print(f"[INFO] Prices: {prices_list}")

        # Connect and create invoice (this requires actual Odoo running)
        try:
            models, uid, db = odoo.connect_to_odoo()
            if models:
                # Create invoice
                invoice_id = odoo.create_invoice(
                    customer_id=1,  # You would look up actual customer ID
                    product_ids=[1, 2],  # You would look up actual product IDs
                    quantities=qties,
                    amounts=prices_list
                )

                if invoice_id:
                    print(f"[OK] Invoice created successfully with ID: {invoice_id}")
                    print(f"[INFO] Invoice details saved to: {os.path.join(odoo.accounting_dir, 'odoo_invoice_*.json')}")
                    return True
                else:
                    print("ERROR: Failed to create invoice")
                    return False
            else:
                print("WARNING: Cannot connect to Odoo (this is expected if Odoo server is not running)")
                print("Please start your Odoo server first!")
                return False

        except Exception as e:
            print(f"ERROR: {e}")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def get_sales_data(days=7):
    """Get sales data from Odoo for reporting."""
    try:
        from odoo_integration import OdooIntegration
        odoo = OdooIntegration()

        with open(os.path.join(os.path.dirname(__file__), '..', 'credentials.json'), 'r') as f:
            creds = json.load(f)
            odoo_creds = creds.get('odoo', {})

        if not odoo_creds.get('url'):
            print("ERROR: Odoo credentials not configured!")
            return False

        # Connect and get sales data
        try:
            models, uid, db = odoo.connect_to_odoo()
            if models:
                sales_data = odoo.get_sales_data(days)
                if sales_data:
                    print(f"[OK] Retrieved sales data for last {days} days")
                    print(f"[INFO] Orders: {sales_data.get('order_count', 0)}")
                    print(f"[INFO] Revenue: ${sales_data.get('total_revenue', 0):.2f}")
                    print(f"[INFO] Data saved to: {os.path.join(odoo.accounting_dir, 'odoo_sales_data_*.json')}")
                    return True
                else:
                    print("ERROR: Failed to get sales data")
                    return False
            else:
                print("WARNING: Cannot connect to Odoo (this is expected if Odoo server is not running)")
                print("Please start your Odoo server first!")
                return False

        except Exception as e:
            print(f"ERROR: {e}")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("Usage: python create_odoo_invoice.py \"Customer Name\" \"Product1,Product2\" \"Qty1,Qty2\" \"Price1,Price2\"")
        print("Example: python create_odoo_invoice.py \"John Doe\" \"Laptop,Mouse\" \"1,2\" \"1200.00,25.50\"")
        print("Or: python create_odoo_invoice.py --sales 7  (to get sales data for last 7 days)")
    else:
        if sys.argv[1] == "--sales":
            days = int(sys.argv[2])
            get_sales_data(days)
        else:
            customer_name = sys.argv[1]
            product_names = sys.argv[2]
            quantities = sys.argv[3]
            prices = sys.argv[4]
            create_invoice(customer_name, product_names, quantities, prices)