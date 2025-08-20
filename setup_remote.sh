#!/bin/bash

# Setup Remote Repository for Xyrus
# Usage: ./setup_remote.sh <repository-url>

if [ -z "$1" ]; then
    echo "Usage: ./setup_remote.sh <repository-url>"
    echo "Example: ./setup_remote.sh https://github.com/username/xyrus.git"
    echo "         ./setup_remote.sh git@github.com:username/xyrus.git"
    exit 1
fi

REPO_URL=$1

echo "Adding remote repository: $REPO_URL"
git remote add origin "$REPO_URL"

echo "Verifying remote..."
git remote -v

echo ""
echo "Remote added successfully!"
echo "To push your code, run:"
echo "  git push -u origin main"
echo ""
echo "Current status:"
git status --short
echo ""
echo "Recent commits:"
git log --oneline -5