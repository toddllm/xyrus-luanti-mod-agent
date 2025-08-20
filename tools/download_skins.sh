#!/bin/bash

# Download skins from Minetest skin database
SKINS_DIR="/var/games/minetest-server/.minetest/mods/skinsdb/textures"

echo "Downloading popular skins..."

# Download a few popular skins with direct URLs
sudo wget -O "$SKINS_DIR/player_cool_guy.png" "https://raw.githubusercontent.com/minetest/minetest_game/master/mods/player_api/textures/character.png" 2>/dev/null

# Create a simple script to fetch from skin database
echo "Fetching skins from database..."

# Download specific skin IDs from the skin database
SKIN_IDS=(1 2 3 10 20 50 100 200)

for id in "${SKIN_IDS[@]}"; do
    echo "Downloading skin ID $id..."
    sudo wget -q -O "$SKINS_DIR/character_$id.png" "http://minetest.fensta.bplaced.net/skins/1/$id.png" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Downloaded skin $id"
    fi
done

# Also download their preview images
for id in "${SKIN_IDS[@]}"; do
    sudo wget -q -O "$SKINS_DIR/character_${id}_preview.png" "http://minetest.fensta.bplaced.net/skins/1/${id}_preview.png" 2>/dev/null
done

# Create metadata files for the skins
for id in "${SKIN_IDS[@]}"; do
    if [ -f "$SKINS_DIR/character_$id.png" ]; then
        echo "name = Skin $id" | sudo tee "$SKINS_DIR/character_$id.txt" > /dev/null
        echo "author = Community" | sudo tee -a "$SKINS_DIR/character_$id.txt" > /dev/null
    fi
done

# Fix permissions
sudo chown -R Debian-minetest:games "$SKINS_DIR"

echo "Done! Restart the server to load new skins."