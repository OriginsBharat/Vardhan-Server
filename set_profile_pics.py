import os
import asyncio
import httpx
import random
from io import BytesIO
from dotenv import load_dotenv
import discord

from bot_profiles import PROFILES

# --- Configuration ---
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID_STR = os.getenv('DISCORD_GUILD_ID')
SD_API_URL = os.getenv('SD_API_URL', 'http://127.0.0.1:8188')

if not all([TOKEN, GUILD_ID_STR]):
    print("!!! ERROR: Missing DISCORD_BOT_TOKEN or DISCORD_GUILD_ID in .env file. Please fill it out. !!!")
    exit()

GUILD_ID = int(GUILD_ID_STR)

# --- ComfyUI Image Generation ---
async def generate_art_comfy(bot_name, persona_snippet):
    print(f"🎨 Generating profile picture for {bot_name}...")

    prompt_text = f"masterpiece, best quality, beautiful anime character portrait, {bot_name}, {persona_snippet}"
    negative_prompt = "text, watermark, low quality, worst quality, blurry, ugly, deformed"

    # Default ComfyUI txt2img workflow
    workflow = {
        "3": { "class_type": "KSampler", "inputs": { "seed": random.randint(0, 18446744073709551615), "steps": 25, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0] } },
        "4": { "class_type": "CheckpointLoaderSimple", "inputs": { "ckpt_name": "v1-5-pruned-emaonly.safetensors" } },
        "5": { "class_type": "EmptyLatentImage", "inputs": { "width": 512, "height": 512, "batch_size": 1 } },
        "6": { "class_type": "CLIPTextEncode", "inputs": { "text": prompt_text, "clip": ["4", 1] } },
        "7": { "class_type": "CLIPTextEncode", "inputs": { "text": negative_prompt, "clip": ["4", 1] } },
        "8": { "class_type": "VAEDecode", "inputs": { "samples": ["3", 0], "vae": ["4", 2] } }
    }

    prompt_payload = {"prompt": workflow, "client_id": "ProfilePicSetter"}

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            # Queue prompt
            res = await client.post(f"{SD_API_URL}/prompt", json=prompt_payload)
            res.raise_for_status()
            prompt_id = res.json()['prompt_id']
            print(f"  > Queued prompt {prompt_id} for {bot_name}.")

            # Poll for result
            while True:
                history_res = await client.get(f"{SD_API_URL}/history/{prompt_id}")
                history_res.raise_for_status()
                history = history_res.json()
                if prompt_id in history and history[prompt_id]['outputs']:
                    outputs = history[prompt_id]['outputs']
                    if '8' in outputs and 'images' in outputs['8']: # Check for output from VAEDecode node
                        image_info = outputs['8']['images'][0]
                        print(f"  > Image generated for {bot_name}.")
                        break
                await asyncio.sleep(2)

            # Fetch image data
            image_res = await client.get(f"{SD_API_URL}/view?filename={image_info['filename']}&subfolder={image_info.get('subfolder', '')}&type={image_info['type']}")
            image_res.raise_for_status()
            print(f"  > Fetched image data for {bot_name}.")
            return image_res.content

        except Exception as e:
            print(f"❌ Error generating art for {bot_name}: {e}")
            return None

# --- Discord Client to Set Pictures ---
class ProfileSetterClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Logged in as {self.user} to set profile pictures.')

        guild = self.get_guild(GUILD_ID)
        if not guild:
            print(f"❌ ERROR: Cannot find Guild with ID {GUILD_ID}. Make sure the bot is in the server.")
            await self.close()
            return

        print(f"Found server: {guild.name}")
        channels_to_update = [c for c in guild.text_channels]
        print(f"Found {len(channels_to_update)} text channels to update webhooks in.")

        for bot_profile in PROFILES:
            bot_name = bot_profile["name"]
            persona_snippet = bot_profile["base_persona"].split('.')[1].strip()

            image_bytes = await generate_art_comfy(bot_name, persona_snippet)

            if image_bytes:
                print(f"🖼️ Updating profile picture for {bot_name} across all channels...")
                for channel in channels_to_update:
                    try:
                        # Find existing webhook or create a new one
                        wh = discord.utils.get(await channel.webhooks(), name=bot_name)
                        if not wh:
                            wh = await channel.create_webhook(name=bot_name)
                            print(f"  > Created new webhook for {bot_name} in #{channel.name}")

                        # Edit the webhook's avatar
                        await wh.edit(avatar=image_bytes)
                        print(f"  > Successfully set avatar for {bot_name} in #{channel.name}")
                    except Exception as e:
                        print(f"  > ❌ Failed to update webhook for {bot_name} in #{channel.name}: {e}")
                print("-" * 20)
            else:
                print(f"❌ Skipped setting profile picture for {bot_name} due to image generation failure.")
                print("-" * 20)

        print("✅✅✅ All profile pictures have been updated. You can now stop this script with CTRL+C.")
        await self.close()

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting the profile picture setter script...")
    print("NOTE: This script will generate and set a profile picture for all 11 bots.")
    print("This may take a long time. Please ensure ComfyUI is running.")

    intents = discord.Intents.default()
    intents.guilds = True
    intents.webhooks = True

    client = ProfileSetterClient(intents=intents)
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"An error occurred while running the client: {e}")