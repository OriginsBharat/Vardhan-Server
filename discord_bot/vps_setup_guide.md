# VPS and AI Bot Setup Guide

This guide will walk you through setting up your 24/7 persistent AI world on a cloud server. Follow these steps carefully.

## Part 1: Setting up the Cloud Server (VPS)

1.  **Sign Up for the Free Trial:**
    *   Go to [https://gratisvps.net/](https://gratisvps.net/).
    *   Sign up for the **Free VPS** plan ($0.00/month for 120 days).
    *   **Crucially, ensure the VPS you select has a GPU.** You may need to look for specific plans advertised with GPU access (e.g., NVIDIA Tesla T4, etc.). AI image generation is impossible without one.

2.  **Configure Your Server:**
    *   During setup, choose the Operating System: **Ubuntu 22.04**.
    *   Choose a server location closest to you.

3.  **Get Your Server Credentials:**
    *   After creation, you will receive an **IP Address**, a **Username** (`root`), and a **Password**. Save these.

## Part 2: Connecting to Your Server

*   Use an SSH client (PowerShell on Windows, Terminal on macOS/Linux) to connect.
*   Run the command: `ssh root@your_server_ip`
*   Enter `yes` if prompted, then paste your password to log in.

## Part 3: Deploying the AI Bot World

I will provide you with a single deployment script (`deploy.sh`). This script will automate everything.

*   **What the script does:**
    1.  Installs all necessary software (Ollama for text AI, AUTOMATIC1111's Web UI for image AI).
    2.  Downloads the bot application code.
    3.  Downloads and configures the AI models (`llama3` for text, an anime-style model for images).
    4.  Sets up all services to run 24/7 in the background.

I am still finalizing this script. Once it's ready, I will give you the final command to run on your server.

## Part 4: The Backup and Restore Process (For Trial Migration)

Every 120 days, you will need to migrate to a new free trial server. I have made this process as simple as possible.

1.  **On the OLD server:**
    *   Connect to it via SSH.
    *   Run a backup script I will provide: `/opt/discord-ai-world/backup.sh`.
    *   This will create a `world_backup.zip` file. Download this file to your local computer.

2.  **On the NEW server:**
    *   Set up the new server and connect via SSH.
    *   Upload the `world_backup.zip` file to the new server.
    *   Run the main `deploy.sh` script. It will automatically detect the backup and restore your world, including all bot memories and conversations.

This ensures a seamless transition, keeping your AI world alive indefinitely. I will create the `backup.sh` script in a later step.