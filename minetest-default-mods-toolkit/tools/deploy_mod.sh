#!/bin/bash
# deploy_mod.sh - Deploy a mod to the Minetest/Luanti server
# Usage: ./deploy_mod.sh <mod_directory>

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
WORLD_PATH="/var/games/minetest-server/.minetest/worlds/world"
WORLDMODS_PATH="$WORLD_PATH/worldmods"
WORLD_MT="$WORLD_PATH/world.mt"
SERVICE_NAME="minetest-server"
SERVER_USER="Debian-minetest"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check arguments
MOD_PATH="$1"
if [ -z "$MOD_PATH" ] || [ ! -d "$MOD_PATH" ]; then
    print_error "Usage: $0 <mod_directory>"
    echo "       Example: $0 ~/luanti/my_mods/signs_fix"
    exit 1
fi

# Get mod name from directory or mod.conf
MOD_NAME=$(basename "$MOD_PATH")
if [ -f "$MOD_PATH/mod.conf" ]; then
    CONF_NAME=$(grep "^name" "$MOD_PATH/mod.conf" | cut -d'=' -f2 | tr -d ' ')
    if [ -n "$CONF_NAME" ]; then
        MOD_NAME="$CONF_NAME"
    fi
fi

echo "========================================="
echo "Deploying mod: $MOD_NAME"
echo "From: $MOD_PATH"
echo "To: $WORLDMODS_PATH/$MOD_NAME"
echo "========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    print_warning "This script needs sudo privileges. Re-running with sudo..."
    exec sudo "$0" "$@"
fi

# Step 1: Validate mod structure
print_status "Validating mod structure..."
if [ ! -f "$MOD_PATH/init.lua" ]; then
    print_error "No init.lua found in mod directory"
    exit 1
fi

if [ ! -f "$MOD_PATH/mod.conf" ]; then
    print_warning "No mod.conf found - mod might not load properly"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Backup existing mod if it exists
if [ -d "$WORLDMODS_PATH/$MOD_NAME" ]; then
    BACKUP_NAME="${MOD_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
    print_warning "Existing mod found. Creating backup: $BACKUP_NAME"
    cp -r "$WORLDMODS_PATH/$MOD_NAME" "$WORLDMODS_PATH/$BACKUP_NAME"
fi

# Step 3: Stop the server
print_status "Stopping $SERVICE_NAME..."
systemctl stop "$SERVICE_NAME"
sleep 2

# Verify server stopped
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_error "Failed to stop server"
    exit 1
fi

# Step 4: Create worldmods directory if needed
if [ ! -d "$WORLDMODS_PATH" ]; then
    print_status "Creating worldmods directory..."
    mkdir -p "$WORLDMODS_PATH"
fi

# Step 5: Copy the mod
print_status "Copying mod files..."
rm -rf "$WORLDMODS_PATH/$MOD_NAME"
cp -r "$MOD_PATH" "$WORLDMODS_PATH/$MOD_NAME"

# Step 6: Set proper permissions
print_status "Setting permissions..."
chown -R "$SERVER_USER:$SERVER_USER" "$WORLDMODS_PATH/$MOD_NAME"
chmod -R 755 "$WORLDMODS_PATH/$MOD_NAME"

# Step 7: Enable mod in world.mt
print_status "Enabling mod in world.mt..."
if grep -q "^load_mod_$MOD_NAME" "$WORLD_MT"; then
    # Update existing entry
    sed -i "s/^load_mod_$MOD_NAME.*/load_mod_$MOD_NAME = true/" "$WORLD_MT"
    print_status "Updated existing mod entry"
else
    # Add new entry
    echo "load_mod_$MOD_NAME = true" >> "$WORLD_MT"
    print_status "Added new mod entry"
fi

# Step 8: Start the server
print_status "Starting $SERVICE_NAME..."
systemctl start "$SERVICE_NAME"

# Step 9: Wait for server to start
print_status "Waiting for server to initialize..."
sleep 5

# Step 10: Check if server started successfully
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "Server started successfully"
    
    # Check if mod loaded
    echo ""
    echo "Checking mod status in logs..."
    if grep -q "$MOD_NAME" /var/log/minetest/minetest.log; then
        print_status "Mod mentioned in logs:"
        grep "$MOD_NAME" /var/log/minetest/minetest.log | tail -3
    else
        print_warning "Mod not mentioned in recent logs"
    fi
    
    # Check for errors
    RECENT_ERRORS=$(grep "ERROR.*$MOD_NAME" /var/log/minetest/minetest.log | tail -3)
    if [ -n "$RECENT_ERRORS" ]; then
        print_warning "Recent errors related to mod:"
        echo "$RECENT_ERRORS"
    fi
    
    echo ""
    print_status "Deployment complete!"
    echo ""
    echo "Server is running on port 30000"
    echo "Mod installed at: $WORLDMODS_PATH/$MOD_NAME"
    
else
    print_error "Server failed to start!"
    echo ""
    echo "Recent log entries:"
    journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    
    echo ""
    print_warning "Rolling back changes..."
    
    # Disable mod
    sed -i "s/^load_mod_$MOD_NAME.*/load_mod_$MOD_NAME = false/" "$WORLD_MT"
    
    # Try to start server again
    systemctl start "$SERVICE_NAME"
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "Server recovered after disabling mod"
    else
        print_error "Server still failing - manual intervention required"
    fi
    
    exit 1
fi