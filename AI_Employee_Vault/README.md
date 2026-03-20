# AI Employee Vault - Bronze Tier

This is an Obsidian vault for the Personal AI Employee Hackathon Bronze Tier implementation.

## How to Open This Vault in Obsidian

1. Download and install Obsidian from https://obsidian.md/
2. Open Obsidian
3. Click "Open folder as vault"
4. Navigate to and select the `AI_Employee_Vault` folder
5. The vault will open with all files and folders visible

## Vault Structure

```
AI_Employee_Vault/
├── .obsidian/              # Obsidian configuration
├── Inbox/                  # New files awaiting processing
├── Needs_Action/           # Files requiring action
├── Done/                   # Completed tasks
├── skills/                 # Agent Skills implementation
│   └── vault_manager.py   # Vault operations
├── file_watcher.py        # File system monitoring (custom)
├── filesystem_watcher.py  # File system monitoring (standard)
├── orchestrator.py        # Main system coordinator
├── Dashboard.md           # System dashboard
├── Company_Handbook.md    # Business procedures
└── README.md             # This file
```

## Quick Start

1. **Start a file watcher (choose one):**
   ```bash
   python file_watcher.py        # Custom implementation
   # OR
   python filesystem_watcher.py  # Standard implementation
   ```

2. **Run the orchestrator:**
   ```bash
   python orchestrator.py --single  # Run once
   # OR
   python orchestrator.py           # Run continuously
   ```

3. **View the Dashboard** - Open `Dashboard.md` in Obsidian to see system status

## Watchers Explained

- **file_watcher.py**: Custom implementation with additional features
- **filesystem_watcher.py**: Standard implementation matching the hackathon documentation

## Bronze Tier Requirements Met

✓ Obsidian vault with Dashboard.md and Company_Handbook.md
✓ One working Watcher script (file system monitoring)
✓ Claude Code successfully reading from and writing to the vault
✓ Basic folder structure: /Inbox, /Needs_Action, /Done
✓ All AI functionality implemented as Agent Skills
✓ Orchestrator for system coordination

## Next Steps

For Silver Tier, consider adding:
- Gmail watcher
- WhatsApp integration
- LinkedIn automation
- MCP servers for external actions