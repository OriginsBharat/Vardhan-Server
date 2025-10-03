#!/bin/bash

# This script creates a backup of the entire AI World.
# Run this on your old server before the trial expires.

echo ">>> Creating world backup..."

# Define the directory where the application is installed
APP_DIR="/opt/discord-ai-world"
BACKUP_FILE="world_backup.zip"

# Check if the application directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Application directory not found at $APP_DIR"
    exit 1
fi

# Go to the parent directory to make zipping easier
cd /opt

# Create a zip archive of the application directory
# This will include the bot code, conversation history, and deployment date.
zip -r $BACKUP_FILE discord-ai-world

echo ">>> Backup complete!"
echo ">>> Your world has been saved to /opt/$BACKUP_FILE"
echo ">>> Please download this file to your local computer now."
echo ">>> You can use a tool like scp or an SFTP client (like FileZilla)."
echo ">>> Example scp command: scp root@your_server_ip:/opt/world_backup.zip ."