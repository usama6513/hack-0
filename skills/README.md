# AI Employee Skills - Silver Tier

This directory contains all the Agent Skills for the Silver Tier implementation of the Personal AI Employee.

## Silver Tier Skills Overview

Silver Tier adds the following capabilities to your AI Employee:

### 1. **Social Media Integration**
- **LinkedIn Watcher** (`linkedin_watcher.py`) - Monitors LinkedIn for messages, notifications, and connection requests
- **LinkedIn Poster** (`linkedin_poster.py`) - Automatically creates and posts business content to generate sales

### 2. **Communication Watchers**
- **Gmail Watcher** (`gmail_watcher.py`) - Monitors Gmail for new emails and creates action files
- **WhatsApp Watcher** (`whatsapp_watcher.py`) - Monitors WhatsApp messages using Playwright

### 3. **Intelligence & Planning**
- **Plan Generator** (`plan_generator.py`) - Creates comprehensive Plan.md files with Claude reasoning loop

### 4. **External Actions**
- **Email Sender** (`email_sender.py`) - Sends emails via MCP (Model Context Protocol) integration

### 5. **Safety & Control**
- **Approval Workflow** (`approval_workflow.py`) - Human-in-the-loop approval for sensitive actions
- **Scheduler** (`scheduler.py`) - Basic scheduling via cron/Task Scheduler

### 6. **Foundation Skills (from Bronze Tier)**
- **Vault Manager** (`vault_manager.py`) - Manages reading/writing to Obsidian vault

## Quick Start

1. **Set up LinkedIn integration:**
   ```bash
   python skills/linkedin_watcher.py  # Monitor LinkedIn
   python skills/linkedin_poster.py   # Auto-post content
   ```

2. **Set up communication watchers:**
   ```bash
   python skills/gmail_watcher.py     # Monitor Gmail
   python skills/whatsapp_watcher.py  # Monitor WhatsApp
   ```

3. **Create plans with reasoning:**
   ```bash
   python skills/plan_generator.py    # Generate execution plans
   ```

4. **Send emails via MCP:**
   ```bash
   python skills/email_sender.py      # Email integration
   ```

5. **Set up approvals and scheduling:**
   ```bash
   python skills/approval_workflow.py # Approval system
   python skills/scheduler.py         # Task scheduling
   ```

## Dependencies

Install required packages:
```bash
pip install selenium playwright google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Configuration

1. **Gmail Setup:**
   - Enable Gmail API in Google Cloud Console
   - Download credentials.json
   - Run gmail_watcher.py to authenticate

2. **LinkedIn Setup:**
   - Requires manual login for WhatsApp Web automation
   - Session is saved for future use

3. **MCP Setup:**
   - Configure MCP servers in mcp.json
   - Email MCP requires Gmail credentials

4. **Schedule Setup:**
   - Linux/Mac: Uses cron
   - Windows: Creates Task Scheduler tasks

## Silver Tier Requirements Met

✅ Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn)
✅ Automatically Post on LinkedIn about business to generate sales
✅ Claude reasoning loop that creates Plan.md files
✅ One working MCP server for external action (email sending)
✅ Human-in-the-loop approval workflow for sensitive actions
✅ Basic scheduling via cron or Task Scheduler
✅ All AI functionality implemented as Agent Skills

## Next Steps (Gold Tier)

- Full cross-domain integration (Personal + Business)
- Odoo accounting system integration via MCP
- Facebook and Instagram integration
- Twitter (X) integration
- Multiple MCP servers
- Weekly business audits with CEO briefings
- Ralph Wiggum loop for autonomous completion