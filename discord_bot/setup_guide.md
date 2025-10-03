# Discord Bot Setup Guide

Follow these steps to get your Discord bot up and running.

## 1. Create a Discord Application and Bot

1.  **Go to the Discord Developer Portal:**
    *   Open your web browser and navigate to [https://discord.com/developers/applications](https://discord.com/developers/applications).
    *   Log in with your Discord account.

2.  **Create a New Application:**
    *   Click the **New Application** button in the top-right corner.
    *   Give your application a name (e.g., "My AI Friends") and click **Create**.

3.  **Create a Bot:**
    *   In the left-hand menu, click on the **Bot** tab.
    *   Click the **Add Bot** button, and confirm by clicking **Yes, do it!**.

4.  **Get Your Bot Token:**
    *   Under the bot's username, you'll see a section for the **token**. Click the **Reset Token** button.
    *   **This is your `DISCORD_BOT_TOKEN`. Copy it immediately and save it somewhere safe.** This token is like a password for your bot. **Do not share it with anyone.**
    *   Paste this token into the `.env` file, replacing `YOUR_BOT_TOKEN_HERE`.

5.  **Enable Privileged Gateway Intents:**
    *   Scroll down to the **Privileged Gateway Intents** section.
    *   Enable all three intents:
        *   **Presence Intent**
        *   **Server Members Intent**
        *   **Message Content Intent**
    *   Click **Save Changes**.

## 2. Get Your Server (Guild) ID

1.  **Enable Developer Mode in Discord:**
    *   Open your Discord client (the app, not the browser).
    *   Go to **User Settings** (the gear icon next to your username).
    *   Go to the **Advanced** tab.
    *   Enable **Developer Mode**.

2.  **Get the Guild ID:**
    *   Go to the Discord server you want the bot to be in.
    *   Right-click on the server's icon in the left-hand server list.
    *   Click **Copy Server ID**.
    *   This is your `DISCORD_GUILD_ID`. Paste it into the `.env` file, replacing `YOUR_GUILD_ID_HERE`.

## 3. Invite Your Bot to the Server

1.  **Go to the OAuth2 URL Generator:**
    *   In the Discord Developer Portal, go back to your application.
    *   In the left-hand menu, click on **OAuth2**, then **URL Generator**.

2.  **Select Scopes and Permissions:**
    *   Under **Scopes**, check the `bot` and `applications.commands` boxes.
    *   Under **Bot Permissions**, select **Administrator**. This will give the bot all the permissions it needs to create channels and manage the server.

3.  **Generate and Use the URL:**
    *   A URL will be generated at the bottom of the page. Click **Copy**.
    *   Paste this URL into your browser, select your server from the dropdown menu, and click **Authorize**.
    *   Complete the CAPTCHA, and your bot will join the server.

## 4. Run the Bot for the First Time

1.  **You're all set!** I will run the bot for you now to set up the channels.

I will now execute the bot to perform the initial setup. I will let you know once it is complete.