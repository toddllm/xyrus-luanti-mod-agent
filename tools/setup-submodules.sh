#!/bin/bash
# Setup script for adding git submodules to toddllm-luanti mono repo

echo "Setting up git submodules for toddllm-luanti..."

# Move existing directories temporarily
echo "Moving existing directories..."
[ -d "petz-fork" ] && mv petz-fork mods/petz-fork-temp
[ -d "devkorth_mod" ] && mv devkorth_mod mods/devkorth_mod-temp
[ -d "simple_skins" ] && mv simple_skins mods/simple_skins-temp
[ -d "unified_inventory" ] && mv unified_inventory mods/unified_inventory-temp
[ -d "nullifier_adventure" ] && mv nullifier_adventure mods/nullifier_adventure-temp

# Add submodules
echo "Adding petz-fork as submodule..."
git submodule add git@github.com:toddllm/petz.git mods/petz-fork

echo "Adding upstream mods as submodules (for reference)..."
git submodule add https://codeberg.org/TenPlus1/simple_skins.git mods/simple_skins
git submodule add https://github.com/minetest-mods/unified_inventory.git mods/unified_inventory

echo "For devkorth_mod and nullifier_adventure:"
echo "1. Create repositories on GitHub first"
echo "2. Then run:"
echo "   git submodule add <repository-url> mods/devkorth_mod"
echo "   git submodule add <repository-url> mods/nullifier_adventure"

echo ""
echo "To restore your local changes after adding submodules:"
echo "1. Copy your local modifications from mods/*-temp directories"
echo "2. Commit changes to the respective submodules"
echo "3. Remove the -temp directories"

echo "Done!"