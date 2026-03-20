# Individual Automation Scripts - README

This document explains how to use the standalone automation scripts for LinkedIn, Gmail, and WhatsApp.

## Prerequisites

1. **Python 3.7+** installed
2. **Chrome browser** installed for LinkedIn automation
3. **Credentials configured** for each service
4. **Dependencies installed**:
```bash
pip install selenium playwright google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client webdriver-manager
```

## 1. LinkedIn Automation (`linkedin_automation.py`)

### Setup
1. Fill in your LinkedIn credentials in `linkedin_credentials.json`:
```json
{
  "email": "your-email@example.com",
  "password": "your-password",
  "profile_url": "https://www.linkedin.com/in/your-profile/"
}
```

### Usage

**Test content generation (no posting):**
```bash
python linkedin_automation.py --test
```

**Post to LinkedIn with custom topic:**
```bash
python linkedin_automation.py --post "AI automation benefits"
```

**Schedule automated posting (every 24 hours):**
```bash
python linkedin_automation.py --schedule 24
```

**Default post (AI automation topic):**
```bash
python linkedin_automation.py
```

### Features
- Automatically generates business-focused content
- Posts directly to your LinkedIn profile
- Saves posted content for records
- Supports scheduled posting
- Uses Chrome browser automation

## 2. Gmail Automation (`gmail_automation.py`)

### Setup
1. Ensure `credentials.json` is in the parent directory (same as Silver Tier)
2. Run authentication flow on first use

### Usage

**Check unread emails once:**
```bash
python gmail_automation.py --check
```

**Monitor inbox continuously:**
```bash
python gmail_automation.py --monitor
```

**Send an email:**
```bash
python gmail_automation.py --send "recipient@example.com" "Subject" "Email body"
```

**Send bulk emails:**
```bash
# Create recipients.txt with one email per line
python gmail_automation.py --bulk recipients.txt "Subject" "Email body"
```

**Auto-reply to emails:**
```bash
python gmail_automation.py --auto-reply "support" "Auto-reply: Support Request" "Thank you for contacting support. We'll get back to you soon."
```

### Features
- Monitors Gmail inbox for new emails
- Sends emails directly through Gmail API
- Creates action files for important emails
- Supports bulk email sending
- Auto-reply functionality
- Automatic email prioritization

## 3. WhatsApp Automation (`whatsapp_automation.py`)

### Setup
1. No credentials file needed (uses QR code login)
2. Ensure WhatsApp is active on your phone

### Usage

**Check unread messages once:**
```bash
python whatsapp_automation.py --check
```

**Monitor messages continuously:**
```bash
python whatsapp_automation.py --monitor
```

**Send a message:**
```bash
python whatsapp_automation.py --send "Contact Name" "Your message"
```

**Auto-reply to messages:**
```bash
python whatsapp_automation.py --auto-reply "price" "Our prices start at $99/month"
```

**Auto-reply with contact restrictions:**
```bash
# Create contacts.txt with one contact per line
python whatsapp_automation.py --auto-reply "price" "Our prices..." --contacts contacts.txt
```

### Features
- Monitors WhatsApp for new messages
- Sends messages to contacts
- Auto-reply based on keywords
- Message priority analysis
- Session persistence (no repeated QR scanning)

## Important Notes

### LinkedIn Automation
- **First Run**: Chrome will open for LinkedIn login
- **Security**: Keep your credentials file secure
- **Rate Limiting**: Avoid posting too frequently (recommended: 1-2 posts per day)
- **Content**: Generated content is professional and business-focused

### Gmail Automation
- **Permissions**: First run requires OAuth approval
- **Rate Limiting**: Gmail has sending limits (500 emails/day for regular accounts)
- **Bulk Sending**: Add delays between emails to avoid spam filters
- **Privacy**: Emails are processed locally, no data sent to third parties

### WhatsApp Automation
- **QR Code**: Required on first run or after session expires
- **Phone Connection**: Phone must be connected to internet
- **Headless Mode**: Currently disabled as WhatsApp requires visible browser
- **Contact Names**: Use exact names as saved in your WhatsApp

## Monitoring and Logs

Each script creates its own log file:
- `linkedin_automation.log`
- `gmail_automation.log`
- `whatsapp_automation.log`

Check these logs for:
- Success/failure of operations
- Error messages
- Activity timestamps

## Security Considerations

1. **Credentials**: Never commit credentials to version control
2. **Rate Limiting**: Respect platform limits to avoid account suspension
3. **Personal Use**: These scripts are for personal automation only
4. **Backup**: Keep backups of your data and configurations

## Troubleshooting

### Common Issues

1. **Chrome not found**: Install Chrome browser or update paths in script
2. **Authentication failed**: Check credentials and re-authenticate
3. **Timeout errors**: Increase timeout values in scripts
4. **Unicode errors**: Fixed in scripts, but ensure terminal supports UTF-8

### Getting Help

Check the log files first for error details. Common solutions:
- Re-authenticate with OAuth
- Update Chrome browser
- Check internet connection
- Verify credentials are correct

## Next Steps

1. Configure credentials for each service
2. Test each script individually
3. Set up monitoring schedules
4. Customize content and responses
5. Monitor logs regularly

These scripts give you full control over your LinkedIn, Gmail, and WhatsApp automation with direct posting and sending capabilities!