#!/bin/bash

# Luanti/Minetest Mod Unloader Script
# Usage: ./unload_mod.sh <mod_name>

set -e

# Configuration
SERVER_MODS_DIR="/var/games/minetest-server/.minetest/mods"
WORLD_CONFIG="/var/games/minetest-server/.minetest/worlds/world/world.mt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if running as root or with sudo
check_permissions() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Function to unload a mod
unload_mod() {
    local mod_name="$1"
    
    print_status "Unloading mod: $mod_name"
    
    # Disable mod in world.mt
    if grep -q "^load_mod_${mod_name} = true" "$WORLD_CONFIG"; then
        sed -i "/^load_mod_${mod_name} = true/d" "$WORLD_CONFIG"
        print_status "Mod disabled in world configuration"
    else
        print_warning "Mod $mod_name was not enabled in world configuration"
    fi
    
    # Ask if user wants to remove mod files
    if [[ -d "$SERVER_MODS_DIR/$mod_name" ]]; then
        read -p "Remove mod files from server? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$SERVER_MODS_DIR/$mod_name"
            print_status "Mod files removed from server"
        else
            print_status "Mod files kept in server directory (disabled only)"
        fi
    else
        print_warning "Mod directory not found in server mods"
    fi
    
    print_status "Mod $mod_name unloaded successfully!"
    print_warning "Server restart required for changes to take effect"
    echo
    read -p "Restart server now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl restart minetest-server
        print_status "Server restarted"
    else
        print_warning "Remember to restart the server later with: sudo systemctl restart minetest-server"
    fi
}

# Main execution
if [[ $# -eq 0 ]]; then
    print_error "Usage: $0 <mod_name>"
    echo "Example: $0 nullifier_adventure"
    exit 1
fi

check_permissions
unload_mod "$1"