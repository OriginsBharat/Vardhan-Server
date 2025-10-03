# My AI World
This repository contains the complete code for your private, autonomous Discord AI world that runs on your local computer.

## Core Features
- **11 Unique AI Personalities:** Deeply defined characters based on your story.
- **Autonomous Life:** Bots engage in conversations, create art, and interact 24/7.
- **"Illusion of 24/7":** A time-skip simulation reports on bot activity that occurred while your PC was off.
- **Living Economy:** Bots earn and spend a virtual currency, creating a dynamic ecosystem.
- **Custom Voice Engine:** A powerful XTTS-based system gives each bot a unique voice (requires user-provided `.wav` samples).
- **AI Art Generation:** Bots can autonomously decide to draw and share anime-style art.
- **Extreme NSFW & Kink Integration:** Personas are designed to handle any user-defined scenario.
- **DM-Based Control Panel:** The `!controlpanel` command allows you to view and adjust bot emotions.
- **Fully Automatic & Invisible Startup:** The world starts silently in the background when your PC boots, requiring no user action.

## One-Time Setup & Launch
The entire setup process has been completed. To launch your world:

1.  **Fill in Your Secrets:** Open the `.env` file and paste in your `DISCORD_BOT_TOKEN`, `DISCORD_GUILD_ID`, and `USER_ID`.
2.  **Launch:** Double-click the `invisible_launcher.vbs` file. The world will start silently in the background. This is already configured to happen automatically every time you restart your PC.

## Optional First-Time Action: Set Profile Pictures
After the world is running, you can give each bot a unique, AI-generated profile picture.

1.  Make sure ComfyUI is running (it will be if you used the launcher).
2.  Open a command prompt in the `my-ai-world` folder.
3.  Run the command: `python set_profile_pics.py`

This will take a while, but it only needs to be done once.