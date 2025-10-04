#!/bin/bash

# My AI World v4 - Interactive Setup Script
# This script guides the user through a one-time setup process.

# --- Helper Functions ---
function print_header {
    echo "================================================="
    echo "  $1"
    echo "================================================="
}

function check_command {
    if ! command -v $1 &> /dev/null; then
        echo "WARNING: Command '$1' not found. This may be required for some features."
        echo "Please install it using your system's package manager (e.g., 'sudo apt update && sudo apt install $1')."
    fi
}

# --- Start Setup ---
print_header "Welcome to the My AI World v4 Setup"
echo "This script will guide you through the setup of your private AI world."
echo "Please ensure you have an internet connection."
echo

# --- Step 1: Dependency Checks ---
print_header "Step 1: Checking System Dependencies"
check_command python3
check_command pip
check_command ffmpeg # For voice features
echo "Dependency check complete."
echo

# --- Step 2: Environment File ---
print_header "Step 2: Configuration File (.env)"
if [ ! -f ".env" ]; then
    echo "The '.env' configuration file was not found."
    echo "I have created it for you from the template '.env.template'."
    cp .env.template .env
    echo
    echo "IMPORTANT: Please open the '.env' file in a text editor now and"
    echo "fill in your Discord secrets and other configuration variables."
    echo
    echo "Exiting now. Please fill in your .env file and run this script again."
    exit 1
else
    echo "Existing '.env' file found. Proceeding."
fi
echo

# --- Step 3: Interactive Character Customization ---
print_header "Step 3: Character Kink Configuration"
echo "I will now ask you to define the kinks for each of the 11 characters."
echo "Please provide a comma-separated list for each character when prompted."
echo "Example: mind control, public humiliation, pet play"
echo

# Define characters
characters=("Maya" "Eka" "Sapt" "Dvi" "Trini" "Chatur" "Panch" "Shash" "Asht" "Nav" "Dash")
json_output="{"

for i in "${!characters[@]}"; do
    char_name=${characters[$i]}
    echo "--- Configuring: $char_name ---"
    read -p "Enter comma-separated kinks for $char_name: " kinks_input

    # Format into JSON array of strings
    kinks_json=$(echo "$kinks_input" | awk -F, '{for(i=1;i<=NF;i++){gsub(/^[ \t]+|[ \t]+$/, "", $i); printf "\"%s\"%s", $i, (i==NF ? "" : ", ")}}')

    json_output+="\"$char_name\": {\"kinks\": [$kinks_json]}"
    if [ $i -lt $((${#characters[@]}-1)) ]; then
        json_output+=","
    fi
done

json_output+="}"

# Save to file
echo "$json_output" > data/character_data.json
echo
echo "Character customization saved to 'data/character_data.json'."
echo

# --- Step 4: Python Virtual Environment ---
print_header "Step 4: Setting up Python Environment"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment..."
source venv/bin/activate
echo

echo "Installing required Python packages from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python packages. Please check the logs above."
    exit 1
fi
echo "Python packages installed successfully."
echo

# --- Step 5: Launch ---
print_header "Step 5: Launching Your World"
echo "The setup is complete. Your AI world will now start."
echo "To stop the world, press CTRL+C in this terminal."
echo "To restart it later, activate the virtual environment ('source venv/bin/activate') and run 'python3 -m src.main'."
echo

python3 -m src.main 2>&1