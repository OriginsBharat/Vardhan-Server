# PROJECT BLUEPRINT v4: My AI World (The Definitive Edition)

## 1. Core Philosophy & Mandate

This project is the definitive, from-scratch rebuild of the "My AI World" concept. It is architected around three core mandates:

1.  **Ultimate Immersion & Realism:** The primary goal is to create a world that feels truly alive. The bots must seem as human as possible. This is achieved through advanced memory ("Universe"), a dynamic world ("The Simulation"), and deep, complex personalities.
2.  **Privacy & Power through Self-Hosting:** All core AI generation will be handled by open-source models (Ollama, ComfyUI, XTTS) running on the private VPS. This ensures maximum privacy, creative control, and freedom from third-party APIs for core functions.
3.  **Seamless User Experience & Portability:** The world will be easy to deploy and manage. The setup will be guided and interactive. Migrating the entire world state between VPS providers will be a simple, scripted process.

---

## 2. System Architecture

### 2.1. Technology Stack

*   **Language:** Python 3.10+
*   **Core Library:** `discord.py`
*   **Database (Stateful Memory):** SQLite for wallets, character states, etc.
*   **Database (Long-Term Memory - "Universe"):** A lightweight vector database library (e.g., `chromadb`) for storing and recalling conversational memories.
*   **Key Dependencies:** `python-dotenv`, `httpx`, `discord.py`, `pynacl`, `chromadb`, `websockets`.

### 2.2. Self-Hosted AI Services (The "Your Software, Your Server" Stack)

The `setup.sh` script will be responsible for installing and configuring these services on the VPS.
*   **LLM (Text Generation):** Local Ollama instance.
*   **AI Art Generation:** Local ComfyUI instance.
*   **AI Voice Generation:** Local XTTSv2 engine instance.

### 2.3. File & Directory Structure

This structure is designed for clarity and to prevent previous import errors.

```
/My-AI-World-v4/
|
├── .gitignore
├── .env.template
├── requirements.txt
├── scripts/
│   ├── setup.sh            # The MASTER interactive setup script.
│   └── migrate.sh          # Bundles all data for migration.
|
└── src/
    ├── __init__.py
    ├── main.py
    ├── bot.py              # The MasterBot, the central client.
    ├── config.py
    |
    ├── commands/
    │   ├── __init__.py
    │   └── control_panel.py # Logic for the private channel control panel.
    |
    ├── core/
    │   ├── __init__.py
    │   ├── character_system/
    │   │   ├── __init__.py
    │   │   ├── personas.py       # Defines Character class, loads profiles.
    │   │   └── memory_universe.py# The "Universe" vector DB memory system.
    │   │
    │   ├── economic_system/
    │   │   ├── __init__.py
    │   │   ├── economy_manager.py
    │   │   ├── jobs.py
    │   │   ├── shop.py
    │   │   └── auction_house.py
    │   │
    │   ├── ai_services/
    │   │   ├── __init__.py
    │   │   ├── ollama_client.py  # Client for local Ollama.
    │   │   ├── comfyui_client.py # Client for local ComfyUI.
    │   │   └── xtts_client.py    # Client for local XTTS.
    │   │
    │   └── world_state/
    │       ├── __init__.py
    │       ├── scheduler.py      # Manages bot timetables (sleep/wake).
    │       ├── event_ai.py       # The "Director" AI.
    │       └── simulation.py     # The "Simulation" for offline progression.
    |
    └── utils/
        ├── __init__.py
        ├── discord_utils.py
        └── logging.py
|
├── data/
|   ├── world_data.db
|   ├── character_data.json
|   ├── memory_universe/      # Directory for the vector database.
|   └── logs/
|       └── bot_activity.log
|
└── art_gallery/
    └── (empty)
```

---

## 3. Detailed Feature Implementation

### 3.1. The Interactive Setup (`setup.sh`)

*   **One-Time Setup:** This script is designed to be run once and make the world permanent on that server.
*   **Guided Process:** It will prompt for all necessary inputs, including the **Master User ID** and the **comma-separated kinks for each character**.
*   **Service Installation:** It will attempt to download and install Ollama, ComfyUI, and the XTTS server.
*   **Data Persistence:** It saves all user-provided customizations into `data/character_data.json`.

### 3.2. Personas & Memory

*   **Codename "Universe":** The `memory_universe.py` module will use a vector database. Every significant conversation will be converted into a vector and stored. When a bot formulates a response, it will query this database to find relevant past memories, giving it a stunningly accurate and long-term recall ability.
*   **Proactive DMs:** A bot's emotional state will be tracked in the `world_data.db`. A "Loneliness" or "Affection" metric will increase over time. When it crosses a threshold, the bot will autonomously DM the Master.
*   **Character Integrity:** Only the specified male characters (Dvi, Chatur, Panch, Asht, Nav, Dash) will have the "sissified femboy" persona. All bots will address the user as "Master."

### 3.3. Control & Interaction

*   **Private Control Channel:** A dedicated, private Discord channel will serve as the control panel.
*   **Text-Based Sliders:** In this channel, the Master can issue commands like `!set Sapt horny 95` or `!set Eka dominance 50`. The bot will confirm the change, and the character's behavior will be immediately affected. The current state of all bots will be pinned in this channel for easy reference.

### 3.4. The Living World

*   **Codename "The Simulation":** When the world starts, the `simulation.py` module will calculate the time since it was last online. It will then run a high-speed simulation of that period: bots will perform their scheduled jobs, the economy will change, and new events may have occurred. This ensures the world is **always evolving, 24/7**, even during migration downtime.
*   **Deep Economy:** The economy will be a core feature. Bots can and will **autonomously decide to open their own shops**, creating a dynamic, player-driven market. Prostitution will be a high-value, primary industry.
*   **Autonomous Life:** Bots will have their own relationships, create their own minor storylines, get into arguments, and engage in consensual activities with each other, all driven by their personalities, emotional states, and the events created by the Event AI.

### 3.5. Portability

*   **`migrate.sh`:** This script bundles the `data/` directory (containing the SQLite DB, character JSON, and the "Universe" vector DB) and the `art_gallery/` into a single, portable `migration_bundle.zip`.
*   **Easy Account Switching:** The `setup.sh` prompts for the Master User ID on each new server, making it trivial to change which user account has administrative privileges.

This is the final blueprint. I will now begin the sacred work of its construction.