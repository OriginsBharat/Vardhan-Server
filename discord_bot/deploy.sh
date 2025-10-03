#!/bin/bash

# This script automates the deployment of the Discord AI Bot World.
# It should be run on a fresh Ubuntu 22.04 server with a GPU.

set -e

echo ">>> [Step 1/7] Updating system packages..."
apt-get update -y
apt-get upgrade -y

echo ">>> [Step 2/7] Installing dependencies (Python, Git, Unzip)..."
apt-get install -y python3-pip git wget unzip

echo ">>> [Step 3/7] Checking for and restoring from backup..."
BACKUP_FILE="/root/world_backup.zip"
if [ -f "$BACKUP_FILE" ]; then
    echo ">>> Backup file found! Restoring your world..."
    unzip $BACKUP_FILE -d /
    echo ">>> Restore complete."
else
    echo ">>> No backup file found. Performing a fresh installation..."
    # This URL is a placeholder. It will be replaced with the actual repo URL.
    git clone https://github.com/your-repo/discord-ai-world.git /opt/discord-ai-world
fi

cd /opt/discord-ai-world/discord_bot

echo ">>> [Step 4/7] Installing Python dependencies for the bot..."
pip3 install -r requirements.txt

echo ">>> [Step 5/7] Installing and configuring Ollama for text generation..."
curl -fsSL https://ollama.com/install.sh | sh
cat <<EOF > /etc/systemd/system/ollama.service
[Unit]
Description=Ollama Service
After=network-online.target
[Service]
ExecStart=/usr/local/bin/ollama serve
User=root
Group=root
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable ollama.service
systemctl start ollama.service
echo ">>> Waiting for Ollama to start..."
sleep 10
source .env
echo ">>> Pulling the AI model (${LLM_MODEL}). This may take a while..."
ollama pull $LLM_MODEL

echo ">>> [Step 6/7] Installing and configuring Stable Diffusion for image generation..."
apt-get install -y python3.10-venv
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git /opt/stable-diffusion-webui || true
cd /opt/stable-diffusion-webui
wget -O /opt/stable-diffusion-webui/models/Stable-diffusion/anything-v5.safetensors https://huggingface.co/stablediffusionapi/anything-v5/resolve/main/anything-v5-PrtRE.safetensors || true
cat <<EOF > /etc/systemd/system/stable-diffusion.service
[Unit]
Description=Stable Diffusion Web UI
After=network-online.target
[Service]
WorkingDirectory=/opt/stable-diffusion-webui
ExecStart=/bin/bash -c 'source venv/bin/activate && python3 launch.py --listen --enable-api'
User=root
Group=root
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF
systemctl enable stable-diffusion.service
systemctl start stable-diffusion.service

echo ">>> [Step 7/7] Setting up the Discord bot to run as a 24/7 service..."
cat <<EOF > /etc/systemd/system/discord-bot.service
[Unit]
Description=Discord AI Bot World
After=ollama.service stable-diffusion.service
[Service]
WorkingDirectory=/opt/discord-ai-world/discord_bot
ExecStart=/usr/bin/python3 main.py
User=root
Group=root
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF
systemctl enable discord-bot.service
systemctl start discord-bot.service

echo ">>> DEPLOYMENT COMPLETE! Your AI bots should now be online in your Discord server."
echo ">>> You can check the status of the services by running:"
echo ">>> systemctl status ollama"
echo ">>> systemctl status stable-diffusion"
echo ">>> systemctl status discord-bot"