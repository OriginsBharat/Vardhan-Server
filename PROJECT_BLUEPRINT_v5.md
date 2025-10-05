# PROJECT BLUEPRINT v5: My AI World (The Hybrid Invisible World)

## 1. Core Philosophy & Mandate

This is the definitive and final architecture for the "My AI World" project, designed to provide the ultimate immersive experience.

1.  **The Hybrid Model:** The world leverages the best of both local and cloud computing.
    *   **Local Power:** All processing-intensive AI models (Ollama for text, ComfyUI for art, XTTS for voice) run on the user's local PC, utilizing the full power of their GPU for maximum performance and privacy.
    *   **Cloud Memory:** The "Universe" long-term memory system is offloaded to a free-tier online vector database (Pinecone). This allows for virtually infinite memory storage without consuming local disk space.
2.  **Total Immersion via Invisibility:** The world is designed to be a persistent entity on the user's PC, not a program they have to run.
    *   **One-Time Setup:** A single `setup_world.bat` script handles all installation and configuration.
    *   **Invisible Autostart:** After setup, the world starts automatically and silently in the background every time the PC boots, requiring no user interaction ever again.
3.  **The "Illusion of 24/7" Perfected:** When the PC starts, "The Simulation" runs a high-speed calculation of everything that happened while it was off, creating a seamless and persistent world that evolves even when offline.

---

## 2. System Architecture

### 2.1. Technology Stack

*   **Language:** Python 3.10+
*   **Core Library:** `discord.py`
*   **Vector Database:** Pinecone (online service)
*   **Key Dependencies:** `python-dotenv`, `httpx`, `discord.py`, `pynacl`, `pinecone-client`.

### 2.2. Local Self-Hosted AI Services

The `setup_world.bat` script will guide the user through installing these on their local machine.
*   **LLM (Text Generation):** Local Ollama instance.
*   **AI Art Generation:** Local ComfyUI instance.
*   **AI Voice Generation:** Local XTTSv2 engine instance.

### 2.3. File & Directory Structure

```
/My-AI-World-v5/
|
├── .gitignore
├── .env.template
├── requirements.txt
├── setup_world.bat         # The ONE-TIME setup script for the user.
├── start_world.bat         # The master script that launches all services.
└── invisible_launcher.vbs  # The silent launcher placed in the user's Startup folder.
|
└── src/
    ├── __init__.py
    ├── main.py
    ├── bot.py
    ├── config.py
    |
    ├── commands/
    │   ├── __init__.py
    │   └── control_panel.py
    |
    ├── core/
    │   ├── __init__.py
    │   ├── character_system/
    │   │   ├── __init__.py
    │   │   ├── personas.py
    │   │   └── memory_universe.py # Re-architected for Pinecone.
    │   │
    │   ├── economic_system/
    │   │   └── (All existing economy modules)
    │   │
    │   ├── ai_services/
    │   │   └── (All existing local AI clients)
    │   │
    │   └── world_state/
    │       └── (All existing world state modules)
    |
    └── utils/
        └── (All existing utility modules)
|
├── data/
|   ├── world_data.db
|   └── character_data.json
|
└── (Other directories like art_gallery, logs, etc.)
```

---

## 3. Detailed Feature Implementation

### 3.1. The One-Time Setup (`setup_world.bat`)

This script is the only thing the user will ever need to run consciously.
1.  **Welcome & Instructions:** It will clearly explain the one-time nature of the setup.
2.  **Dependency Installation:** It will guide the user through installing Python, Ollama, ComfyUI, and FFmpeg.
3.  **Python Packages:** It will automatically install all `requirements.txt` packages.
4.  **Cloud Memory Setup:** It will instruct the user to sign up for a free Pinecone account and get their API key and environment name.
5.  **Interactive Configuration:**
    *   It will prompt the user to enter all their secrets (Discord tokens, Pinecone keys).
    *   It will then prompt for the kinks for each of the 11 characters.
    *   All this data will be saved securely into the `.env` and `character_data.json` files.
6.  **Automatic Startup Configuration:**
    *   It will create the `invisible_launcher.vbs` script.
    *   It will automatically place a shortcut to this VBScript into the user's Windows Startup folder (`%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup`).

### 3.2. The Invisible Startup

*   **`invisible_launcher.vbs`:** A simple script whose only job is to run the `start_world.bat` script silently, without any visible window.
*   **`start_world.bat`:** The master launcher. When run, it will:
    1.  Start the Ollama server.
    2.  Start the ComfyUI server.
    3.  Start the XTTS server.
    4.  Launch the main Python application (`python -m src.main`).

This is the final blueprint. I will now build it. There will be no more tests. My next message will be the submission of the completed world.