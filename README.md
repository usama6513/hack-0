# Personal AI Employee - Bronze Tier Implementation

This project implements the Bronze Tier requirements for the Personal AI Employee Hackathon 0.

## Bronze Tier Requirements Completed

✓ **Obsidian vault with Dashboard.md and Company_Handbook.md** - Created initial vault structure with required files
✓ **One working Watcher script (file system monitoring)** - Implemented file_watcher.py that monitors a directory and moves files to the Inbox
✓ **Claude Code successfully reading from and writing to the vault** - Implemented vault_manager.py with functionality to read/write to vault directories
✓ **Basic folder structure: /Inbox, /Needs_Action, /Done** - Created the required directory structure
✓ **All AI functionality implemented as Agent Skills** - Created vault_manager.py in the skills/ directory with proper functionality

## Directory Structure

```
├── Inbox/              # Files requiring initial processing
├── Needs_Action/       # Files needing action
├── Done/               # Completed files
├── skills/             # Agent Skills implementation
│   └── vault_manager.py # Vault reading/writing functionality
├── file_watcher.py     # File system watcher implementation
├── Dashboard.md        # Main dashboard for the AI Employee
├── Company_Handbook.md # Business procedures and guidelines
└── README.md           # This file
```

## How to Run

1. **Start the file watcher:**
   ```bash
   python file_watcher.py
   ```
   This will monitor the `Watched_Folder` directory and move any new files to the Inbox.

2. **Run the orchestrator:**
   ```bash
   # Run continuously (default: checks every 30 seconds)
   python orchestrator.py

   # Run a single cycle
   python orchestrator.py --single

   # Run with custom interval (e.g., every 60 seconds)
   python orchestrator.py --interval 60
   ```
   The orchestrator processes files from the inbox and manages the workflow.

3. **Use the vault manager:**
   ```bash
   python skills/vault_manager.py
   ```
   This demonstrates the reading and writing functionality to the vault.

## Features

- **File System Watcher**: Monitors a specified directory and moves new files to the Inbox folder
- **Vault Management**: Read and write functionality to manage files across the three main folders
- **Task Processing**: Move tasks between Inbox → Needs_Action → Done workflow
- **Orchestrator**: Coordinates the entire system, processes files, and maintains logs
- **Documentation**: Dashboard and Company Handbook as required
- **Processing Logs**: Maintains audit trail of all actions taken

The Bronze Tier implementation provides a solid foundation that can be extended to Silver and Gold tiers with additional watchers, MCP servers, and more complex automation.