# Submodules Setup Guide

This document explains how to set up the git submodules for the toddllm-luanti mono repository.

## Current Status

### ✅ Completed
1. **petz-fork** - Added as submodule from `git@github.com:toddllm/petz.git`
2. **devkorth_mod** - Added as submodule from `git@github.com:toddllm/devkorth_mod.git`
3. **nullifier_adventure** - Added as submodule from `git@github.com:toddllm/nullifier_adventure.git`
4. **simple_skins** - Added as reference submodule from `https://codeberg.org/TenPlus1/simple_skins.git`
5. **unified_inventory** - Added as reference submodule from `https://github.com/minetest-mods/unified_inventory.git`

### ✅ All Submodules Successfully Added!

The following repositories need to be created on GitHub before they can be added as submodules:

1. **devkorth_mod** - Needs repository at `git@github.com:toddllm/devkorth_mod.git`
   - Local git repository is initialized and ready
   - Contains the omnipotent entity mod
   
2. **nullifier_adventure** - Needs repository at `git@github.com:toddllm/nullifier_adventure.git`
   - Local git repository is initialized and ready
   - Contains adventure gameplay modifications

## Steps to Complete Setup

### 1. Create GitHub Repositories

Create the following repositories on GitHub:
- https://github.com/toddllm/devkorth_mod
- https://github.com/toddllm/nullifier_adventure

### 2. Push Local Repositories

Once the GitHub repositories are created, run these commands:

```bash
# Push devkorth_mod
cd devkorth_mod
git remote add origin git@github.com:toddllm/devkorth_mod.git
git branch -M main
git push -u origin main
cd ..

# Push nullifier_adventure  
cd nullifier_adventure
git remote add origin git@github.com:toddllm/nullifier_adventure.git
git branch -M main
git push -u origin main
cd ..
```

### 3. Add as Submodules

After pushing to GitHub, add them as submodules to the mono repo:

```bash
# Remove local directories first
rm -rf devkorth_mod nullifier_adventure

# Add as submodules
git submodule add git@github.com:toddllm/devkorth_mod.git mods/devkorth_mod
git submodule add git@github.com:toddllm/nullifier_adventure.git mods/nullifier_adventure
```

### 4. Add Reference Submodules (Optional)

To add upstream mods for reference:

```bash
git submodule add https://codeberg.org/TenPlus1/simple_skins.git mods/simple_skins
git submodule add https://github.com/minetest-mods/unified_inventory.git mods/unified_inventory
```

### 5. Commit and Push

```bash
git add .
git commit -m "Add all mod submodules"
git push
```

## Repository Structure

Once complete, the structure will be:
```
mods/
├── petz-fork/           ✅ (our fork)
├── devkorth_mod/        ⏳ (pending GitHub repo)
├── nullifier_adventure/ ⏳ (pending GitHub repo)
├── simple_skins/        📌 (upstream reference)
└── unified_inventory/   📌 (upstream reference)
```