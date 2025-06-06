#!/bin/bash

set -e

echo "Building TwinaOS Live System..."

# Clean any previous build
sudo lb clean

# Configure the build
sudo lb config

# Build the ISO
sudo lb build

echo "Build completed! ISO should be in the current directory."
echo "Look for files like: live-image-amd64.hybrid.iso"
