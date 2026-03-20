# API Credentials Setup Guide

This guide explains how to set up API credentials for the Gold Tier AI Employee system to enable real social media posting and Odoo integration.

## Prerequisites

1. Create a `credentials.json` file in the root directory with the template structure
2. Each API requires specific access tokens and credentials
3. For Odoo, you need to have a local or cloud instance running

## Setting Up API Credentials

### 1. Facebook API Setup

To enable Facebook posting and commenting:

1. Go to [Facebook Developers Console](https://developers.facebook.com/)
2. Create a new app or use an existing one
3. Add the "Facebook Pages" product to your app
4. Generate a Page Access Token with these permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_manage_engagement`
5. Get your Facebook Page ID from your page settings
6. Add to `credentials.json`:

```json
{
  "facebook": {
    "access_token": "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN",
    "page_id": "YOUR_FACEBOOK_PAGE_ID",
    "app_id": "YOUR_FACEBOOK_APP_ID",
    "app_secret": "YOUR_FACEBOOK_APP_SECRET",
    "api_version": "v18.0"
  }
}
```

### 2. Instagram API Setup

To enable Instagram posting and commenting:

1. You need a Facebook Page connected to an Instagram Business Account
2. Go to [Facebook Developers Console](https://developers.facebook.com/)
3. Use the same app you created for Facebook
4. Generate a long-lived Instagram Access Token using the Access Token Tool
5. Get your Instagram Business Account ID
6. Add to `credentials.json`:

```json
{
  "instagram": {
    "access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN",
    "account_id": "YOUR_INSTAGRAM_BUSINESS_ACCOUNT_ID",
    "app_id": "YOUR_INSTAGRAM_APP_ID",
    "app_secret": "YOUR_INSTAGRAM_APP_SECRET",
    "api_version": "v18.0"
  }
}
```

### 3. Twitter API Setup

To enable Twitter posting and engagement:

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for a developer account and create a new app
3. Generate your API keys and tokens:
   - API Key
   - API Secret Key
   - Access Token
   - Access Token Secret
   - Bearer Token
4. Add to `credentials.json`:

```json
{
  "twitter": {
    "bearer_token": "YOUR_TWITTER_BEARER_TOKEN",
    "api_key": "YOUR_TWITTER_API_KEY",
    "api_secret": "YOUR_TWITTER_API_SECRET",
    "access_token": "YOUR_TWITTER_ACCESS_TOKEN",
    "access_token_secret": "YOUR_TWITTER_ACCESS_TOKEN_SECRET",
    "api_version": "2"
  }
}
```

### 4. Odoo API Setup

To enable Odoo integration:

1. Make sure you have an Odoo instance running (local or cloud)
2. For local development, Odoo typically runs on `http://localhost:8069`
3. Get your database name, username, and password from your Odoo instance
4. Add to `credentials.json`:

```json
{
  "odoo": {
    "url": "http://localhost:8069",  // Your Odoo instance URL
    "db": "your_database_name",
    "username": "your_username",
    "password": "your_password"
  }
}
```

## Security Best Practices

⚠️ **IMPORTANT SECURITY NOTES:**

1. Never commit `credentials.json` to version control
2. Add `credentials.json` to your `.gitignore` file
3. Keep your API keys secure and never share them publicly
4. Use environment variables for production deployments
5. Regularly rotate your API keys for security

## Testing Your Setup

After configuring your credentials:

1. Run the enhanced test suite:
   ```bash
   python test_gold_tier_enhanced.py
   ```

2. Verify that all integration tests pass

3. Check the log files to ensure API connections are working:
   - `facebook_api_integration.log`
   - `instagram_api_integration.log`
   - `twitter_api_integration.log`
   - `odoo_integration.log`
   - `advanced_scheduler.log`

## Troubleshooting

### Common Issues:

1. **API Rate Limits**: All social media APIs have rate limits. The scheduler includes retry logic to handle this.

2. **Invalid Credentials**: Double-check all tokens and IDs in your `credentials.json`

3. **Odoo Connection**: Ensure your Odoo instance is running and accessible

4. **Permissions**: Make sure your API tokens have the required permissions

### Verification Steps:

1. Check that `credentials.json` exists in the root directory
2. Verify all required fields are filled in
3. Test each API individually before enabling scheduled tasks
4. Monitor log files for errors

## Enabling Scheduled Tasks

Once your credentials are set up, the Advanced Scheduler will automatically use them for scheduled posting tasks. The scheduler configuration is in `scheduler_config.json` and includes:

- Facebook auto posting (weekdays at 9 AM)
- Instagram auto posting (weekdays at 12 PM)
- Twitter auto posting (weekdays at 3 PM)
- Odoo data sync (daily at 6 AM)
- Weekly reporting (Monday at 6 AM)
- Social media monitoring (every 30 minutes)

The scheduler will only execute tasks when valid credentials are present for each platform.