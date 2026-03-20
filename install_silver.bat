@echo off
REM Silver Tier Installation Script for AI Employee (Windows)

echo Installing Silver Tier requirements for AI Employee...
echo ==============================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed. Please install Python 3.13 or higher.
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set python_version=%%i
echo Python version: %python_version%

REM Install requirements
echo Installing Python packages...
pip install -r requirements_silver.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
python -m playwright install

REM Create necessary directories
echo Creating necessary directories...
if not exist "Drop" mkdir Drop
if not exist "Email_Drafts" mkdir Email_Drafts
if not exist "Email_Templates" mkdir Email_Templates
if not exist "Posted" mkdir Posted
if not exist "Content" mkdir Content
if not exist "Analytics" mkdir Analytics
if not exist "Schedules" mkdir Schedules
if not exist "Schedule_Logs" mkdir Schedule_Logs

REM Create configuration files
echo Setting up configuration files...
echo. > mcp.json
echo. > credentials.json

REM Set up Gmail credentials placeholder
echo {
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
} > credentials.json

echo.
echo ==============================================
echo Silver Tier installation complete!
echo.
echo Next steps:
echo 1. Set up Gmail API credentials (see credentials.json)
echo 2. Configure MCP servers in mcp.json
echo 3. Test each skill individually:
echo    - python skills/vault_manager.py
echo    - python skills/linkedin_watcher.py
echo    - python skills/gmail_watcher.py
echo    - python skills/whatsapp_watcher.py
echo    - python skills/linkedin_poster.py
echo    - python skills/plan_generator.py
echo    - python skills/email_sender.py
echo    - python skills/approval_workflow.py
echo    - python skills/scheduler.py
echo.
echo 4. Run the full system:
echo    python run_bronze.py
echo.
pause