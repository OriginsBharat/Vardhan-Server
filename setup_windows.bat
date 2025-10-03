@echo off
echo "Setting up AI World Environment..."
pip install -r requirements.txt
echo "--------------------------------------------------"
echo "Please download and install Ollama for Windows from https://ollama.com/download"
echo "After installation, open a new Command Prompt and run: ollama pull llama3:latest"
echo "To make Ollama run automatically, run this in an Administrator Command Prompt:"
echo "sc create Ollama binPath= "\"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe\" serve" start=auto"
echo "--------------------------------------------------"
echo "Please download and set up AUTOMATIC1111's Stable Diffusion WebUI from https://github.com/AUTOMATIC1111/stable-diffusion-webui"
echo "To enable the API, edit your webui-user.bat file and add these to the command-line arguments: --listen --enable-api"
echo "To make it run automatically, place a shortcut to the modified webui-user.bat in your Startup folder."
echo "--------------------------------------------------"
echo "Installing FFmpeg for voice chat..."
echo "Please download FFmpeg from https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"
echo "Extract the archive, and add the 'bin' folder to your system's PATH environment variable."
echo "--------------------------------------------------"
echo "Setup complete. You can now run the bot by executing: python main.py"
pause