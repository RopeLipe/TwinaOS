#!/bin/sh

set -e

BOARD_DIR=$(dirname "$0")

echo "TwinaOS: Setting up kiosk environment..."

# Detect boot strategy, EFI or BIOS
if [ -d "$BINARIES_DIR/efi-part/" ]; then
    cp -f "$BOARD_DIR/grub-efi.cfg" "$BINARIES_DIR/efi-part/EFI/BOOT/grub.cfg"
else
    cp -f "$BOARD_DIR/grub-bios.cfg" "$TARGET_DIR/boot/grub/grub.cfg"
    # Copy grub 1st stage to binaries, required for genimage
    cp -f "$TARGET_DIR/lib/grub/i386-pc/boot.img" "$BINARIES_DIR"
fi

# Create TwinaOS kiosk user directory structure
mkdir -p "$TARGET_DIR/etc/systemd/system"
mkdir -p "$TARGET_DIR/etc/cage"

# Set up auto-login for root user (kiosk mode)
mkdir -p "$TARGET_DIR/etc/systemd/system/getty@tty1.service.d"
cat > "$TARGET_DIR/etc/systemd/system/getty@tty1.service.d/override.conf" << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin root --noclear %I linux
EOF

# Create TwinaOS startup script
cat > "$TARGET_DIR/usr/bin/twinaos-start" << 'EOF'
#!/bin/sh

# Set environment for Wayland
export XDG_RUNTIME_DIR=/tmp
export WAYLAND_DISPLAY=wayland-0

# Start cage with a simple application (can be replaced with your TwinaOS app)
exec /usr/bin/cage -- /usr/bin/weston-terminal
EOF

chmod +x "$TARGET_DIR/usr/bin/twinaos-start"

# Create systemd service for TwinaOS
cat > "$TARGET_DIR/etc/systemd/system/twinaos.service" << 'EOF'
[Unit]
Description=TwinaOS Kiosk
After=systemd-user-sessions.service getty@tty1.service
Wants=systemd-user-sessions.service

[Service]
User=root
Group=root
Environment=XDG_RUNTIME_DIR=/tmp
Environment=WAYLAND_DISPLAY=wayland-0
ExecStart=/usr/bin/twinaos-start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable TwinaOS service
ln -sf /etc/systemd/system/twinaos.service "$TARGET_DIR/etc/systemd/system/multi-user.target.wants/twinaos.service"

# Disable unnecessary services for kiosk
rm -f "$TARGET_DIR/etc/systemd/system/multi-user.target.wants/connman.service"

echo "TwinaOS: Kiosk setup complete"
