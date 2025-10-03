#!/bin/bash
echo "Setting up AI World Environment..."
pip3 install -r requirements.txt
echo "--------------------------------------------------"
echo "Installing Ollama and making it a background service..."
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
sleep 10
ollama pull llama3:latest
echo "--------------------------------------------------"
echo "Downloading Stable Diffusion WebUI..."
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
echo "To run Stable Diffusion automatically, creating a systemd service is recommended."
echo "For now, please run it manually in its own terminal: ./webui.sh --listen --enable-api"
echo "--------------------------------------------------"
echo "Installing FFmpeg for voice chat..."
echo "On Debian/Ubuntu: sudo apt-get install ffmpeg"
echo "On Fedora/CentOS: sudo dnf install ffmpeg"
echo "On MacOS (with Homebrew): brew install ffmpeg"
echo "--------------------------------------------------"
echo "Setup complete. To run the bot, type: python3 main.py"