#!/bin/bash

# My AI World v4 - Migration Script
# This script bundles all persistent data into a single archive for easy migration.

print_header() {
    echo "================================================="
    echo "  $1"
    echo "================================================="
}

print_header "My AI World v4 - Data Migration"

# --- Define Directories and Files to Bundle ---
DATA_DIR="data"
ART_DIR="art_gallery"
ENV_FILE=".env" # Include the secrets file for convenience
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BUNDLE_NAME="migration_bundle_${TIMESTAMP}.zip"

echo "This script will create a migration bundle containing all of your world's persistent data."
echo

# --- Check for Essential Data ---
if [ ! -d "$DATA_DIR" ]; then
    echo "ERROR: The '$DATA_DIR' directory does not exist. Cannot create migration bundle."
    echo "Has the world been run at least once?"
    exit 1
fi

echo "The following will be bundled into '${BUNDLE_NAME}':"
echo " - Directory: $DATA_DIR (Contains databases and character data)"
echo " - Directory: $ART_DIR (Contains all generated artwork)"
echo " - File:      $ENV_FILE (Your configuration secrets)"
echo

read -p "Do you wish to proceed? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Migration cancelled."
    exit 0
fi
echo

# --- Create the Bundle ---
echo "Creating migration bundle..."

# Using zip to create the bundle.
# The '-r' flag is for recursive zipping of directories.
zip -r "$BUNDLE_NAME" "$DATA_DIR" "$ART_DIR" "$ENV_FILE" -x "*.log"
# The -x "*.log" excludes log files from the bundle to keep it lean.

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create the zip bundle. Make sure the 'zip' command is installed."
    exit 1
fi

echo
print_header "Migration Bundle Created Successfully!"
echo "Your bundle is named: ${BUNDLE_NAME}"
echo
echo "You can now download this file (e.g., using scp or sftp) and transfer it to your new server."
echo "On the new server, place it in the project directory and unzip it ('unzip ${BUNDLE_NAME}') BEFORE running the setup.sh script."