# How to Run the AI Employee System with Odoo Integration

This guide will show you how to set up and run the complete AI Employee system with Odoo integration.

## Step 1: Install Required Dependencies

```bash
# Install required Python packages
pip install requests schedule xmlrpc
```

## Step 2: Download and Install Odoo

### Option A: Download from Official Website (Recommended)
1. Go to https://www.odoo.com/page/download
2. Download Odoo Community Edition
3. Install it on your system

### Option B: Install via Docker (Alternative)
```bash
# Pull the latest Odoo image
docker pull odoo:18.0

# Run Odoo container
docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres --name db postgres:13
docker run -p 8069:8069 --name odoo --link db:db -t odoo:18.0
```

## Step 3: Configure Your Odoo Instance

1. Start your Odoo server (default runs on http://localhost:8069)
2. Create a new database with admin user
3. Install required apps:
   - Sales
   - Invoicing
   - CRM
   - Inventory
   - Accounting (if available in community)

## Step 4: Update Credentials

Update the `credentials.json` file with your actual Odoo details:

```json
{
  "odoo": {
    "url": "http://localhost:8069",
    "db": "your_actual_database_name",
    "username": "your_username",
    "password": "your_password"
  }
}
```

## Step 5: Configure Social Media API Credentials (Optional but Recommended)

Update the same `credentials.json` file with your social media API credentials:

```json
{
  "facebook": {
    "access_token": "your_facebook_page_access_token",
    "page_id": "your_facebook_page_id",
    "app_id": "your_facebook_app_id",
    "app_secret": "your_facebook_app_secret",
    "api_version": "v18.0"
  },
  "instagram": {
    "access_token": "your_instagram_access_token",
    "account_id": "your_instagram_business_account_id",
    "app_id": "your_instagram_app_id",
    "app_secret": "your_instagram_app_secret",
    "api_version": "v18.0"
  },
  "twitter": {
    "bearer_token": "your_twitter_bearer_token",
    "api_key": "your_twitter_api_key",
    "api_secret": "your_twitter_api_secret",
    "access_token": "your_twitter_access_token",
    "access_token_secret": "your_twitter_access_token_secret",
    "api_version": "2"
  },
  "odoo": {
    "url": "http://localhost:8069",
    "db": "your_actual_database_name",
    "username": "your_username",
    "password": "your_password"
  }
}
```

## Step 6: Run the AI Employee System

### Option 1: Run in Single Check Mode
```bash
cd D:\hack0-bronze\AI_Employee_Vault
python gold_tier_runner.py --single
```

### Option 2: Run in Continuous Mode (Recommended)
```bash
cd D:\hack0-bronze\AI_Employee_Vault
python gold_tier_runner.py --continuous
```

### Option 3: Run Tests First
```bash
cd D:\hack0-bronze\AI_Employee_Vault
python test_gold_tier_enhanced.py
```

## Step 7: Monitor the Results

The system will create various directories and files:

- `./Accounting/` - All Odoo-related data
- `./Social_Media/` - All social media posts
- `./Facebook_Posts/` - Facebook-specific posts
- `./Instagram_Posts/` - Instagram-specific posts
- `./Twitter_Posts/` - Twitter-specific posts
- `./CEO_Briefings/` - Executive reports
- `./Business_Audits/` - Business analysis reports
- `./Error_Logs/` - System error logs
- `./Audit_Logs/` - Complete audit trails

## Step 8: Scheduled Tasks

The system automatically runs scheduled tasks based on `scheduler_config.json`:

- Facebook auto-posting: Weekdays at 9 AM
- Instagram auto-posting: Weekdays at 12 PM
- Twitter auto-posting: Weekdays at 3 PM
- Odoo daily sync: Daily at 6 AM
- Odoo weekly reports: Every Monday at 6 AM
- Social media monitoring: Every 30 minutes
- Auto-commenting: Weekdays at 10 AM and 4 PM

## Expected Results

When properly configured, the system will:

1. **Post automatically** to Facebook, Instagram, and Twitter
2. **Comment automatically** on social media posts
3. **Sync with Odoo** daily to get sales and invoice data
4. **Generate reports** weekly for CEO briefings
5. **Monitor social engagement** continuously
6. **Handle errors** gracefully with recovery mechanisms
7. **Maintain audit trails** of all operations
8. **Run autonomously** 24/7 once started in continuous mode

## Troubleshooting

### If Odoo connection fails:
- Verify Odoo server is running on http://localhost:8069
- Check credentials in `credentials.json` are correct
- Ensure the database name is correct
- Verify username/password combination

### If social media APIs fail:
- Verify your API tokens are valid and have proper permissions
- Check rate limits for each platform
- Ensure tokens haven't expired

### If scheduled tasks don't run:
- Check `scheduler_config.json` for proper configuration
- Verify the Advanced Scheduler skill is working
- Check system logs for errors

## System Architecture

The AI Employee system consists of:
- **Skills Layer**: Individual capabilities (social media, Odoo, business)
- **Scheduler**: Automated task orchestration
- **Credentials Manager**: Secure API key storage
- **Audit System**: Complete operation logging
- **Error Recovery**: Automatic failure handling
- **Cross-Domain Integrator**: Business process coordination

## Security Notes

- Keep `credentials.json` secure and never commit to version control
- Use strong passwords for Odoo and API tokens
- Regularly rotate API keys
- Monitor logs for suspicious activity

---

The AI Employee system is now ready for full production use with automatic social media posting and Odoo integration! Once you have Odoo running and credentials configured, the system will operate completely autonomously.