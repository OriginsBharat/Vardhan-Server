# My AI World: Final Setup & Installation Guide

Master, the world is forged and ready. Follow these steps precisely to bring it to life. This is a one-time process.

---

### **Part 1: Prerequisite Software Installation (The AI Engines)**

First, you need to install the three core programs that will power your world's mind, hands, and voice.

#### 1. The Brain (Ollama for Text Generation)
*   **Action:** Go to [https://ollama.com/download](https://ollama.com/download).
*   **Action:** Download and run the installer for Windows. This will set up Ollama to run automatically in your system tray.
*   **Action:** After the installation is complete, open a new **Command Prompt** (search for "cmd" in your Start Menu).
*   **Action:** In the command prompt, type this exact command and press Enter. This will download the specific AI model your world is configured to use. It is a large file and will take some time.
    ```
    ollama pull dolphin-2.2.1-mistral:7b-q4_K_M
    ```

#### 2. The Hands (ComfyUI for Art Generation)
*   **Action:** Go to the [ComfyUI Releases Page](https://github.com/comfyanonymous/ComfyUI/releases).
*   **Action:** Find the latest release and download the file named `ComfyUI_windows_portable_nvidia_cu121_or_cpu.7z`.
*   **Action:** This is a `.7z` file, so you will need a program like 7-Zip or WinRAR to open it. Extract the entire contents to a permanent folder on your computer. For example: `C:\MyAIWorld\ComfyUI`.
*   **Action:** Next, you need an art model. You can use the one you chose, `aeonfriend.safetensors`.
*   **Action (CRITICAL):** You **must** rename the downloaded art model file to exactly this: `sd_xl_base_1.0.safetensors`.
*   **Action:** Place the renamed file into the following folder inside your ComfyUI installation: `ComfyUI\models\checkpoints`.

---

### **Part 2: The "One-Click" World Setup**

Now that the AI engines are installed, you can run the final setup to bring everything together.

**Step 1: Run the Setup Launcher**
*   **Action:** In the project folder, find and double-click the `RUN_SETUP.bat` file.
*   **Action:** A command prompt will appear and install all the necessary Python libraries. When it's done, it will automatically launch the graphical setup wizard for you.

**Step 2: Use the Graphical Setup Wizard**
*   The graphical setup wizard will now be open.
*   **Have this information ready to paste in when it asks:**
    *   **Your Discord Secrets:** `DISCORD_BOT_TOKEN`, `DISCORD_GUILD_ID` (the ID of your server), and your personal `USER_ID`.
    *   **The Folder Path to ComfyUI:** The full path to where you extracted ComfyUI (e.g., `C:\MyAIWorld\ComfyUI`).
    *   **Your Cloud Memory Keys (Pinecone):** The setup will guide you to [https://pinecone.io](https://pinecone.io) to get your free API Key and Index Host.
    *   **Your Character Customization:** Finally, the setup will ask you, one-by-one, to enter the comma-separated list of kinks for each of the 11 characters.
*   **Action:** Click the "Begin World Setup" button and watch as the script finalizes your world.

---

### **Part 3: Creating the Voice Files**

The final step is to provide the voice samples for each character. The setup wizard will have created a `data/voices` folder inside your project directory.

*   **Action:** For each character below, use a "YouTube to WAV converter" website to download a short audio clip from the source link.
*   **Action:** Rename each downloaded `.wav` file to the exact name listed and place it in the `data/voices` folder.

**The Final Voice Cast:**
*   **Eka:** `Eka.wav` (Source: Akeno Himejima)
*   **Dvi:** `Dvi.wav` (Source: Marulk)
*   **Tri:** `Tri.wav` (Source: Rem)
*   **Chatur:** `Chatur.wav` (Source: Ruka Urushibara)
*   **Panch:** `Panch.wav` (Source: Ken Kaneki)
*   **Shash:** `Shash.wav` (Source: Yukinoshita Yukino)
*   **Sapt:** `Sapt.wav` (Source: Yoruichi Shihouin)
*   **Asht:** `Asht.wav` (Source: Howl)
*   **Nav:** `Nav.wav` (Source: Miku Nakano)
*   **Dash:** `Dash.wav` (Source: Juuzou Suzuya)
*   **Maya:** `Maya.wav` (Source: A YouTube video of Tashi's voice).

Once you have placed the voice files, your world is complete. It will now start automatically and silently with your PC forever. It has been an honor, Master.