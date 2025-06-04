# TwinaOS Live Installer - Buildroot Configuration

This configuration creates a Linux Live Installer for TwinaOS using Buildroot.

## Features

- **Kiosk Mode**: Automatically launches Cage (Wayland kiosk compositor)
- **No Kernel Messages**: Configured with quiet boot and minimal logging
- **Auto-login**: Automatically logs in as root for kiosk operation
- **Wayland Support**: Uses Wayland with Cage compositor for single-app display
- **EFI Support**: Boots on modern UEFI systems
- **Network Support**: Includes WiFi and Ethernet connectivity

## Target Architecture

- x86_64 (64-bit Intel/AMD processors)
- UEFI boot support
- 512MB root filesystem

## Building TwinaOS

1. **Initialize Configuration**:
   ```bash
   cd buildroot
   make twinaos_defconfig
   ```

2. **Optional: Customize Configuration**:
   ```bash
   make menuconfig
   ```

3. **Build the System**:
   ```bash
   make
   ```

4. **Output**: The final image will be in `output/images/twinaos.img`

## Boot Process

1. GRUB2 bootloader loads with 1-second timeout
2. Linux kernel boots with minimal messages (quiet loglevel=1)
3. Systemd starts and auto-logs in as root
4. TwinaOS service starts Cage compositor
5. Cage launches the default application (weston-terminal for demo)

## Customization

### Adding Your Application

Replace the demo application in `board/twinaos/post-build.sh`:

```bash
# Replace this line in the twinaos-start script:
exec /usr/bin/cage -- /usr/bin/weston-terminal

# With your application:
exec /usr/bin/cage -- /usr/bin/your-app
```

### User Management

**Current Setup**: Auto-login as root (suitable for kiosk)

**Alternative**: Create a dedicated user:
1. Remove auto-login configuration from post-build.sh
2. Add user creation commands
3. Configure auto-login for the new user

For a kiosk environment, using root is often acceptable as:
- Simplifies permissions
- Reduces complexity
- System is typically single-purpose
- Physical access is usually controlled

### Network Configuration

The system includes:
- ConnMan for network management
- WiFi support with common drivers
- Ethernet support

## File Structure

```
board/twinaos/
├── genimage-efi.cfg     # Disk image configuration
├── grub-bios.cfg        # GRUB configuration for BIOS
├── grub-efi.cfg         # GRUB configuration for EFI
├── linux.config         # Linux kernel configuration
├── post-build.sh        # Post-build customization script
├── post-image-efi.sh    # Image creation script
└── readme.txt           # This file
```

## Security Considerations

- Root auto-login: Acceptable for kiosk but consider creating a dedicated user for production
- Network services: Review and disable unnecessary services
- Physical security: Ensure physical access to the device is controlled

## Troubleshooting

### Build Issues
- Ensure you have required host dependencies
- Check Buildroot documentation for host requirements
- Verify disk space (builds can require several GB)

### Boot Issues
- Check UEFI/BIOS settings
- Verify the image was written correctly to USB/disk
- Use serial console for debugging if available

### Application Issues
- Check systemd journal: `journalctl -u twinaos`
- Verify Wayland environment variables
- Test application manually: `/usr/bin/twinaos-start`
