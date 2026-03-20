# COMPLETE ODOO SETUP GUIDE FOR AI EMPLOYEE SYSTEM

This guide will help you set up Odoo and connect it to your AI Employee system for full automation.

## OPTION 1: DOCKER SETUP (Recommended)

### For Windows (using the provided batch file):
1. Run the `odoo_local_setup.bat` file
2. Follow the automated setup process
3. Open your browser and go to http://localhost:8069

### For Linux/Mac:
1. Run the `odoo_local_setup.sh` script
2. Follow the automated setup process
3. Open your browser and go to http://localhost:8069

## OPTION 2: MANUAL INSTALLATION

### Step 1: Download Odoo
1. Go to https://www.odoo.com/page/download
2. Download Odoo Community Edition for your operating system
3. Follow the installation wizard

### Step 2: Install Python Dependencies
```bash
pip install psycopg2-binary
```

### Step 3: Start PostgreSQL Database
1. Make sure PostgreSQL is installed (usually comes with Odoo installer)
2. Start the PostgreSQL service

### Step 4: Run Odoo Server
1. Open Command Prompt/Terminal as Administrator
2. Navigate to Odoo installation directory
3. Run: `odoo-bin -d aie_employee_db --db_host=localhost --db_port=5432 --db_user=odoo --db_password=odoo`

## STEP 3: INITIAL ODOO CONFIGURATION

### Create Your Database:
1. Open browser and go to http://localhost:8069
2. You'll see the database creation screen
3. Click "Manage Databases"
4. Enter "aie_employee_db" as the database name
5. Set your admin password (remember this for credentials.json)
6. Click "Create Database"

### Install Required Apps:
After database creation, install these essential modules:
- Sales
- Invoicing
- CRM
- Inventory
- Accounting (if available in community)
- Purchase
- Project

## STEP 4: CONFIGURE AI EMPLOYEE SYSTEM

### Update credentials.json:
```json
{
  "odoo": {
    "url": "http://localhost:8069",
    "db": "aie_employee_db",
    "username": "admin",
    "password": "your_admin_password_here"
  }
}
```

## STEP 5: TEST INTEGRATION

### Run the AI Employee system:
```bash
cd D:\hack0-bronze\AI_Employee_Vault
python gold_tier_runner.py --single
```

### Verify Odoo integration:
1. Check that the system can connect to Odoo
2. Verify that sales data can be retrieved
3. Verify that invoices can be pulled
4. Check that customer and product lists work

## STEP 6: RUN CONTINUOUSLY

### Start the system in continuous mode:
```bash
python gold_tier_runner.py --continuous
```

## TROUBLESHOOTING

### If Odoo doesn't start:
- Check that port 8069 is not in use
- Ensure PostgreSQL service is running
- Verify database credentials

### If AI system can't connect to Odoo:
- Verify Odoo is running at http://localhost:8069
- Check credentials in credentials.json
- Ensure database name is correct
- Verify admin password

### Common Error Solutions:
- **"Connection refused"**: Odoo server is not running
- **"Database does not exist"**: Database name is incorrect
- **"Authentication failed"**: Check username/password in credentials.json

## SUCCESS INDICATORS

When properly configured, you'll see:
- ✅ Successful Odoo connection messages
- ✅ Sales data retrieval
- ✅ Invoice data retrieval
- ✅ Customer and product lists
- ✅ Automated daily syncs
- ✅ Weekly business reports in ./Accounting/ directory

## AUTOMATED FEATURES

Once connected, the system will:
- Automatically sync with Odoo daily at 6 AM
- Generate weekly reports every Monday
- Track sales and invoices automatically
- Maintain customer and product data
- Schedule automatic business operations
- Provide complete audit trails

## SECURITY NOTES

- Store credentials.json securely
- Use strong passwords for Odoo admin
- Regularly backup your Odoo database
- Monitor system logs for unusual activity

---

Your Odoo server will be ready for full integration with the AI Employee system once you complete these steps. The system will then automatically perform business operations as requested!