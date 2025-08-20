#!/bin/bash

# Luanti/Minetest Server Control Script
# Usage: ./server_control.sh [start|stop|restart|status|logs]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check if running as root or with sudo
check_permissions() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Server control functions
start_server() {
    print_info "Starting Minetest server..."
    if systemctl is-active --quiet minetest-server; then
        print_warning "Server is already running"
    else
        systemctl start minetest-server
        sleep 2
        if systemctl is-active --quiet minetest-server; then
            print_status "Server started successfully"
        else
            print_error "Failed to start server"
            systemctl status minetest-server --no-pager
        fi
    fi
}

stop_server() {
    print_info "Stopping Minetest server..."
    if ! systemctl is-active --quiet minetest-server; then
        print_warning "Server is already stopped"
    else
        systemctl stop minetest-server
        sleep 2
        if ! systemctl is-active --quiet minetest-server; then
            print_status "Server stopped successfully"
        else
            print_error "Failed to stop server"
        fi
    fi
}

restart_server() {
    print_info "Restarting Minetest server..."
    systemctl restart minetest-server
    sleep 2
    if systemctl is-active --quiet minetest-server; then
        print_status "Server restarted successfully"
    else
        print_error "Failed to restart server"
        systemctl status minetest-server --no-pager
    fi
}

server_status() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Minetest Server Status${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    
    if systemctl is-active --quiet minetest-server; then
        print_status "Server is running"
        echo
        # Show detailed status
        systemctl status minetest-server --no-pager
        
        # Show server info
        echo
        echo -e "${BLUE}Server Information:${NC}"
        echo "Config file: /etc/minetest/minetest.conf"
        echo "Log file: /var/log/minetest/minetest.log"
        echo "World directory: /var/games/minetest-server/.minetest/worlds/world"
        echo "Mods directory: /var/games/minetest-server/.minetest/mods"
        
        # Show active connections if any
        echo
        echo -e "${BLUE}Network:${NC}"
        ss -tulpn | grep :30000 || echo "No active connections on port 30000"
    else
        print_error "Server is not running"
        echo
        echo "Last 10 lines from log:"
        tail -n 10 /var/log/minetest/minetest.log 2>/dev/null || echo "Log file not found"
    fi
}

show_logs() {
    local lines="${2:-50}"
    print_info "Showing last $lines lines of server log..."
    echo
    tail -n "$lines" /var/log/minetest/minetest.log 2>/dev/null || print_error "Log file not found"
}

follow_logs() {
    print_info "Following server logs (Ctrl+C to stop)..."
    echo
    tail -f /var/log/minetest/minetest.log 2>/dev/null || print_error "Log file not found"
}

# Main execution
case "$1" in
    start)
        check_permissions
        start_server
        ;;
    stop)
        check_permissions
        stop_server
        ;;
    restart)
        check_permissions
        restart_server
        ;;
    status)
        server_status
        ;;
    logs)
        show_logs "$@"
        ;;
    logs-follow|follow)
        follow_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|logs-follow}"
        echo
        echo "Commands:"
        echo "  start       - Start the Minetest server"
        echo "  stop        - Stop the Minetest server"
        echo "  restart     - Restart the Minetest server"
        echo "  status      - Show server status and information"
        echo "  logs [n]    - Show last n lines of log (default: 50)"
        echo "  logs-follow - Follow server logs in real-time"
        exit 1
        ;;
esac