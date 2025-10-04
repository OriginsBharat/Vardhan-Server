# PROJECT BLUEPRINT v3: My AI World (Cloud Edition)

## 1. Core Philosophy & Mandate

This project is a complete, from-scratch rebuild of the "My AI World" concept. The previous version was plagued by structural errors and a reliance on local dependencies. This version corrects those mistakes with two core mandates:

1.  **Cloud-First Architecture:** Eradicate all local dependencies. The world will run on a lean VPS, orchestrating powerful, free-tier online services for all AI generation tasks (LLM, Art, Voice). This ensures maximum portability and removes complex local setup.
2.  **User-Centric Design & Supreme Ease of Use:** The entire user experience, from initial setup to daily interaction, will be seamless. The setup will be interactive and guided. The system will be self-managing and robust.

Every feature and architectural decision will be measured against these two principles.

---

## 2. System Architecture

### 2.1. Technology Stack

*   **Language:** Python 3.10+
*   **Core Library:** `discord.py`
*   **Database:** SQLite (for maximum portability of the world's state).
*   **Key Dependencies:** `python-dotenv`, `httpx`, `discord.py`, `pynacl`.

### 2.2. External Cloud Services (The "No Local" Stack)

*   **LLM (Text Generation):** The system will be built with a generic API client for a free-tier LLM provider (e.g., Groq, Together.ai, or other services found via research). The specific API key and endpoint URL will be configured in the `.env` file.
*   **AI Art Generation:** The system will use a free-tier online image generation service (e.g., Stability AI API, or similar). The API key will be configured in the `.env` file. This replaces the local ComfyUI dependency.
*   **AI Voice Generation:** The system will use a free-tier online TTS service (e.g., ElevenLabs, Play.ht). The API key will be configured in the `.env` file. This replaces the local XTTS engine dependency.

### 2.3. File & Directory Structure

This structure is designed for absolute clarity and to prevent the previous import errors. The application will be run as a proper Python module.

```
/My-AI-World-v3/
|
├── .gitignore              # Ignores venv, logs, pycache, etc.
├── .env.template           # A template for the user to create their .env file.
├── requirements.txt        # All Python dependencies.
├── scripts/
│   ├── setup.sh            # The MASTER setup script. Interactive and guided.
│   └── migrate.sh          # Bundles all persistent data for migration.
|
└── src/
    ├── __init__.py         # Makes 'src' a package.
    ├── main.py             # Main application entry point.
    ├── bot.py              # Defines the MasterBot, the central client.
    ├── config.py           # Loads and validates all secrets from .env.
    |
    ├── commands/
    │   ├── __init__.py
    │   └── control_panel.py # Logic for the !controlpanel command.
    |
    ├── core/
    │   ├── __init__.py
    │   ├── character_system/
    │   │   ├── __init__.py
    │   │   └── personas.py       # Defines Character class, loads profiles from JSON.
    │   │
    │   ├── economic_system/
    │   │   ├── __init__.py
    │   │   ├── economy_manager.py# Manages the SQLite database for wallets/transactions.
    │   │   ├── jobs.py           # Defines the job market.
    │   │   ├── shop.py           # Defines system-run shops.
    │   │   └── auction_house.py  # Manages the auction system.
    │   │
    │   ├── ai_services/
    │   │   ├── __init__.py
    │   │   ├── llm_api.py        # Generic client for online LLM services.
    │   │   ├── art_api.py        # Generic client for online art generation services.
    │   │   └── voice_api.py      # Generic client for online TTS services.
    │   │
    │   └── world_state/
    │       ├── __init__.py
    │       ├── scheduler.py      # Manages bot timetables (sleep/wake).
    │       └── event_ai.py       # The "Director" AI for creating world events.
    |
    └── utils/
        ├── __init__.py
        ├── discord_utils.py  # Helper functions for Discord embeds.
        └── logging.py        # Centralized logging setup.
|
├── data/
|   ├── world_data.db         # SQLite database for economy, etc. (Created on run)
|   ├── character_data.json   # Stores character kinks and customizations. (Created by setup)
|   └── logs/
|       └── bot_activity.log    # General activity log.
|
└── art_gallery/
    └── (empty)                 # Saved AI-generated art will go here.
```

---

## 3. Detailed Feature Implementation

### 3.1. The Interactive Setup (`setup.sh`)

This is the new, user-friendly entry point to the world.
1.  **Welcome Message:** Greets the "Master."
2.  **Dependency Checks:** Verifies `python3.10+` and `ffmpeg`.
3.  **Environment Setup:** Creates the Python `venv` and installs `requirements.txt`.
4.  **Configuration Check:** Prompts the user to create a `.env` file from `.env.template` if one doesn't exist, and waits for them to fill it in.
5.  **Interactive Kink Configuration:**
    *   It will loop through each of the 11 characters by name.
    *   For each character, it will prompt: `Please enter the comma-separated kinks for [Character Name]:`
    *   It will parse this input.
    *   It will save the results into a `data/character_data.json` file.
6.  **Launch:** Executes the bot using `python3 -m src.main`.

### 3.2. Personas & Kinks

*   **`personas.py`:** Will now load all character data from `data/character_data.json`. This makes the characters fully customizable without editing code.
*   **Core Personalities:**
    *   All bots refer to the user as **"Master"**. This will be hardcoded into the base prompt.
    *   **Maya:** Leader, administrator, devoted.
    *   **Eka:** "Dom MILF" to bots, "mommy" to Master.
    *   **Sapt:** Loyal bodyguard, exclusive to Master for NSFW.
    *   **Dvi, Trini, Chatur, Panch, Shash, Asht, Nav, Dash:** All adopt a "sissified femboy" persona towards the Master. Their base personalities (artistic, studious, etc.) remain.
*   **Schedules:** Each character will have a daily schedule (wake, work, sleep) defined in the `personas.py` module, which the `scheduler.py` will enforce.

### 3.3. Economy

*   **Currency:** `Rs` (Rupees).
*   **Master's Wallet:** The user has functionally infinite `Rs`.
*   **Jobs:** A diverse market of fantasy (Alchemist, Hunter) and NSFW (Prostitution, Erotic Writing, Art Commissions) jobs will be defined in `jobs.py`. Bots will autonomously perform jobs based on their persona.
*   **Shops:** Eka will own and run a system shop, "Eka's Emporium," selling various goods.
*   **Auctions:** A fully-featured `AuctionHouse` will run in the background, allowing any character (or the Master) to auction items like high-quality art or special services in a dedicated channel.

### 3.4. Supporting Systems

*   **Event AI:** The "Director" will run as a background task, periodically triggering random world events (festivals, wars, mysteries) to create emergent story moments.
*   **`!controlpanel`:** A Master-only command to view the current emotional state of all bots and set them to a new state (e.g., `!controlpanel set Maya Happy`). This will use "emotional sliders" in concept, allowing for easy adjustment.
*   **VPS Trial Timer:** A background task will check the `TRIAL_END_DATE` in the `.env` file daily. If the trial is within 3 days of expiring, it will automatically send a DM to the Master.

### 3.5. Portability

*   **`migrate.sh`:** This script will bundle the entire state of the world (`data/` directory, `art_gallery/`, etc.) into a single `migration_bundle.zip` file, allowing for easy transfer to a new server.

---

## 4. Secrets & Configuration (`.env.template`)

This file will be the template for all user-provided secrets.

```
# --- Discord Secrets ---
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
DISCORD_GUILD_ID=YOUR_DISCORD_SERVER_ID_HERE
USER_ID=YOUR_DISCORD_USER_ID_HERE
DISCORD_EVENT_CHANNEL_ID=YOUR_EVENT_CHANNEL_ID_HERE
DISCORD_AUCTION_CHANNEL_ID=YOUR_AUCTION_CHANNEL_ID_HERE

# --- Online AI Service APIs ---
# Find these in the dashboards of your chosen free-tier providers.
LLM_API_PROVIDER= # e.g., "groq" or "together"
LLM_API_KEY=YOUR_LLM_API_KEY_HERE
LLM_MODEL_NAME= # e.g., "llama3-70b-8192"

ART_API_PROVIDER= # e.g., "stabilityai"
ART_API_KEY=YOUR_ART_API_KEY_HERE

VOICE_API_PROVIDER= # e.g., "elevenlabs"
VOICE_API_KEY=YOUR_VOICE_API_KEY_HERE

# --- VPS Portability ---
# Enter the end date of your VPS trial here (YYYY-MM-DD). Leave blank to disable.
TRIAL_END_DATE=""
```

This blueprint is the definitive guide. I will now proceed to the next step as commanded: wiping the repository clean.