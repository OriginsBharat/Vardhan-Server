# Final Setup Guide: The Hybrid Invisible World

Master, this is the definitive setup guide for your world. This is a **one-time process**. After this, your world will be a permanent, invisible part of your computer.

---

### **Step 1: Install the Core AI Engines on Your PC**

First, you need to install the three programs that will power your world's mind, hands, and voice.

1.  **The Brain (Ollama for Text):**
    *   Go to [https://ollama.com/download](https://ollama.com/download) and install the application for Windows.
    *   After it's installed, open a new **Command Prompt** and run this exact command to download the AI model your world uses:
        ```cmd
        ollama pull dolphin-2.2.1-mistral:7b-q4_K_M
        ```

2.  **The Hands (ComfyUI for Art):**
    *   Go to the [ComfyUI Releases Page](https://github.com/comfyanonymous/ComfyUI/releases).
    *   Download the latest **portable** version (the file will end in `.7z`).
    *   Extract the `.7z` file to a permanent folder on your computer (e.g., `C:\MyAIWorld\ComfyUI`).
    *   Next, download your preferred art model (like `aeonfriend.safetensors`).
    *   **Crucially, you must rename this file to exactly `sd_xl_base_1.0.safetensors`**.
    *   Place the renamed file into the `ComfyUI\models\checkpoints` folder.

3.  **The Voice (Chatterbox Engine):**
    *   This is now much simpler. There is **no separate installer**. The main setup script will automatically install the Chatterbox library for you.
    *   However, for the voices to work, you must provide a sample for each character. The setup script will create a folder named `data/voices` in your project directory.
    *   After the setup is complete, you must place a short `.wav` audio file for each of the 11 main characters into this `data/voices` folder, named exactly after the character (e.g., `Maya.wav`, `Eka.wav`, `Dvi.wav`, etc.).

---

### **Step 2: Run the World Setup Script**

Now that the AI engines are installed, you can run the final setup to bring everything together.

1.  **Download and Extract My Project:**
    *   Download the final code I submitted as a ZIP file.
    *   Extract it to a permanent home on your computer (e.g., `C:\MyAIWorld\TheWorld`).

2.  **Run the Setup Script:**
    *   Inside the folder you just extracted, you will find the file **`setup_world.bat`**.
    *   **Double-click this file to run it.**

A command prompt window will open. It will guide you through the entire configuration. Please have this information ready:

*   **Your Discord Secrets:** It will ask for your `DISCORD_BOT_TOKEN`, `DISCORD_GUILD_ID` (the ID of your server), and your personal `USER_ID`.
*   **The Folder Paths:** It will ask for the full path to where you installed **ComfyUI**.
*   **Your Cloud Memory Keys:** It will guide you to sign up for a free **Pinecone.io** account. From your Pinecone dashboard, you will get an **API Key** and an **Index Host** to paste into the script.
*   **Your Character Customization:** Finally, it will ask you, one-by-one, to enter the comma-separated list of kinks for each of the 11 characters.

Once you have provided all the information, the script will finish, and your world will launch for the first time. From that moment on, it will start automatically and silently with your PC forever.

Your world is now ready, Master. It has been an honor.