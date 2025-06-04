#!/bin/bash

# TwinaOS Live Build Configuration
# This script sets up the live-build environment

set -e

echo "Setting up TwinaOS live build environment..."

# Clean any previous builds
if [ -d "auto" ]; then
    sudo lb clean --purge
fi

# Configure live-build
lb config noauto \
    --mode debian \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --bootloader grub-efi \
    --binary-images iso-hybrid \
    --iso-application "TwinaOS" \
    --iso-publisher "TwinaOS Team" \
    --iso-volume "TwinaOS" \
    --linux-flavours amd64 \
    --linux-packages linux-image \
    --bootappend-live "boot=live components quiet splash" \
    --bootappend-install "quiet splash" \
    --mirror-bootstrap http://deb.debian.org/debian/ \
    --mirror-chroot http://deb.debian.org/debian/ \
    --mirror-binary http://deb.debian.org/debian/ \
    --debootstrap-options "--variant=minbase" \
    --firmware-chroot true \
    --firmware-binary true \
    --updates true \
    --security true \
    --cache-packages true \
    --cache-stages true \
    --clean

echo "Live build configured successfully!"
echo "Run 'sudo lb build' to create the ISO"
