# AI Employee - Silver Tier Implementation

## Overview

Silver Tier adds professional communication capabilities to your AI Employee, including:
- Email monitoring and sending (Gmail integration)
- WhatsApp message monitoring
- LinkedIn monitoring and posting
- Human-in-the-loop approval system
- Automated scheduling
- MCP (Model Context Protocol) integration

## Prerequisites

- Python 3.7+
- Gmail API credentials (credentials.json)
- Chrome browser (for LinkedIn automation)
- WhatsApp Web access

## Installation

1. Install required packages:
```bash
python silver_tier_runner.py --setup
```

Or manually install:
```bash
pip install selenium playwright google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client schedule croniter watchdog requests
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Ensure Gmail credentials.json is in the parent directory

## Quick Start

1. **Initial Setup:**
```bash
python silver_tier_runner.py --setup
```

2. **Run Single Check:**
```bash
python silver_tier_runner.py --single
```

3. **Run Continuous Mode:**
```bash
python silver_tier_runner.py --continuous
```

## Skills Overview

### 1. Gmail Watcher (`skills/gmail_watcher.py`)
- Monitors Gmail inbox for new emails
- Creates action files for important messages
- Supports priority detection and auto-reply logic
- Uses existing credentials.json for authentication

### 2. WhatsApp Watcher (`skills/whatsapp_watcher.py`)
- Monitors WhatsApp Web for new messages
- Uses Playwright for browser automation
- Creates action files with priority analysis
- Supports session persistence

### 3. LinkedIn Watcher (`skills/linkedin_watcher.py`)
- Monitors LinkedIn for messages, notifications, and connection requests
- Uses Selenium WebDriver for automation
- Creates action files for different LinkedIn activities

### 4. LinkedIn Poster (`skills/linkedin_poster.py`)
- Generates business-focused content for LinkedIn posts
- Creates approval workflows for social media posts
- Supports content scheduling and performance tracking

### 5. Email Sender (`skills/email_sender.py`)
- Sends emails using MCP (Model Context Protocol)
- Falls back to SMTP if MCP is unavailable
- Supports email templates and approval workflows
- Integrates with approval system for external emails

### 6. Approval Workflow (`skills/approval_workflow.py`)
- Manages human-in-the-loop approval system
- Analyzes action risk levels
- Handles approval/rejection workflow
- Supports timeout and auto-approval for low-risk actions

### 7. Scheduler (`skills/scheduler.py`)
- Manages automated task scheduling
- Uses cron expressions for flexible scheduling
- Supports concurrent job execution
- Includes retry logic for failed tasks

### 8. Plan Generator (`skills/plan_generator.py`)
- Creates comprehensive execution plans
- Uses Claude reasoning loop for complex tasks
- Analyzes task complexity and dependencies

## Directory Structure

```
AI_Employee_Vault/
├── skills/                    # All skill implementations
├── Needs_Action/             # Pending actions requiring approval
├── Approved/                 # Approved actions ready for execution
├── Rejected/                 # Rejected actions
├── Pending/                  # Actions pending approval
├── Sent/                     # Sent emails log
├── Drafts/                   # Draft emails and posts
├── Content/                  # Scheduled content
├── Posted/                   # Posted content log
├── Templates/                # Email and content templates
├── Analytics/                # Performance analytics
├── Schedules/                # Job schedule files
├── Scheduler_Logs/           # Scheduler execution logs
├── Approval_Logs/            # Approval decision logs
├── Errors/                   # Error logs and failed actions
└── silver_tier_config.json   # Silver Tier configuration
```

## Configuration

### Main Configuration (`silver_tier_config.json`)
```json
{
  "enabled_skills": {
    "gmail_watcher": true,
    "whatsapp_watcher": true,
    "linkedin_watcher": true,
    "linkedin_poster": true,
    "email_sender": true,
    "approval_workflow": true,
    "scheduler": true,
    "plan_generator": true
  },
  "settings": {
    "check_interval": 60,
    "approval_timeout": 24,
    "max_concurrent_tasks": 5
  }
}
```

### Approval Configuration (`approval_config.json`)
```json
{
  "auto_approve_low_risk": true,
  "approval_timeout_hours": 24,
  "risk_categories": {
    "low": ["internal_communication", "draft_review"],
    "medium": ["external_email", "social_media_post", "data_export"],
    "high": ["financial_transaction", "delete_operation", "confidential_share"]
  }
}
```

### Scheduler Configuration (`scheduler_config.json`)
```json
{
  "default_schedule": {
    "gmail_check": "*/5 * * * *",
    "whatsapp_check": "*/2 * * * *",
    "linkedin_check": "*/10 * * * *",
    "linkedin_post": "0 9 * * 1-5",
    "backup_vault": "0 2 * * *"
  }
}
```

## Usage Examples

### 1. Create a LinkedIn Post
```bash
python silver_tier_runner.py --linkedin-post "AI automation benefits"
```

### 2. Send an Email
```bash
python silver_tier_runner.py --email "client@example.com" "Project Update" "Here's the latest update..."
```

### 3. Create a Task Plan
```bash
python silver_tier_runner.py --plan "Research AI automation trends and create report"
```

### 4. Run Specific Skill
```bash
python silver_tier_runner.py --skill gmail_watcher --method run_single_check
```

### 5. Check Status
```bash
python silver_tier_runner.py --status
```

## Approval Workflow

### How it Works:
1. AI Employee creates action files in `Needs_Action/`
2. Approval workflow analyzes risk level
3. High/Medium risk actions require approval
4. Low risk actions are auto-approved (configurable)
5. Humans review and move files to `Approved/` or `Rejected/`
6. Approved actions are executed automatically

### Approval File Format:
Files requiring approval have headers like:
```markdown
# APPROVAL REQUIRED - Action Request

**Action Type:** external_email
**Risk Level:** MEDIUM
**Created:** 2024-01-01T12:00:00
```

To approve: Move file to `Approved/` folder
To reject: Move file to `Rejected/` folder

## MCP Integration

The Email Sender supports MCP (Model Context Protocol) for external actions:

1. Configure MCP in `mcp_config.json`:
```json
{
  "mcp_enabled": true,
  "servers": {
    "email": {
      "enabled": true,
      "endpoint": "http://localhost:8080/mcp/email",
      "api_key": "your-api-key"
    }
  }
}
```

2. Falls back to SMTP if MCP unavailable

## Security Considerations

1. **Credential Management:**
   - Store credentials.json securely
   - Use environment variables for sensitive data
   - Never commit credentials to version control

2. **Approval System:**
   - All external communications require approval by default
   - Review approval rules regularly
   - Monitor approval logs

3. **Browser Automation:**
   - Uses Chrome profile for LinkedIn/WhatsApp
   - Ensure browser is secure and updated
   - Consider using dedicated browser profile

## Troubleshooting

### Gmail Issues:
- Ensure credentials.json is valid and in correct location
- Check Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen configuration

### WhatsApp Issues:
- Ensure QR code is scanned during setup
- Check WhatsApp Web works in browser
- Verify Playwright browsers are installed

### LinkedIn Issues:
- Ensure Chrome browser is installed
- Check Selenium WebDriver compatibility
- Verify LinkedIn credentials in browser profile

### Approval Workflow:
- Check file permissions on directories
- Ensure watchdog is installed for file monitoring
- Review approval_config.json settings

## Monitoring

- Check logs in respective `.log` files
- Monitor `Approval_Logs/` for approval decisions
- Review `Scheduler_Logs/` for task execution
- Check `Errors/` folder for failed actions

## Next Steps

After Silver Tier is running successfully:
1. Configure approval rules for your use case
2. Set up appropriate schedules
3. Train team on approval workflow
4. Monitor and adjust settings as needed
5. Consider upgrading to Gold Tier for advanced features

## Support

For issues or questions:
1. Check logs for error details
2. Review configuration files
3. Ensure all prerequisites are met
4. Verify credentials and permissions

---

**Silver Tier Complete!** Your AI Employee now has professional communication capabilities with human oversight.