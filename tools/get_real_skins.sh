#!/bin/bash

SKINS_DIR="/var/games/minetest-server/.minetest/mods/skinsdb/textures"

echo "Downloading real Minetest skins..."

# Download from the actual skinsdb repository
cd /home/tdeshane/luanti

# Clone the u_skins repository which has actual skins
git clone https://github.com/SmallJoker/minetest-u_skins.git temp_skins 2>/dev/null || true

# Copy the actual skin files if they exist
if [ -d "temp_skins/u_skins/textures" ]; then
    echo "Found u_skins textures, copying..."
    sudo cp temp_skins/u_skins/textures/character_*.png "$SKINS_DIR/" 2>/dev/null || true
fi

# Get some skins from MT-Eurythmia skin database
SKIN_URLS=(
    "https://raw.githubusercontent.com/ChaosWormz/mt-skin-db/master/textures/character.Alien.png"
    "https://raw.githubusercontent.com/ChaosWormz/mt-skin-db/master/textures/character.Knight.png"
    "https://raw.githubusercontent.com/ChaosWormz/mt-skin-db/master/textures/character.Builder.png"
    "https://raw.githubusercontent.com/ChaosWormz/mt-skin-db/master/textures/character.Farmer.png"
    "https://raw.githubusercontent.com/ChaosWormz/mt-skin-db/master/textures/character.Warrior.png"
)

SKIN_NAMES=(
    "alien"
    "knight"
    "builder"
    "farmer"
    "warrior"
)

for i in "${!SKIN_URLS[@]}"; do
    url="${SKIN_URLS[$i]}"
    name="${SKIN_NAMES[$i]}"
    echo "Downloading $name skin..."
    sudo wget -q -O "$SKINS_DIR/character_$name.png" "$url" 2>/dev/null
    if [ $? -eq 0 ] && [ -s "$SKINS_DIR/character_$name.png" ]; then
        echo "✓ Downloaded $name skin"
        # Create metadata
        echo "name = ${name^} Skin" | sudo tee "$SKINS_DIR/character_$name.txt" > /dev/null
        echo "author = MT Community" | sudo tee -a "$SKINS_DIR/character_$name.txt" > /dev/null
    else
        sudo rm -f "$SKINS_DIR/character_$name.png" 2>/dev/null
    fi
done

# Clean up
rm -rf temp_skins

# Fix permissions
sudo chown -R Debian-minetest:games "$SKINS_DIR"

echo "Done! Checking downloaded skins..."
ls -la "$SKINS_DIR"/*.png 2>/dev/null | grep -v "^total" | wc -l
echo "skin files found"