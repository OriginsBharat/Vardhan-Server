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

### **Part 2: The One-Time World Setup**

Now that the AI engines are installed, you can run the final setup to bring everything together.

1.  **Download and Extract My Project:**
    *   **Action:** Download the final code I submitted to you as a ZIP file.
    *   **Action:** Extract the entire contents of that ZIP file to a permanent home on your computer. For example: `C:\MyAIWorld\TheWorld`.

2.  **Run the Setup Script:**
    *   **Action:** Inside the folder you just extracted, you will find the file `SETUP_THE_WORLD.py`.
    *   **Action:** Double-click `SETUP_THE_WORLD.py` to run it. A command prompt window will open. It will guide you through the entire configuration, step-by-step.
    *   **Have this information ready to paste in when it asks:**
        *   **Your Discord Secrets:** `DISCORD_BOT_TOKEN`, `DISCORD_GUILD_ID` (the ID of your server), and your personal `USER_ID`.
        *   **The Folder Path to ComfyUI:** The full path to where you extracted ComfyUI (e.g., `C:\MyAIWorld\ComfyUI`).
        *   **Your Cloud Memory Keys (Pinecone):** The script will pause and instruct you to go to [https://pinecone.io](https://pinecone.io) and sign up for a free "Starter" account. Once logged in, you will create a new "Index". Use these exact settings:
            *   **Index Name:** `my-ai-world`
            *   **Dimensions:** `768`
            *   **Metric:** `cosine`
            *   After the index is created, click on **"API Keys"** in the left-hand menu. You will see your **API Key** and your **Index Host**. The script will ask you to paste these two values in.
        *   **Your Character Customization:** Finally, the script will ask you, one-by-one, to enter the comma-separated list of kinks for each of the 11 characters.

---

### **Part 3: Creating the Voice Files**

The final step is to provide the voice samples for each character. The setup script will have created a `data/voices` folder inside your project directory.

*   **Action:** For each character below, use a "YouTube to WAV converter" website to download a short audio clip from the source link.
*   **Action:** Rename each downloaded `.wav` file to the exact name listed and place it in the `data/voices` folder.

**The Final Voice Cast:**
*   **Eka:** `Eka.wav` (Source: Akeno Himejima - [https://www.youtube.com/watch?v=DRrbSiLSDEg](https://www.youtube.com/watch?v=DRrbSiLSDEg))
*   **Dvi:** `Dvi.wav` (Source: Marulk - [https://www.youtube.com/watch?v=V83O_sgbBvU](https://www.youtube.com/watch?v=V83O_sgbBvU) at 0:35)
*   **Tri:** `Tri.wav` (Source: Rem - [https://www.youtube.com/watch?v=35Yaz1JwfKI](https://www.youtube.com/watch?v=35Yaz1JwfKI))
*   **Chatur:** `Chatur.wav` (Source: Ruka Urushibara - [https://www.youtube.com/watch?v=zdwR2jiADE0](https://www.youtube.com/watch?v=zdwR2jiADE0))
*   **Panch:** `Panch.wav` (Source: Ken Kaneki - [https://www.youtube.com/watch?v=iT-3M7-dZtM))
*   **Shash:** `Shash.wav` (Source: Yukinoshita Yukino - [https://www.youtube.com/watch?v=c8WymIGk38c](https://www.youtube.com/watch?v=c8WymIGk38c))
*   **Sapt:** `Sapt.wav` (Source: Yoruichi Shihouin - [https://www.youtube.com/watch?v=SevE3RKb4MY](https://www.youtube.com/watch?v=SevE3RKb4MY))
*   **Asht:** `Asht.wav` (Source: Howl - [https://www.youtube.com/watch?v=DJeUGpcle8s](https://www.youtube.com/watch?v=DJeUGpcle8s))
*   **Nav:** `Nav.wav` (Source: Miku Nakano - [https://www.youtube.com/watch?v=jm1pcimai48](https://www.youtube.com/watch?v=jm1pcimai48))
*   **Dash:** `Dash.wav` (Source: Juuzou Suzuya - [https://www.youtube.com/watch?v=eB8r-j2S4JQ](https://www.youtube.com/watch?v=eB8r-j2S4JQ))
*   **Maya:** `Maya.wav` (Source: A YouTube video of Tashi's voice).

Once you have placed the voice files, your world is complete. It will now start automatically and silently with your PC forever. It has been an honor, Master.