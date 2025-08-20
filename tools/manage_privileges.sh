#!/bin/bash

# Luanti/Minetest Privilege Management Script

WORLD_PATH="/var/games/minetest-server/.minetest/worlds/world"
AUTH_DB="$WORLD_PATH/auth.sqlite"

echo "Luanti/Minetest Privilege Manager"
echo "================================="
echo

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# Function to execute SQL commands
run_sql() {
    sudo -u Debian-minetest sqlite3 "$AUTH_DB" "$1"
}

# Function to list all players
list_players() {
    echo "Current players and their privileges:"
    echo
    run_sql "SELECT a.name, GROUP_CONCAT(p.privilege) as privileges 
             FROM auth a 
             LEFT JOIN user_privileges p ON a.id = p.id 
             GROUP BY a.id, a.name;"
}

# Function to grant all privileges to a player
make_admin() {
    local player=$1
    echo "Granting all privileges to $player..."
    
    # Get player ID
    local player_id=$(run_sql "SELECT id FROM auth WHERE name='$player';")
    
    if [ -z "$player_id" ]; then
        echo "Player $player not found!"
        return
    fi
    
    # Standard admin privileges
    local privs=("interact" "shout" "privs" "teleport" "bring" "fast" "fly" "noclip" "creative" "give" "settime" "server" "protection_bypass" "ban" "kick")
    
    # Clear existing privileges
    run_sql "DELETE FROM user_privileges WHERE id=$player_id;"
    
    # Grant all privileges
    for priv in "${privs[@]}"; do
        run_sql "INSERT INTO user_privileges (id, privilege) VALUES ($player_id, '$priv');"
    done
    
    echo "Done! $player now has admin privileges."
}

# Function to grant specific privilege
grant_priv() {
    local player=$1
    local priv=$2
    echo "Granting $priv to $player..."
    
    # Get player ID
    local player_id=$(run_sql "SELECT id FROM auth WHERE name='$player';")
    
    if [ -z "$player_id" ]; then
        echo "Player $player not found!"
        return
    fi
    
    # Check if privilege already exists
    local exists=$(run_sql "SELECT COUNT(*) FROM user_privileges WHERE id=$player_id AND privilege='$priv';")
    
    if [ "$exists" -eq 0 ]; then
        run_sql "INSERT INTO user_privileges (id, privilege) VALUES ($player_id, '$priv');"
        echo "Done!"
    else
        echo "$player already has $priv privilege."
    fi
}

# Main menu
case "$1" in
    list)
        list_players
        ;;
    admin)
        if [ -z "$2" ]; then
            echo "Usage: $0 admin <playername>"
            exit 1
        fi
        make_admin "$2"
        ;;
    grant)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 grant <playername> <privilege>"
            exit 1
        fi
        grant_priv "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {list|admin|grant}"
        echo
        echo "Commands:"
        echo "  list                    - List all players and privileges"
        echo "  admin <player>          - Make player an admin"
        echo "  grant <player> <priv>   - Grant specific privilege"
        echo
        echo "Example:"
        echo "  $0 admin ToddLLM"
        echo "  $0 grant Chelsea creative"
        ;;
esac