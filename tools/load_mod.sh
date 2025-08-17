#!/bin/bash

# Luanti/Minetest Mod Loader Script
# Usage: ./load_mod.sh <mod_name_or_path>

set -e

# Non-interactive controls (can be set via environment)
NONINTERACTIVE=${NONINTERACTIVE:-0}   # 1 to skip prompts
AUTO_RESTART=${AUTO_RESTART:-0}       # 1 to restart automatically after enabling

# Configuration
SERVER_MODS_DIR="/var/games/minetest-server/.minetest/mods"
WORLD_CONFIG="/var/games/minetest-server/.minetest/worlds/world/world.mt"
LOCAL_MODS_DIR="/home/tdeshane/luanti"

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

# Function to load a mod
load_mod() {
    local mod_input="$1"
    local mod_name=""
    local mod_source=""
    
    # Determine if input is a path or just a mod name
    if [[ -d "$mod_input" ]]; then
        # Full path provided
        mod_source="$mod_input"
        mod_name=$(basename "$mod_input")
    elif [[ -d "$LOCAL_MODS_DIR/$mod_input" ]]; then
        # Mod exists in local directory
        mod_source="$LOCAL_MODS_DIR/$mod_input"
        mod_name="$mod_input"
    else
        print_error "Mod not found: $mod_input"
        exit 1
    fi
    
    print_status "Loading mod: $mod_name"
    
    # Check if mod already exists
    if [[ -d "$SERVER_MODS_DIR/$mod_name" ]]; then
        print_warning "Mod $mod_name already exists in server mods directory"
        if [[ "$NONINTERACTIVE" = "1" ]]; then
            rm -rf "$SERVER_MODS_DIR/$mod_name"
            cp -r "$mod_source" "$SERVER_MODS_DIR/"
            chown -R Debian-minetest:games "$SERVER_MODS_DIR/$mod_name"
            print_status "Mod files replaced (non-interactive)"
        else
            read -p "Do you want to replace it? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_status "Skipping mod copy"
            else
                rm -rf "$SERVER_MODS_DIR/$mod_name"
                cp -r "$mod_source" "$SERVER_MODS_DIR/"
                chown -R Debian-minetest:games "$SERVER_MODS_DIR/$mod_name"
                print_status "Mod files replaced"
            fi
        fi
    else
        # Copy mod to server directory
        cp -r "$mod_source" "$SERVER_MODS_DIR/"
        chown -R Debian-minetest:games "$SERVER_MODS_DIR/$mod_name"
        print_status "Mod copied to server directory"
    fi
    
    # Check if mod is already enabled in world.mt
    if grep -q "^load_mod_${mod_name} = true" "$WORLD_CONFIG"; then
        print_warning "Mod $mod_name is already enabled in world configuration"
    else
        # Enable mod in world.mt
        echo "load_mod_${mod_name} = true" >> "$WORLD_CONFIG"
        print_status "Mod enabled in world configuration"
    fi
    
    print_status "Mod $mod_name loaded successfully!"
    print_warning "Server restart required for changes to take effect"
    echo
    if [[ "$AUTO_RESTART" = "1" ]]; then
        systemctl restart minetest-server
        print_status "Server restarted (AUTO_RESTART)"
    elif [[ "$NONINTERACTIVE" = "1" ]]; then
        print_warning "Non-interactive mode: not restarting automatically (set AUTO_RESTART=1 to enable)"
        print_warning "Remember to restart the server later with: sudo systemctl restart minetest-server"
    else
        read -p "Restart server now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            systemctl restart minetest-server
            print_status "Server restarted"
        else
            print_warning "Remember to restart the server later with: sudo systemctl restart minetest-server"
        fi
    fi
}

# Main execution
if [[ $# -eq 0 ]]; then
    print_error "Usage: $0 <mod_name_or_path>"
    echo "Examples:"
    echo "  $0 nullifier_adventure"
    echo "  $0 /path/to/mod_directory"
    exit 1
fi

check_permissions
load_mod "$1"