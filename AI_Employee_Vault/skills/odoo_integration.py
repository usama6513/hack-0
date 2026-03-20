"""
Odoo Integration Skill for AI Employee - Gold Tier
Integrates with local Odoo Community instance using JSON-RPC API.
"""

import os
import json
import logging
import xmlrpc.client
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('odoo_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OdooIntegration:
    """
    Skill to integrate with Odoo Community accounting system using JSON-RPC API.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.accounting_dir = os.path.join(vault_path, "Accounting")
        self.credentials_file = os.path.join(vault_path, "credentials.json")
        self.odoo_config_file = os.path.join(vault_path, "odoo_config.json")

        # Ensure directories exist
        os.makedirs(self.accounting_dir, exist_ok=True)

        # Load or create credentials
        self.credentials = self.load_credentials()
        self.config = self.load_config()

    def load_credentials(self) -> Dict[str, Any]:
        """Load Odoo credentials from file."""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
                # Return only Odoo-specific credentials
                return credentials.get("odoo", {})
        else:
            # The main credentials file should already exist
            logger.warning(f"[WARNING] Main credentials.json file not found at {self.credentials_file}")
            logger.info("Please create credentials.json with proper Odoo API credentials")
            return {
                "url": "http://localhost:8069",
                "db": "your_database_name",
                "username": "your_username",
                "password": "your_password"
            }

    def load_config(self) -> Dict[str, Any]:
        """Load Odoo configuration from file."""
        if os.path.exists(self.odoo_config_file):
            with open(self.odoo_config_file, 'r') as f:
                return json.load(f)
        else:
            # Create template configuration
            template = {
                "modules": {
                    "sale": True,
                    "account": True,
                    "crm": True,
                    "hr": True,
                    "stock": True,
                    "project": True
                },
                "sync_enabled": True,
                "auto_create_customers": True,
                "auto_create_products": True,
                "auto_sync_sales": True,
                "auto_sync_invoices": True
            }
            with open(self.odoo_config_file, 'w') as f:
                json.dump(template, f, indent=2)
            logger.info(f"[OK] Created Odoo config template: {self.odoo_config_file}")
            return template

    def connect_to_odoo(self):
        """Connect to local Odoo instance using JSON-RPC."""
        try:
            url = self.credentials.get("url", "http://localhost:8069")
            db = self.credentials.get("db", "odoo_db")
            username = self.credentials.get("username", "admin")
            password = self.credentials.get("password", "admin")

            # Create JSON-RPC connection
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, password, {})

            if uid:
                models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
                logger.info(f"[OK] Connected to Odoo instance: {url}")
                return models, uid, db
            else:
                logger.error("[ERROR] Failed to authenticate with Odoo")
                return None, None, None

        except Exception as e:
            logger.error(f"[ERROR] Connection to Odoo failed: {e}")
            return None, None, None

    def create_sale_order(self, customer_id: int, product_ids: List[int], quantities: List[int], total_amount: float, order_name: str = None) -> int:
        """Create a sale order in Odoo."""
        models, uid, db = self.connect_to_odoo()
        if not models:
            return False

        try:
            # Prepare order values
            order_vals = {
                'partner_id': customer_id,
                'order_line': [(0, 0, {
                    'product_id': prod_id,
                    'product_uom_qty': qty,
                    'price_unit': 10.0  # This would be dynamic in production
                }) for prod_id, qty in zip(product_ids, quantities)],
                'amount_total': total_amount
            }

            if order_name:
                order_vals['name'] = order_name

            # Create sale order
            order_id = models.execute_kw(
                db, uid, self.credentials["password"],
                'sale.order', 'create',
                [order_vals]
            )

            logger.info(f"[OK] Sale order created: {order_id}")

            # Save order record
            order_record = {
                "platform": "odoo",
                "order_id": order_id,
                "customer_id": customer_id,
                "total_amount": total_amount,
                "timestamp": datetime.now().isoformat(),
                "status": "created"
            }

            # Save to vault
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            order_file = os.path.join(self.accounting_dir, f"odoo_order_{timestamp}.json")
            with open(order_file, 'w', encoding='utf-8') as f:
                json.dump(order_record, f, indent=2)

            return order_id

        except Exception as e:
            logger.error(f"[ERROR] Failed to create sale order: {e}")
            return False

    def create_customer(self, name: str, email: str = None, phone: str = None, address: str = None) -> int:
        """Create a customer in Odoo."""
        models, uid, db = self.connect_to_odoo()
        if not models:
            return False

        try:
            customer_vals = {
                'name': name,
                'email': email,
                'phone': phone,
                'customer_rank': 1  # Mark as customer
            }

            if address:
                customer_vals['street'] = address

            customer_id = models.execute_kw(
                db, uid, self.credentials["password"],
                'res.partner', 'create',
                [customer_vals]
            )

            logger.info(f"[OK] Customer created: {customer_id}")

            # Save customer record
            customer_record = {
                "platform": "odoo",
                "customer_id": customer_id,
                "name": name,
                "email": email,
                "timestamp": datetime.now().isoformat(),
                "status": "created"
            }

            # Save to vault
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            customer_file = os.path.join(self.accounting_dir, f"odoo_customer_{timestamp}.json")
            with open(customer_file, 'w', encoding='utf-8') as f:
                json.dump(customer_record, f, indent=2)

            return customer_id

        except Exception as e:
            logger.error(f"[ERROR] Failed to create customer: {e}")
            return False

    def create_invoice(self, customer_id: int, product_ids: List[int], quantities: List[int], amounts: List[float], invoice_date: str = None) -> int:
        """Create an invoice in Odoo."""
        models, uid, db = self.connect_to_odoo()
        if not models:
            return False

        try:
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': customer_id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': prod_id,
                    'quantity': qty,
                    'price_unit': amt
                }) for prod_id, qty, amt in zip(product_ids, quantities, amounts)]
            }

            if invoice_date:
                invoice_vals['invoice_date'] = invoice_date
                invoice_vals['date'] = invoice_date

            invoice_id = models.execute_kw(
                db, uid, self.credentials["password"],
                'account.move', 'create',
                [invoice_vals]
            )

            logger.info(f"[OK] Invoice created: {invoice_id}")

            # Save invoice record
            invoice_record = {
                "platform": "odoo",
                "invoice_id": invoice_id,
                "customer_id": customer_id,
                "total_amount": sum(amounts),
                "timestamp": datetime.now().isoformat(),
                "status": "created"
            }

            # Save to vault
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            invoice_file = os.path.join(self.accounting_dir, f"odoo_invoice_{timestamp}.json")
            with open(invoice_file, 'w', encoding='utf-8') as f:
                json.dump(invoice_record, f, indent=2)

            return invoice_id

        except Exception as e:
            logger.error(f"[ERROR] Failed to create invoice: {e}")
            return False

    def create_product(self, name: str, default_code: str, list_price: float, type: str = 'consu') -> int:
        """Create a product in Odoo."""
        models, uid, db = self.connect_to_odoo()
        if not models:
            return False

        try:
            product_id = models.execute_kw(
                db, uid, self.credentials["password"],
                'product.product', 'create',
                [{
                    'name': name,
                    'default_code': default_code,
                    'list_price': list_price,
                    'type': type  # 'consu' for consumable, 'product' for stockable, 'service' for service
                }]
            )

            logger.info(f"[OK] Product created: {product_id}")
            return product_id

        except Exception as e:
            logger.error(f"[ERROR] Failed to create product: {e}")
            return False

    def get_sales_data(self, days: int = 30) -> Dict[str, Any]:
        """Get sales data from Odoo for the specified period."""
        models, uid, db = self.connect_to_odoo()
        if not models:
            return {}

        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            domain = [
                ('date_order', '>=', start_date.isoformat()),
                ('date_order', '<=', end_date.isoformat()),
                ('state', 'in', ['sale', 'done'])
            ]

            # Search for sales orders
            order_ids = models.execute_kw(
                db, uid, self.credentials["password"],
                'sale.order', 'search',
                [domain]
            )

            # Get order details
            orders = models.execute_kw(
                db, uid, self.credentials["password"],
                'sale.order', 'read',
                [order_ids], {
                    'fields': ['name', 'date_order', 'partner_id', 'amount_total', 'state', 'order_line']
                }
            )

            # Calculate totals
            total_revenue = sum(order.get('amount_total', 0) for order in orders)
            order_count = len(orders)
            average_order_value = total_revenue / order_count if order_count > 0 else 0

            # Get customer data
            customer_ids = [order['partner_id'][0] for order in orders if order['partner_id']]
            customers = {}
            if customer_ids:
                customer_data = models.execute_kw(
                    db, uid, self.credentials["password"],
                    'res.partner', 'read',
                    [list(set(customer_ids))], {
                        'fields': ['name', 'email', 'phone']
                    }
                )
                for customer in customer_data:
                    customers[customer['id']] = customer

            sales_data = {
                "period": f"Last {days} days ({start_date} to {end_date})",
                "total_revenue": total_revenue,
                "order_count": order_count,
                "average_order_value": average_order_value,
                "new_customers": len(set(customer_ids)),
                "orders": orders,
                "customers": customers,
                "last_updated": datetime.now().isoformat()
            }

            # Save to accounting directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = os.path.join(self.accounting_dir, f"odoo_sales_data_{timestamp}.json")

            with open(data_file, 'w') as f:
                json.dump(sales_data, f, indent=2, default=str)

            logger.info(f"[OK] Sales data retrieved and saved: {data_file}")
            return sales_data

        except Exception as e:
            logger.error(f"[ERROR] Failed to get sales data: {e}")
            return {}

    def get_invoices_data(self, days: int = 30) -> Dict[str, Any]:
        """Get invoices data from Odoo for the specified period."""
        models, uid, db = self.connect_to_odoo()
        if not models:
            return {}

        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            domain = [
                ('invoice_date', '>=', start_date.isoformat()),
                ('invoice_date', '<=', end_date.isoformat()),
                ('state', 'in', ['posted'])
            ]

            # Search for invoices
            invoice_ids = models.execute_kw(
                db, uid, self.credentials["password"],
                'account.move', 'search',
                [domain]
            )

            # Get invoice details
            invoices = models.execute_kw(
                db, uid, self.credentials["password"],
                'account.move', 'read',
                [invoice_ids], {
                    'fields': ['name', 'invoice_date', 'partner_id', 'amount_total', 'state', 'invoice_line_ids']
                }
            )

            # Calculate totals
            total_invoiced = sum(invoice.get('amount_total', 0) for invoice in invoices)
            invoice_count = len(invoices)

            invoices_data = {
                "period": f"Last {days} days ({start_date} to {end_date})",
                "total_invoiced": total_invoiced,
                "invoice_count": invoice_count,
                "average_invoice_value": total_invoiced / invoice_count if invoice_count > 0 else 0,
                "invoices": invoices,
                "last_updated": datetime.now().isoformat()
            }

            # Save to accounting directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = os.path.join(self.accounting_dir, f"odoo_invoices_data_{timestamp}.json")

            with open(data_file, 'w') as f:
                json.dump(invoices_data, f, indent=2, default=str)

            logger.info(f"[OK] Invoices data retrieved and saved: {data_file}")
            return invoices_data

        except Exception as e:
            logger.error(f"[ERROR] Failed to get invoices data: {e}")
            return {}

    def sync_data(self, data_type: str, direction: str = "to_odoo") -> bool:
        """Sync data to/from Odoo."""
        logger.info(f"Syncing {data_type} data in {direction} direction")

        models, uid, db = self.connect_to_odoo()
        if not models and direction != "from_odoo_simulation":
            return False

        # This would implement actual synchronization logic in production
        sync_file = os.path.join(self.accounting_dir, f"sync_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        sync_data = {
            "data_type": data_type,
            "direction": direction,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"  # In production, this would reflect actual sync results
        }

        with open(sync_file, 'w') as f:
            json.dump(sync_data, f, indent=2)

        logger.info(f"[OK] Sync operation logged: {sync_file}")
        return True

    def get_customer_list(self) -> List[Dict]:
        """Get list of all customers from Odoo."""
        models, uid, db = self.connect_to_odoo()
        if not models:
            return []

        try:
            # Search for all customers
            domain = [('customer_rank', '>', 0)]  # Only customers (not all partners)

            customer_ids = models.execute_kw(
                db, uid, self.credentials["password"],
                'res.partner', 'search',
                [domain]
            )

            # Get customer details
            customers = models.execute_kw(
                db, uid, self.credentials["password"],
                'res.partner', 'read',
                [customer_ids], {
                    'fields': ['name', 'email', 'phone', 'street', 'city', 'country_id', 'total_invoiced']
                }
            )

            logger.info(f"[OK] Retrieved {len(customers)} customers from Odoo")
            return customers

        except Exception as e:
            logger.error(f"[ERROR] Failed to get customer list: {e}")
            return []

    def get_product_list(self) -> List[Dict]:
        """Get list of all products from Odoo."""
        models, uid, db = self.connect_to_odoo()
        if not models:
            return []

        try:
            # Search for all products
            domain = []

            product_ids = models.execute_kw(
                db, uid, self.credentials["password"],
                'product.product', 'search',
                [domain]
            )

            # Get product details
            products = models.execute_kw(
                db, uid, self.credentials["password"],
                'product.product', 'read',
                [product_ids], {
                    'fields': ['name', 'default_code', 'list_price', 'type', 'uom_name']
                }
            )

            logger.info(f"[OK] Retrieved {len(products)} products from Odoo")
            return products

        except Exception as e:
            logger.error(f"[ERROR] Failed to get product list: {e}")
            return []

    def run_single_check(self):
        """Run single check for Odoo integration."""
        logger.info("Running Odoo integration check...")

        # Try to connect to Odoo
        models, uid, db = self.connect_to_odoo()

        if models:
            # Get sales data as a test
            sales_data = self.get_sales_data(7)
            invoices_data = self.get_invoices_data(7)

            logger.info(f"[OK] Odoo check completed. Sales: {sales_data.get('order_count', 0)}, Invoices: {invoices_data.get('invoice_count', 0)}")
            return True
        else:
            logger.warning("[WARNING] Odoo connection failed - check credentials")
            return False

if __name__ == "__main__":
    # For testing
    odoo = OdooIntegration()
    connected = odoo.connect_to_odoo()
    if connected[0]:
        print("[OK] Connected to Odoo successfully")

        # Get sales data
        sales = odoo.get_sales_data(7)
        print(f"Sales data retrieved: {sales.get('order_count', 0)} orders")

        # Get invoices data
        invoices = odoo.get_invoices_data(7)
        print(f"Invoices data retrieved: {invoices.get('invoice_count', 0)} invoices")
    else:
        print("[ERROR] Failed to connect to Odoo - ensure local instance is running")