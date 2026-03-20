#!/bin/bash
# Silver Tier Installation Script for AI Employee

echo "Installing Silver Tier requirements for AI Employee..."
echo "=============================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed. Please install Python 3.13 or higher."
    exit 1
fi

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install requirements
echo "Installing Python packages..."
pip install -r requirements_silver.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install

# Install additional dependencies for specific platforms
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux detected - installing additional dependencies..."
    # Add Linux-specific installations if needed
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected - installing additional dependencies..."
    # Add macOS-specific installations if needed
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "Windows detected - installing additional dependencies..."
    # Add Windows-specific installations if needed
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p Drop
mkdir -p Email_Drafts
mkdir -p Email_Templates
mkdir -p Posted
mkdir -p Content
mkdir -p Analytics
mkdir -p Schedules
mkdir -p Schedule_Logs

# Create configuration files if they don't exist
echo "Setting up configuration files..."
touch mcp.json
touch credentials.json

# Set up Gmail credentials placeholder
echo '{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}' > credentials.json

echo ""
echo "=============================================="
echo "Silver Tier installation complete!"
echo ""
echo "Next steps:"
echo "1. Set up Gmail API credentials (see credentials.json)"
echo "2. Configure MCP servers in mcp.json"
echo "3. Test each skill individually:"
echo "   - python skills/vault_manager.py"
echo "   - python skills/linkedin_watcher.py"
echo "   - python skills/gmail_watcher.py"
echo "   - python skills/whatsapp_watcher.py"
echo "   - python skills/linkedin_poster.py"
echo "   - python skills/plan_generator.py"
echo "   - python skills/email_sender.py"
echo "   - python skills/approval_workflow.py"
echo "   - python skills/scheduler.py"
echo ""
echo "4. Run the full system:"
echo "   python run_bronze.py"