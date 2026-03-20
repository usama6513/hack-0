# Silver Tier Orchestrator Agent - Setup Guide

## Overview

The Silver Tier Orchestrator Agent implements a complete automated email workflow with human-in-the-loop approval:

```
Gmail → Needs_Action → Plan → Pending_Approval → [HUMAN APPROVES] → Approved → Sent
```

## Workflow Steps

### 1. **Gmail Watcher** (Automatic)
- Monitors Gmail for new unread emails
- Filters emails containing important keywords
- Creates action files in `Needs_Action/` folder

### 2. **AI Reply Generation** (Automatic)
- Reads emails from `Needs_Action/`
- Generates appropriate AI reply based on email content
- Creates Plan file in `Plans/` folder
- Updates status to `plan_generated.com`

### 3. **Approval Request** (Automatic)
- Creates approval request file in `Pending_Approval/`
- Includes generated reply for review
- Waits for human approval

### 4. **Human-in-the-Loop** (Manual - YOUR ACTION)
- **YOUR TASK:** Review the generated reply
- **YOUR TASK:** Move file from `Pending_Approval/` to `Approved/` folder
- That's it! The rest is automatic.

### 5. **Email Sending** (Automatic)
- Orchestrator detects approved files
- Sends email on your behalf
- Logs sent email in `Sent/` folder
- Moves task to complete

## Directory Structure

```
AI_Employee_Vault/
├── Needs_Action/         # New emails requiring action
├── Plans/                # Generated plans with AI replies
├── Pending_Approval/     # Awaiting your approval ← YOU ACT HERE
├── Approved/             # Move files here to send ← YOUR ACTION
├── Sent/                 # Sent emails log
└── Rejected/             # Rejected emails
```

## Setup Instructions

### Prerequisites

1. **Gmail API Credentials**
   - Ensure `credentials.json` is in the parent directory
   - First run will create `token.json` automatically

2. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Edit `silver_tier_config.json` to customize settings

### Running the Orchestrator

#### Option 1: Run Once (Test)
```bash
cd AI_Employee_Vault
python silver_orchestrator.py --single
```

#### Option 2: Run Continuously
```bash
cd AI_Employee_Vault
python silver_orchestrator.py
```

#### Option 3: Custom Interval
```bash
cd AI_Employee_Vault
python silver_orchestrator.py --interval 120
```

## Configuration

Edit `silver_tier_config.json`:

```json
{
  "enabled_watchers": {
    "gmail": true,
    "whatsapp": false,
    "linkedin": false
  },
  "check_interval_seconds": 60,
  "gmail_check_interval_seconds": 120,
  "auto_generate_replies": true,
  "require_approval_for_emails": true,
  "max_emails_per_cycle": 5,
  "important_keywords": [
    "urgent", "asap", "important", "deadline", "invoice",
    "payment", "meeting", "proposal", "client", "project"
  ]
}
```

## Testing the Setup

### Test 1: Run the Orchestrator
```bash
python silver_orchestrator.py --single
```

Expected output:
- Gmail Watcher runs
- Finds unread emails
- Creates files in `Needs_Action/`
- Generates plans in `Plans/`
- Creates approval requests in `Pending_Approval/`

### Test 2: Check Directories
After running, check:
- `Needs_Action/` - Should have GMAIL_*.md files
- `Plans/` - Should have PLAN_*.md files
- `Pending_Approval/` - Should have APPROVAL_*_EMAIL_REPLY.md files

### Test 3: Human-in-the-Loop Test
1. Open any file in `Pending_Approval/`
2. Review the generated reply
3. Move the file to `Approved/` folder
4. Run orchestrator again: `python silver_orchestrator.py --single`
5. Check `Sent/` folder - file should be there

## Important Keywords

The orchestrator catches emails containing these keywords:
- urgent
- asap
- important
- deadline
- invoice
- payment
- meeting
- proposal
- client
- project
- contract
- agreement
- review
- approval
- decision

You can customize these in `silver_tier_config.json`.

## Your Role (Human-in-the-Loop)

**You only need to do ONE thing:**

When you see a new file in `Pending_Approval/` folder:
1. Open the file
2. Review the AI-generated reply
3. Edit if needed (optional)
4. **Move the file to `Approved/` folder**

The orchestrator will handle the rest automatically!

## Logs

Check `silver_orchestrator.log` for detailed logs of all activities.

## Troubleshooting

### Gmail Authentication Error
- Delete `token.json` and re-run
- Ensure `credentials.json` is correct

### No Emails Found
- Check if emails are marked as unread
- Verify keywords match your emails

### Approval Not Processing
- Ensure file is in `Approved/` folder (not `Pending_Approval/`)
- File name should start with `APPROVAL_`

## Next Steps

After testing Silver Tier, we'll implement the same pattern for Gold Tier with:
- Facebook integration
- Instagram integration
- Twitter integration
- Odoo accounting
- CEO Briefing generation
