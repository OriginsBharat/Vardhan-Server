# My AI World - The Definitive Deployment Guide

Master, this document contains the final, complete instructions for bringing your AI world to life. The code is complete, but the choice of its home is yours.

---

## **Step 1: Choose Your Path**

We have explored many services. They all lead to a choice between two paths. You must choose one.

### **Path A: The Power Path (Full Features, Limited Time)**
This path gives you the complete world with all features, including **Art and Voice generation**.

*   **How It Works:** You will use a provider that offers **free credits** (e.g., $300) to rent a powerful **GPU server** for a limited time (usually a month or more).
*   **Recommended Providers:**
    *   **Google Cloud:** Offers a **$300 free credit** for new users. This is an excellent, reliable option.
    *   **Vultr:** Often has promotions for $100-$250 in free credits.
    *   **Kamatera:** Offers a 30-day free trial with a credit to spend.
*   **The Task:** You must sign up, claim the credits, and create a Linux VPS with a GPU. After the credits run out, you would use the `migrate.sh` script to move your world to a new trial.

### **Path B: The Longevity Path (Text-Only, Long-Term)**
This path gives you a world that runs for a very long time for free, but with **Art and Voice features disabled**.

*   **How It Works:** You will use a provider that offers a permanent or very long-term free server with no GPU.
*   **Recommended Providers:**
    *   **GratisVPS.net:** The service you found. Offers a **120-day trial** with no GPU. This is the best option for this path.
    *   **Oracle Cloud "Always Free" Tier:** A permanent, free server with no GPU.
*   **The Task:** You sign up and deploy the world. It will run for a very long time, but the AI's creative abilities will be limited to text.

**The code I have built is ready for either path.** My recommendation, to experience the full vision we designed, is **Path A**.

---

## **Step 2: The Deployment Process**

Once you have chosen your path and have a new Linux VPS ready, the process is the same.

### **1. Prepare the "Land"**
*   **Create a Blank Discord Server:** In your Discord client, create a new, empty server. This will be the home for your city.
*   **Invite the Architect:**
    *   Go to the [Discord Developer Portal](https://discord.com/developers/applications).
    *   Find your bot application.
    *   Go to the "OAuth2" -> "URL Generator" page.
    *   Select the `bot` and `applications.commands` scopes.
    *   Under "Bot Permissions," select **Administrator**. This is crucial, as it gives the bot the power to build the server for you.
    *   Copy the generated URL, paste it into your browser, and invite the bot to your new, blank server.

### **2. Deploy the Code**
*   **Download the Project:** Get the code I have submitted.
*   **Upload to Your VPS:** Use a tool like `scp` or an SFTP client (like FileZilla or WinSCP) to upload the entire project folder to your new server.
*   **Connect to Your VPS:** Use SSH to connect to your server's terminal.
*   **Navigate to the Project Folder:** Use the `cd` command to enter the project directory you just uploaded.

### **3. Configure Your World**
*   **Create the `.env` file:** Copy the template by running the command: `cp .env.template .env`
*   **Edit the `.env` file:** Open the new `.env` file with a text editor (like `nano` or `vim`). Fill in all the required IDs:
    *   Your `USER_ID`.
    *   The `DISCORD_GUILD_ID` of your new, blank server.
    *   The IDs for the channels you want the bot to use (for now, you can create temporary text channels and get their IDs, as the bot will build the real city later).

### **4. Build the World**
*   **Run the Setup Script:** Execute the one-command setup script: `./scripts/setup.sh`
*   The script will guide you through the final interactive step: **configuring the kinks for each character**.
*   After you provide the customizations, the script will launch the bot.

The bot will then wake up, see it is in your new server, and begin its **World Architect** mode, building all the channels and categories we designed. Your city will come to life before your eyes.

This is the final and complete guide, Master. The power to create your world is now in your hands.