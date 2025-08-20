#!/bin/bash

# Luanti/Minetest Mod Listing Script
# Usage: ./list_mods.sh

# Configuration
SERVER_MODS_DIR="/var/games/minetest-server/.minetest/mods"
WORLD_CONFIG="/var/games/minetest-server/.minetest/worlds/world/world.mt"
LOCAL_MODS_DIR="/home/tdeshane/luanti"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_disabled() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to check if mod is enabled
is_mod_enabled() {
    local mod_name="$1"
    grep -q "^load_mod_${mod_name} = true" "$WORLD_CONFIG" 2>/dev/null
}

# List server mods
list_server_mods() {
    print_header "Server Mods (${SERVER_MODS_DIR})"
    
    if [[ -d "$SERVER_MODS_DIR" ]]; then
        for mod in "$SERVER_MODS_DIR"/*; do
            if [[ -d "$mod" ]]; then
                mod_name=$(basename "$mod")
                if is_mod_enabled "$mod_name"; then
                    print_status "$mod_name (enabled)"
                else
                    print_disabled "$mod_name (disabled)"
                fi
                
                # Show mod.conf description if available
                if [[ -f "$mod/mod.conf" ]]; then
                    description=$(grep "^description" "$mod/mod.conf" 2>/dev/null | cut -d'=' -f2- | sed 's/^ *//g')
                    if [[ -n "$description" ]]; then
                        echo "    └─ $description"
                    fi
                fi
            fi
        done
    else
        echo "No server mods directory found"
    fi
    echo
}

# List available local mods
list_local_mods() {
    print_header "Available Local Mods (${LOCAL_MODS_DIR})"
    
    if [[ -d "$LOCAL_MODS_DIR" ]]; then
        for item in "$LOCAL_MODS_DIR"/*; do
            if [[ -d "$item" ]] && [[ -f "$item/init.lua" || -f "$item/mod.conf" ]]; then
                mod_name=$(basename "$item")
                
                # Check if already on server
                if [[ -d "$SERVER_MODS_DIR/$mod_name" ]]; then
                    echo -e "${YELLOW}○${NC} $mod_name (already on server)"
                else
                    echo -e "○ $mod_name"
                fi
                
                # Show mod.conf description if available
                if [[ -f "$item/mod.conf" ]]; then
                    description=$(grep "^description" "$item/mod.conf" 2>/dev/null | cut -d'=' -f2- | sed 's/^ *//g')
                    if [[ -n "$description" ]]; then
                        echo "    └─ $description"
                    fi
                fi
            fi
        done
    else
        echo "No local mods directory found"
    fi
    echo
}

# Show server status
show_server_status() {
    print_header "Server Status"
    
    if systemctl is-active --quiet minetest-server; then
        print_status "Minetest server is running"
        echo
        echo "Server details:"
        systemctl status minetest-server --no-pager | head -n 5
    else
        print_disabled "Minetest server is not running"
    fi
    echo
}

# Main execution
show_server_status
list_server_mods
list_local_mods