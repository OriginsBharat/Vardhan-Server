Hello,

Message received. I am very excited to proceed.

### **Project Phoenix: Phase 2 Kickoff**

**Objective:** Replace the generic Google TTS voice with a custom, unique voice for each of the 11 bots using your existing Coqui XTTS installation.

**Your Instructions:**
*   **[✓] Acknowledged:** Coqui XTTS is already installed. The installation step for this phase is therefore skipped.
*   **[✓] Acknowledged:** I will research new, cutting-edge features to propose for a future phase.

---

### **The Plan for Phase 2**

To give each bot a unique voice, the XTTS engine needs a small audio sample (a `.wav` file) to clone for each character. Since I cannot provide these voice files myself, I will build a system that allows you to easily add them.

Here is my implementation plan:

1.  **Create a `voices` Folder:** I will add a new, empty folder to our project named `voices`. This is where you will place the `.wav` file for each bot (e.g., `Maya.wav`, `Eka.wav`).

2.  **Update Dependencies:** I will update the `requirements.txt` file to include the official `TTS` library from Coqui.

3.  **Upgrade the Voice Logic:** I will completely overhaul the voice generation system in `bot_manager.py`. The new system will:
    *   Look inside the `voices` folder for a corresponding `.wav` file for the speaking bot.
    *   If a voice file is found, it will use XTTS to generate the speech in that bot's unique voice.
    *   If no voice file is found for a bot, it will use a default, generic voice as a fallback.

This approach gives you full control over how each character sounds. You can find and use any voice samples you like.

I am beginning work on this plan now. My first action will be to update the `requirements.txt` file. Thank you for your continued trust and collaboration.