#!/bin/bash
# find_in_default.sh - Search for features in default mods
# Usage: ./find_in_default.sh <search_term> [game_path]

SEARCH_TERM="$1"
GAME_PATH="${2:-/usr/share/games/minetest/games/minetest_game}"

if [ -z "$SEARCH_TERM" ]; then
    echo "Usage: $0 <search_term> [game_path]"
    echo "Example: $0 sign"
    echo "Example: $0 'register_node.*chest' /path/to/minetest_game"
    exit 1
fi

echo "Searching for '$SEARCH_TERM' in minetest_game..."
echo "Game path: $GAME_PATH"
echo "----------------------------------------"

if [ ! -d "$GAME_PATH" ]; then
    echo "Error: Game path not found: $GAME_PATH"
    echo "Trying alternate locations..."
    
    ALTERNATE_PATHS=(
        "$HOME/.minetest/games/minetest_game"
        "$HOME/.local/share/minetest/games/minetest_game"
        "/usr/local/share/minetest/games/minetest_game"
        "./minetest_game_copy"
    )
    
    for path in "${ALTERNATE_PATHS[@]}"; do
        if [ -d "$path" ]; then
            echo "Found at: $path"
            GAME_PATH="$path"
            break
        fi
    done
    
    if [ ! -d "$GAME_PATH" ]; then
        echo "Could not find minetest_game. Please specify the path."
        exit 1
    fi
fi

# Search with context
grep -r --include="*.lua" -n -B2 -A2 "$SEARCH_TERM" "$GAME_PATH/mods/" 2>/dev/null | head -100

echo "----------------------------------------"
echo "Files containing '$SEARCH_TERM':"
grep -r --include="*.lua" -l "$SEARCH_TERM" "$GAME_PATH/mods/" 2>/dev/null