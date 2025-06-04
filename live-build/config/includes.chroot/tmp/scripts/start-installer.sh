#!/bin/bash

# TwinaOS Installer Startup Script
# This script starts the installer backend and opens the browser

set -e

INSTALLER_DIR="/opt/twinaos"
LOG_FILE="/tmp/twinaos-installer.log"

echo "Starting TwinaOS Installer..." | tee $LOG_FILE

# Wait for network to be ready
echo "Waiting for network..." | tee -a $LOG_FILE
for i in {1..30}; do
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        echo "Network is ready" | tee -a $LOG_FILE
        break
    fi
    sleep 1
done

# Start the backend API
echo "Starting installer backend..." | tee -a $LOG_FILE
cd $INSTALLER_DIR/installer-backend
python3 app.py &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..." | tee -a $LOG_FILE
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
        echo "Backend is ready" | tee -a $LOG_FILE
        break
    fi
    sleep 1
done

# Start X server if not already running
if ! pgrep -x "Xorg" > /dev/null; then
    echo "Starting X server..." | tee -a $LOG_FILE
    startx /opt/twinaos/scripts/start-browser.sh &
else
    echo "X server already running, starting browser..." | tee -a $LOG_FILE
    /opt/twinaos/scripts/start-browser.sh &
fi

# Keep the script running
wait $BACKEND_PID
