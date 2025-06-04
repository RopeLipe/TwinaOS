#!/usr/bin/env python3
"""
TwinaOS Installer Backend API
A simple Flask API for handling system installation
"""

import os
import json
import subprocess
import threading
import time
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import psutil

app = Flask(__name__)
CORS(app)

# Development mode check
DEV_MODE = os.environ.get('TWINAOS_DEV_MODE', '0') == '1'

if DEV_MODE:
    print("🔧 Running in development mode")
    # Serve static files in dev mode
    @app.route('/')
    def serve_index():
        return send_from_directory('../installer-ui', 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('../installer-ui', path)

# Global variables for installation tracking
installation_progress = 0
installation_status = "Ready"
installation_log = []
installation_active = False

def log_message(message):
    """Add a message to the installation log"""
    global installation_log
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    installation_log.append(log_entry)
    print(log_entry)  # Also print to console

@app.route('/api/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "service": "TwinaOS Installer API"})

@app.route('/api/disks')
def get_disks():
    """Get available disk drives"""
    try:
        disks = []
        
        if DEV_MODE:
            # Mock data for development
            disks = [
                {
                    'device': '/dev/sda',
                    'model': 'Samsung SSD 970 EVO',
                    'size': 500000000000  # 500GB
                },
                {
                    'device': '/dev/sdb', 
                    'model': 'WD Blue HDD',
                    'size': 1000000000000  # 1TB
                }
            ]
        else:
            # Production code for real disk detection
            partitions = psutil.disk_partitions()
            
            # Get all block devices
            result = subprocess.run(['lsblk', '-J', '-o', 'NAME,SIZE,MODEL,TYPE'], 
                                  capture_output=True, text=True, check=True)
            lsblk_data = json.loads(result.stdout)
            
            for device in lsblk_data['blockdevices']:
                if device['type'] == 'disk':
                    size_bytes = parse_size(device['size'])
                    disks.append({
                        'device': f"/dev/{device['name']}",
                        'model': device.get('model', 'Unknown'),
                        'size': size_bytes
                    })
        
        return jsonify(disks)
    
    except Exception as e:
        log_message(f"Error getting disks: {str(e)}")
        return jsonify({"error": "Failed to get disk information"}), 500

@app.route('/api/install', methods=['POST'])
def start_installation():
    """Start the installation process"""
    global installation_active, installation_progress, installation_status
    
    if installation_active:
        return jsonify({"error": "Installation already in progress"}), 400
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['language', 'timezone', 'disk', 'username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Start installation in a separate thread
        installation_thread = threading.Thread(
            target=run_installation, 
            args=(data,)
        )
        installation_thread.daemon = True
        installation_thread.start()
        
        return jsonify({"status": "Installation started"})
    
    except Exception as e:
        log_message(f"Error starting installation: {str(e)}")
        return jsonify({"error": "Failed to start installation"}), 500

@app.route('/api/install/progress')
def installation_progress_stream():
    """Server-sent events endpoint for installation progress"""
    def generate():
        global installation_active, installation_progress, installation_status, installation_log
        
        while installation_active or installation_progress < 100:
            # Send current status
            data = {
                "progress": installation_progress,
                "status": installation_status,
                "message": installation_log[-1] if installation_log else "Starting..."
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)
        
        # Send final completion message
        final_data = {
            "progress": 100,
            "status": "Installation complete",
            "message": "TwinaOS installation finished successfully!"
        }
        yield f"data: {json.dumps(final_data)}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/reboot', methods=['POST'])
def reboot_system():
    """Reboot the system"""
    try:
        log_message("Rebooting system...")
        subprocess.Popen(['sudo', 'reboot'])
        return jsonify({"status": "Reboot initiated"})
    except Exception as e:
        log_message(f"Error rebooting: {str(e)}")
        return jsonify({"error": "Failed to reboot"}), 500

def run_installation(config):
    """Main installation function"""
    global installation_active, installation_progress, installation_status
    
    installation_active = True
    installation_progress = 0
    
    try:
        if DEV_MODE:
            # Mock installation for development
            log_message("🔧 Development mode - simulating installation")
            
            steps = [
                ("Preparing disk...", 20),
                ("Installing base system...", 60), 
                ("Configuring system...", 80),
                ("Installing bootloader...", 95),
                ("Finalizing installation...", 100)
            ]
            
            for step_name, progress in steps:
                installation_status = step_name
                log_message(step_name)
                installation_progress = progress
                time.sleep(2)  # Simulate work
                
        else:
            # Real installation process
            # Step 1: Prepare disk
            installation_status = "Preparing disk..."
            log_message(f"Starting installation on {config['disk']}")
            prepare_disk(config['disk'])
            installation_progress = 20
            
            # Step 2: Install base system
            installation_status = "Installing base system..."
            log_message("Installing Debian base system...")
            install_base_system(config)
            installation_progress = 60
            
            # Step 3: Configure system
            installation_status = "Configuring system..."
            log_message("Configuring system settings...")
            configure_system(config)
            installation_progress = 80
            
            # Step 4: Install bootloader
            installation_status = "Installing bootloader..."
            log_message("Installing GRUB bootloader...")
            install_bootloader(config['disk'])
            installation_progress = 95
            
            # Step 5: Final cleanup
            installation_status = "Finalizing installation..."
            log_message("Cleaning up and finalizing...")
            finalize_installation()
            installation_progress = 100
        
        installation_status = "Installation complete!"
        log_message("TwinaOS installation completed successfully!")
        
    except Exception as e:
        installation_status = f"Installation failed: {str(e)}"
        log_message(f"ERROR: {str(e)}")
    finally:
        installation_active = False

def prepare_disk(disk):
    """Prepare the target disk for installation"""
    log_message(f"Partitioning disk {disk}")
    
    # Create partition table and partitions
    commands = [
        f"parted -s {disk} mklabel gpt",
        f"parted -s {disk} mkpart primary fat32 1MiB 513MiB",
        f"parted -s {disk} set 1 esp on",
        f"parted -s {disk} mkpart primary ext4 513MiB 100%"
    ]
    
    for cmd in commands:
        subprocess.run(cmd.split(), check=True)
    
    # Format partitions
    log_message("Formatting partitions...")
    subprocess.run([f"mkfs.fat", "-F32", f"{disk}1"], check=True)
    subprocess.run([f"mkfs.ext4", "-F", f"{disk}2"], check=True)

def install_base_system(config):
    """Install Debian base system using debootstrap"""
    mount_point = "/mnt/twinaos"
    
    # Create mount point and mount partitions
    os.makedirs(mount_point, exist_ok=True)
    subprocess.run(["mount", f"{config['disk']}2", mount_point], check=True)
    os.makedirs(f"{mount_point}/boot/efi", exist_ok=True)
    subprocess.run(["mount", f"{config['disk']}1", f"{mount_point}/boot/efi"], check=True)
    
    # Run debootstrap
    log_message("Running debootstrap (this may take several minutes)...")
    subprocess.run([
        "debootstrap", "--arch=amd64", "--variant=minbase",
        "bookworm", mount_point, "http://deb.debian.org/debian/"
    ], check=True)

def configure_system(config):
    """Configure the installed system"""
    mount_point = "/mnt/twinaos"
    
    # Generate fstab
    log_message("Generating fstab...")
    with open(f"{mount_point}/etc/fstab", "w") as f:
        # Get UUIDs for partitions
        root_uuid = subprocess.check_output([
            "blkid", "-s", "UUID", "-o", "value", f"{config['disk']}2"
        ]).decode().strip()
        boot_uuid = subprocess.check_output([
            "blkid", "-s", "UUID", "-o", "value", f"{config['disk']}1"
        ]).decode().strip()
        
        f.write(f"UUID={root_uuid} / ext4 defaults 0 1\n")
        f.write(f"UUID={boot_uuid} /boot/efi vfat defaults 0 2\n")
    
    # Set hostname
    with open(f"{mount_point}/etc/hostname", "w") as f:
        f.write("twinaos\n")
    
    # Configure user
    log_message(f"Creating user {config['username']}...")
    chroot_command([
        "useradd", "-m", "-s", "/bin/bash", "-G", "sudo", config['username']
    ], mount_point)
    
    # Set passwords (this is simplified - in production, use proper hashing)
    chroot_command([
        "bash", "-c", f"echo '{config['username']}:{config['password']}' | chpasswd"
    ], mount_point)
    
    # Set timezone
    chroot_command([
        "ln", "-sf", f"/usr/share/zoneinfo/{config['timezone']}", "/etc/localtime"
    ], mount_point)

def install_bootloader(disk):
    """Install GRUB bootloader"""
    mount_point = "/mnt/twinaos"
    
    # Install GRUB packages in chroot
    chroot_command(["apt", "update"], mount_point)
    chroot_command(["apt", "install", "-y", "grub-efi-amd64", "linux-image-amd64"], mount_point)
    
    # Install GRUB to disk
    chroot_command(["grub-install", "--target=x86_64-efi", f"--efi-directory=/boot/efi", disk], mount_point)
    chroot_command(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], mount_point)

def finalize_installation():
    """Clean up and unmount filesystems"""
    mount_point = "/mnt/twinaos"
    
    # Unmount filesystems
    subprocess.run(["umount", f"{mount_point}/boot/efi"], check=False)
    subprocess.run(["umount", mount_point], check=False)
    
    log_message("Installation completed successfully!")

def chroot_command(command, mount_point):
    """Execute a command in chroot environment"""
    full_command = ["chroot", mount_point] + command
    subprocess.run(full_command, check=True)

def parse_size(size_str):
    """Parse size string like '100G' to bytes"""
    units = {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
    size_str = size_str.strip().upper()
    
    if size_str[-1] in units:
        return int(float(size_str[:-1]) * units[size_str[-1]])
    else:
        return int(size_str)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
