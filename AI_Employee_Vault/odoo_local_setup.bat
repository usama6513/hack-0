@echo off
echo Setting up Odoo for AI Employee Integration...
echo.

echo Step 1: Check if Docker is installed...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Installing Docker Desktop is recommended.
    echo Please download and install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Docker is installed! Proceeding with Odoo setup...
echo.

echo Step 2: Pulling Odoo Docker image...
docker pull odoo:18.0
if %errorlevel% neq 0 (
    echo Error pulling Odoo image
    pause
    exit /b 1
)

echo Step 3: Setting up Odoo with PostgreSQL database...
echo Creating Odoo database container...
docker run -d ^
    --name odoo-db ^
    -e POSTGRES_USER=odoo ^
    -e POSTGRES_PASSWORD=odoo ^
    -e POSTGRES_DB=postgres ^
    -v odoo-db-data:/var/lib/postgresql/data ^
    postgres:13

timeout /t 10 /nobreak >nul

echo Creating Odoo application container...
docker run -d ^
    --name odoo ^
    -p 8069:8069 ^
    -e POSTGRES_HOST=odoo-db ^
    -e POSTGRES_USER=odoo ^
    -e POSTGRES_PASSWORD=odoo ^
    --link odoo-db:db ^
    -v odoo-web-data:/var/lib/odoo ^
    -v odoo-addons:/mnt/extra-addons ^
    odoo:18.0

echo.
echo Step 4: Waiting for Odoo to start...
timeout /t 30 /nobreak >nul

echo Step 5: Checking Odoo status...
docker ps | findstr odoo >nul
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS! Odoo is now running!
    echo.
    echo Odoo is accessible at: http://localhost:8069
    echo Database: odoo
    echo Username: odoo
    echo Password: odoo
    echo.
    echo Next steps:
    echo 1. Open http://localhost:8069 in your browser
    echo 2. Create a new database (e.g., "aie_employee_db")
    echo 3. Set admin password
    echo 4. Install required apps: Sales, Invoicing, CRM, Inventory
    echo 5. Update credentials.json with your new database details
    echo.
    echo Example credentials.json configuration:
    echo {
    echo   "odoo": {
    echo     "url": "http://localhost:8069",
    echo     "db": "aie_employee_db",
    echo     "username": "admin",
    echo     "password": "yourodompassword"
    echo   }
    echo }
) else (
    echo Error: Odoo container failed to start
    docker logs odoo
)

echo.
echo Setup complete! Press any key to exit.
pause >nul