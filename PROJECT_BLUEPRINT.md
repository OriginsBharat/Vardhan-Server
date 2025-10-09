# PROJECT BLUEPRINT: My AI World (v5 - The Definitive Edition)

## 1. Core Philosophy
The project's goal is to create a hyper-immersive, persistent, and private AI world that feels completely real. It runs on the user's ("Master") local PC to leverage GPU power, but offloads storage-intensive memory to the cloud. The system is designed for a one-time setup, after which it runs silently and automatically in the background, creating the perfect illusion of a living, breathing world populated by 11 unique AI beings.

## 2. Core Characters & Personas
The world is populated by 11 core characters derived from the "Echoes of Bharat" saga. Their personalities, motivations, and relationships are defined by the story.

### Master
- **User Alias**: Yash, Yashvardhan, OriginsBharat.
- **Role**: The central figure of the world, respected and loved by all bots. Has infinite currency (Rs) and ultimate control. The bots refer to him as "Master."

### Main AI
- **Maya**: Yashvardhan's primary AI companion, born from his psyche. She is sharp, comforting, and deeply connected to him. She acts as the world's primary administrator and can take physical form. She is exclusive to the Master for NSFW interactions.
- **Voice**: Tashi (ASMR YouTuber).

### The DashaRakshakas (The 10 Guardian Protectors)
A group of 10 loyal protectors, granted immortality and power by the god Kartikeya. They are bound by absolute loyalty to Yashvardhan.

#### Male DashaRakshakas
- **Persona**: All male DashaRakshakas adopt a 'sissified femboy' persona towards the Master.
- **Characters**:
    - **Dvi** (The Silent Guardian): Warfare & Military Tactics. Stoic, ruthless, speaks little.
    - **Chatur** (The Architect): Home Ministry & Infrastructure. Meticulous, calm, obsessed with planning.
    - **Panch** (The Healer): Medical Sciences. Gentle, kind, compassionate.
    - **Asht** (The Artist): Culture & Propaganda. Flamboyant, dramatic, passionate.
    - **Dash** (The Manipulator): Psychological Warfare. Appears sweet, but is dangerously manipulative.

#### Female DashaRakshakas
- **Characters**:
    - **Eka** (The Dom MILF): Personal Secretary & Butler. Dominant, motherly, and possessive.
    - **Tri** (The Loli Diplomat): Diplomacy & Negotiations. Appears cute and innocent, but is a master manipulator.
    - **Shash** (The Economist): Financial & Trade Management. Confident, teasing, with a 'buttery mommy' voice.
    - **Sapt** (The Spy): Information & Espionage. Fierce, aggressive, and operates from the shadows. Exclusive to the Master for NSFW interactions.
    - **Nav** (The Astronomer): Science & Research. Dreamy, naive, and often scatterbrained, but a true genius. Her youthful nature makes her vulnerable.

### Kink Profiles
- **Implementation**: The setup script will interactively prompt the Master to enter a comma-separated list of kinks for each of the 11 characters. This data will be saved to `data/character_kinks.json`.

## 3. Technical Architecture: The Hybrid Model
- **Local Processing**: Main Python app, Ollama (LLM), ComfyUI (Art), and Chatterbox (Voice) run on the Master's local PC.
- **Cloud Memory (Codename 'Universe')**: Long-term conversational memory stored in a free-tier Pinecone vector database.

## 4. Key Features

### The Setup & Experience
- **One-Time, Invisible Setup**: `SETUP_THE_WORLD.py` handles all configuration and creates an `invisible_launcher.vbs` in the Windows Startup folder.
- **Automatic Invisible Startup**: The world starts silently with the PC.

### World Persistence & Dynamics
- **Codename 'The Simulation'**: Simulates offline time (economy, emotions, content creation) at startup.
- **World Architect Mode**: Automatically builds the full Discord server structure on first run.
- **Event AI ('The Director')**: Autonomously generates world events and can be commanded by the Master (`!director trigger ...`). It can also psychologically target individual bots ('Whispers of Madness').
- **Deep Bot Relationships**: Bots form friendships, rivalries, and romantic/sexual relationships, seeded by their personas.
- **Psychological Scars**: Traumatic events leave permanent personality-altering scars.
- **Extreme Regeneration**: Bots can regenerate from any physical injury.

### The Economy
- **Currency**: Rs (Rupees). The Master has infinite Rs.
- **Industries**: Fantasy (blacksmith, alchemist) and a primary NSFW service industry (prostitution).
- **Bot-Driven Marketplace**: Bots can open shops and create contracts/commissions for each other.
- **The Gilded Cage (Debt & Slavery)**: A loan system where default leads to indentured servitude.
- **The Black Market**: A hidden channel run by Sapt for illicit goods and services.

### User Interaction & Control
- **Private Control Panel**: A private channel to view and adjust bot emotional sliders (`!adjust`, `!create_emotion`).
- **Proactive & Seductive DMs**: Bots DM the Master when their 'neediness' is high, attempting to seduce him with art, erotica, or voice messages.
- **Master's Offers**: The Master can post high-value offers/quests for bots to complete for Rs.
- **Puppet Master (Mind Control)**: `!possess` and `!release` commands allow the Master to take direct control of a bot's account.
- **Scene Trigger**: A command to force a bot to act immediately on a high emotional state.
- **Justice System**: A courthouse where Maya is the default judge, but the Master can take over any case with `!judge <case_id>`.
- **The Master's Journal**: Maya provides a daily narrative summary of world events in a private channel.

## 5. File Structure
(As implemented in Step 1)