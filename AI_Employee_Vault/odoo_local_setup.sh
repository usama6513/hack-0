#!/bin/bash
# Odoo Setup Script for Linux/Mac systems
# This script will install and run Odoo with Docker

echo "Setting up Odoo for AI Employee Integration..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    echo "For Ubuntu/Debian: sudo apt install docker.io"
    echo "For Mac: Install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "Docker is installed! Proceeding with Odoo setup..."

# Pull Odoo Docker image
echo "Pulling Odoo Docker image..."
docker pull odoo:18.0

if [ $? -ne 0 ]; then
    echo "Error pulling Odoo image"
    exit 1
fi

# Stop any existing Odoo containers
docker stop odoo odoo-db 2>/dev/null
docker rm odoo odoo-db 2>/dev/null

echo "Setting up Odoo with PostgreSQL database..."

# Create Odoo database container
echo "Creating Odoo database container..."
docker run -d \
    --name odoo-db \
    -e POSTGRES_USER=odoo \
    -e POSTGRES_PASSWORD=odoo \
    -e POSTGRES_DB=postgres \
    -v odoo-db-data:/var/lib/postgresql/data \
    postgres:13

# Wait a bit for the database to start
sleep 10

# Create Odoo application container
echo "Creating Odoo application container..."
docker run -d \
    --name odoo \
    -p 8069:8069 \
    -e POSTGRES_HOST=odoo-db \
    -e POSTGRES_USER=odoo \
    -e POSTGRES_PASSWORD=odoo \
    --link odoo-db:db \
    -v odoo-web-data:/var/lib/odoo \
    -v odoo-addons:/mnt/extra-addons \
    odoo:18.0

echo "Waiting for Odoo to start..."
sleep 30

# Check if Odoo is running
if docker ps | grep -q odoo; then
    echo ""
    echo "SUCCESS! Odoo is now running!"
    echo ""
    echo "Odoo is accessible at: http://localhost:8069"
    echo "Database: odoo"
    echo "Username: odoo"
    echo "Password: odoo"
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:8069 in your browser"
    echo "2. Create a new database (e.g., 'aie_employee_db')"
    echo "3. Set admin password"
    echo "4. Install required apps: Sales, Invoicing, CRM, Inventory"
    echo "5. Update credentials.json with your new database details"
    echo ""
    echo "Example credentials.json configuration:"
    echo "{"
    echo '  "odoo": {'
    echo '    "url": "http://localhost:8069",'
    echo '    "db": "aie_employee_db",'
    echo '    "username": "admin",'
    echo '    "password": "yourodompassword"'
    echo '  }'
    echo "}"
else
    echo "Error: Odoo container failed to start"
    docker logs odoo
fi