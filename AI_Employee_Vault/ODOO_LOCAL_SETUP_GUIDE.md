# ODOO LOCAL SETUP GUIDE

## 🏗️ INSTALLATION OPTIONS

### OPTION 1: DOCKER (QUICKEST)
Run the provided script:
```bash
# Windows
odoo_local_setup.bat

# This will:
# - Download Odoo Docker image
# - Set up PostgreSQL database
# - Start Odoo server on http://localhost:8069
```

### OPTION 2: MANUAL INSTALLATION

#### Step 1: Download Odoo
1. Go to https://www.odoo.com/page/download
2. Download Odoo Community Edition for Windows
3. Run the installer and follow the wizard

#### Step 2: Install PostgreSQL
1. Odoo installer includes PostgreSQL
2. Or download from https://www.postgresql.org/
3. Make sure PostgreSQL service is running

#### Step 3: Start Odoo Server
1. Open Command Prompt as Administrator
2. Navigate to Odoo installation folder
3. Run: `odoo-bin -d aie_employee_db --db_host=localhost --db_port=5432 --db_user=odoo --db_password=odoo`

## 🚀 FIRST TIME SETUP

### Step 1: Create Your Database
1. Open browser and go to http://localhost:8069
2. You'll see the database manager
3. Click "Create Database"
4. Enter database name: `aie_employee_db`
5. Set admin password (remember this!)
6. Click "Continue"

### Step 2: Install Required Apps
After login, install these essential modules:
- **Sales**: For managing sales orders
- **Invoicing**: For creating invoices
- **CRM**: For customer management
- **Inventory**: For stock management
- **Accounting** (if available in community)

## 📊 CREATING INVOICES

### Manual Invoice Creation:
1. Go to "Invoicing" > "Customer Invoices" > "Create"
2. Select customer
3. Add products/services
4. Set quantities and prices
5. Validate the invoice

### Via AI Employee System:
Once configured, the system will automatically create invoices when you run:
```bash
python individual_scripts\create_odoo_invoice.py "Customer Name" "Product1,Product2" "Qty1,Qty2" "Price1,Price2"
```

## 🔧 CONFIGURE AI EMPLOYEE FOR ODOO

Update your `credentials.json`:
```json
{
  "odoo": {
    "url": "http://localhost:8069",
    "db": "aie_employee_db",        // Your database name
    "username": "admin",            // Default is admin
    "password": "your_admin_password" // The password you set during setup
  }
}
```

## 🏃‍♂️ RUN ODOO AUTOMATED TASKS

### Individual Invoice Creation:
```bash
# Create invoice
python individual_scripts\create_odoo_invoice.py "John Doe" "Laptop,Mouse" "1,2" "1200.00,25.50"

# Get sales report
python individual_scripts\create_odoo_invoice.py --sales 7
```

## 🔍 TROUBLESHOOTING

### Common Issues:
- **"Connection refused"**: Odoo server not running
- **"Database does not exist"**: Database name incorrect
- **"Authentication failed"**: Wrong password in credentials.json

### Check if Odoo is running:
1. Open browser
2. Go to http://localhost:8069
3. Should show Odoo login screen

### Start Odoo Manually:
```bash
# From Odoo installation directory
odoo-bin -d aie_employee_db
```

## ✅ SUCCESS CHECKLIST
- [ ] Odoo accessible at http://localhost:8069
- [ ] Database created with valid admin password
- [ ] Required apps installed
- [ ] Credentials.json updated with correct details
- [ ] Test invoice creation successful

Once Odoo is running, your AI Employee will automatically sync data, create invoices, and generate reports daily!