# Silver Tier Orchestrator - Quick Start Guide

## Setup Complete! ✅

Aapka Silver Tier Orchestrator Agent setup complete ho gaya hai with complete workflow automation.

## Workflow Summary

```
Gmail → Needs_Action → Plan → Pending_Approval → [YOU APPROVE] → Approved → Sent
```

## Aapka Role (Human-in-the-Loop)

**Sirf EK kaam karna hai:**

Jab bhi nayi file `Pending_Approval/` folder mein aaye:
1. File ko open karein
2. AI-generated reply ko review karein
3. Agar theek ho toh file ko `Approved/` folder mein move kar dein

**Baaki sab kuch Orchestrator automatically karega!**

## Quick Commands

### Test Setup
```bash
cd AI_Employee_Vault
python test_silver_tier_setup.py
```

### Run Orchestrator (Single Cycle)
```bash
python silver_orchestrator.py --single
```

### Run Orchestrator (Continuous)
```bash
python silver_orchestrator.py
```

### Run with Custom Interval
```bash
python silver_orchestrator.py --interval 120
```

## Testing Steps

### Step 1: Test Setup
```bash
python test_silver_tier_setup.py
```
Expected: 5/6 tests pass (module import warning is OK)

### Step 2: Check Directories
Ye folders ban chuke honge:
- `Inbox/`
- `Needs_Action/`
- `Plans/`
- `Pending_Approval/`
- `Approved/`
- `Sent/`
- `Rejected/`

### Step 3: Run Orchestrator
```bash
python silver_orchestrator.py --single
```

### Step 4: Check Results
- `Needs_Action/` - Check for new email files
- `Plans/` - Check for generated plans
- `Pending_Approval/` - Check for approval requests

### Step 5: Test Human-in-the-Loop
1. Open any file in `Pending_Approval/`
2. Review the AI reply
3. Move file to `Approved/` folder
4. Run orchestrator again: `python silver_orchestrator.py --single`
5. Check `Sent/` folder - email should be there!

## Important Keywords

Orchestrator in keywords wali emails ko catch karega:
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

## Configuration

Edit `silver_tier_config.json`:

```json
{
  "enabled_watchers": {
    "gmail": true,      // Gmail watcher enable/disable
    "whatsapp": false,  // Future: WhatsApp watcher
    "linkedin": false   // Future: LinkedIn watcher
  },
  "check_interval_seconds": 60,  // Check frequency
  "auto_generate_replies": true, // AI reply generation
  "require_approval_for_emails": true, // Human-in-the-loop
  "max_emails_per_cycle": 5  // Max emails per cycle
}
```

## Logs

Check `silver_orchestrator.log` for detailed activity logs.

## Files Created

| File | Purpose |
|------|---------|
| `silver_orchestrator.py` | Main orchestrator agent |
| `silver_tier_config.json` | Configuration file |
| `SILVER_TIER_ORCHESTRATOR_GUIDE.md` | Detailed guide |
| `test_silver_tier_setup.py` | Test script |
| `SILVER_TIER_QUICK_START.md` | This file |

## Next Steps

### Silver Tier Testing Complete?

Jab aap Silver Tier test kar lein, toh batayein. Phir hum **Gold Tier** implement karenge with:

1. ✅ Facebook integration
2. ✅ Instagram integration  
3. ✅ Twitter (X) integration
4. ✅ Odoo accounting integration
5. ✅ CEO Briefing generation
6. ✅ Cross-domain automation

## Troubleshooting

### Gmail Authentication Error
- `token.json` delete karein aur dobara run karein
- Ensure `credentials.json` parent directory mein ho

### No Emails Found
- Check emails unread hon
- Keywords match karein

### Approval Not Processing
- File `Approved/` folder mein honi chahiye
- File name `APPROVAL_*` se start hona chahiye

## Support

For detailed documentation, read:
- `SILVER_TIER_ORCHESTRATOR_GUIDE.md` - Complete guide
- `silver_orchestrator.log` - Activity logs

---

**Setup Status:** ✅ COMPLETE  
**Ready to Test:** YES  
**Next Tier:** Gold Tier (after Silver testing)
