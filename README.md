# TwinaOS Live System

A minimal Debian-based live system with Wayland, Cage compositor, and PipeWire.

## Features

- **Minimal Debian base** (Bookworm)
- **Wayland display server** with Cage compositor
- **PipeWire audio system** (replaces PulseAudio/ALSA)
- **Full networking support** (WiFi, Ethernet, Bluetooth)
- **Auto-login as root**
- **Auto-launch Cage compositor** with GTK4 demo application
- **Basic GTK4 application** showing system information

## Building

### Prerequisites

Install live-build on a Debian/Ubuntu system:

```bash
sudo apt update
sudo apt install live-build debootstrap
```

### Build the ISO

```bash
chmod +x build.sh
./build.sh
```

The build process will create an ISO file (typically named `live-image-amd64.hybrid.iso`) that you can write to a USB drive or burn to a DVD.

## Usage

1. Boot from the created ISO
2. System will auto-login as root
3. Cage compositor will start automatically with a GTK4 demo application
4. You'll see a welcome screen with system information
5. The application demonstrates basic GTK4 functionality on Wayland

## Networking

- **Ethernet**: Should work automatically via NetworkManager
- **WiFi**: Use `nmcli` to connect:
  ```bash
  nmcli device wifi list
  nmcli device wifi connect "SSID" password "password"
  ```
- **Bluetooth**: Use `bluetoothctl` for pairing devices

## Audio

PipeWire is configured as the audio system. No additional configuration should be needed.

## Architecture

```
┌─────────────────┐
│   GTK4 Demo App │ ← Welcome screen application
├─────────────────┤
│   Cage (Wayland │ ← Auto-launched via systemd
│   Compositor)   │
├─────────────────┤
│   PipeWire      │ ← Audio system
├─────────────────┤
│   NetworkManager│ ← Network management
├─────────────────┤
│   Bluetooth     │ ← Bluetooth stack
├─────────────────┤
│   Minimal       │ ← Base Debian system
│   Debian Base   │
└─────────────────┘
```

## Files Structure

- `auto/` - Live-build auto scripts
- `config/package-lists/` - Package definitions
- `config/hooks/live/` - Build-time configuration scripts
- `config/includes.chroot/usr/local/src/twinaos-app/` - GTK4 demo application source
- `build.sh` - Main build script

## GTK4 Application

The included demo application shows:
- Welcome screen with TwinaOS branding
- System information display
- Basic GTK4 widgets (labels, buttons, dialogs)
- Proper Wayland integration

Source code is located in `config/includes.chroot/usr/local/src/twinaos-app/` and gets compiled during the build process.

## Customization

To add more packages, edit `config/package-lists/twinaos.list.chroot`.
To modify system configuration, edit `config/hooks/live/0010-twinaos-config.hook.chroot`.
To customize the GTK4 app, edit the source in `config/includes.chroot/usr/local/src/twinaos-app/main.c`.
