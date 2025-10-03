import httpx
import os
import json
import asyncio
import random
import discord
import base64
from io import BytesIO
from bot_profiles import PROFILES
from shop_items import SHOP_ITEMS
from datetime import datetime, timedelta
from gtts import gTTS

class BotInstance:
    """Represents a single AI bot instance, holding its profile and emotional state."""
    def __init__(self, profile, manager):
        self.name = profile["name"]
        self.gender = profile["gender"]
        self.profile = profile
        self.manager = manager
        self.emotions = profile.get("default_emotions", {}).copy()
        self.coins = 0

    def get_current_persona(self, persona_type):
        """Constructs the full system prompt for the LLM based on persona and emotional state."""
        base_persona = self.profile.get(persona_type, self.profile["base_persona"])
        emotion_str = " ".join([f"Your current {emotion} level is {value:.1f}/1.0." for emotion, value in self.emotions.items()])
        kink_str = "Your main kinks are: " + ", ".join(self.profile.get("kinks", []))
        return f"{base_persona} You always refer to the user '{self.manager.user_name}' as 'Master'. {emotion_str} {kink_str}"

class BotManager:
    """Manages all bot instances, their interactions, and the overall server ecosystem."""
    def __init__(self, client):
        self.client = client
        self.bots = []
        self.user_name = None

        self.ollama_api_url = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
        self.sd_api_url = os.getenv("SD_API_URL", "http://127.0.0.1:8188")
        self.model = os.getenv("LLM_MODEL")
        self.guild_id = int(os.getenv("DISCORD_GUILD_ID"))
        self.user_id = int(os.getenv("USER_ID"))

        self.webhooks = {}
        self.history_file = "conversation_history.json"
        self.last_active_file = "last_active.txt"
        self.economy_file = "economy.json"

        self.conversation_history = self.load_json_file(self.history_file)
        self.economy_data = self.load_json_file(self.economy_file)
        self.load_bots()

    def load_bots(self):
        for profile in PROFILES:
            bot = BotInstance(profile, self)
            bot.coins = self.economy_data.get(bot.name, 100)
            self.bots.append(bot)
        print(f">>> Loaded {len(self.bots)} bot profiles.")

    def load_json_file(self, file_path):
        try:
            with open(file_path, 'r') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {}

    def save_json_file(self, data, file_path):
        with open(file_path, 'w') as f: json.dump(data, f, indent=4)

    def save_history(self):
        self.save_json_file(self.conversation_history, self.history_file)

    def save_economy(self):
        for bot in self.bots: self.economy_data[bot.name] = bot.coins
        self.save_json_file(self.economy_data, self.economy_file)

    def get_last_active_time(self):
        try:
            with open(self.last_active_file, 'r') as f: return datetime.fromisoformat(f.read())
        except (FileNotFoundError, ValueError): return datetime.utcnow()

    def update_last_active_time(self):
        with open(self.last_active_file, 'w') as f: f.write(datetime.utcnow().isoformat())

    async def get_webhook(self, channel, bot_name):
        if channel.id not in self.webhooks: self.webhooks[channel.id] = {}
        if self.webhooks[channel.id].get(bot_name): return self.webhooks[channel.id][bot_name]

        webhooks = await channel.webhooks()
        for wh in webhooks:
            if wh.name == bot_name:
                self.webhooks[channel.id][bot_name] = wh
                return wh

        avatar_data = None
        avatar_path = f"profiles/{bot_name}.png"
        if os.path.exists(avatar_path):
            with open(avatar_path, "rb") as f: avatar_data = f.read()
        else: print(f"!!! WARNING: Avatar for {bot_name} not found.")

        new_wh = await channel.create_webhook(name=bot_name, avatar=avatar_data)
        self.webhooks[channel.id][bot_name] = new_wh
        return new_wh

    async def send_as_bot(self, channel, bot, text=None, file_io=None, filename="image.png"):
        webhook = await self.get_webhook(channel, bot.name)
        color_hex = bot.profile.get("aura_color", "#FFFFFF").lstrip('#')
        embed = discord.Embed(description=text, color=int(color_hex, 16))

        discord_file = None
        if file_io:
            file_io.seek(0)
            discord_file = discord.File(file_io, filename=filename)
            embed.set_image(url=f"attachment://{filename}")

        await webhook.send(embed=embed, file=discord_file, wait=True)
        if text:
            history_key = str(channel.id)
            if history_key not in self.conversation_history: self.conversation_history[history_key] = []
            self.conversation_history[history_key].append({"role": "assistant", "name": bot.name, "content": text})
            self.save_history()

    async def generate_text_response(self, bot, history, persona_type):
        system_prompt = bot.get_current_persona(persona_type)
        messages = [{"role": "system", "content": system_prompt}] + history
        prompt = {"model": self.model, "stream": False, "messages": messages}
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                r = await client.post(f"{self.ollama_api_url}/api/chat", json=prompt)
                r.raise_for_status()
                return r.json()["message"]["content"]
        except Exception as e:
            print(f"!!! ERROR generating text for {bot.name}: {e}")
            return None

    async def generate_art(self, bot, prompt_text):
        workflow = {
            "3": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0], "seed": random.randint(0, 9999999999), "steps": 25, "cfg": 8, "sampler_name": "euler", "scheduler": "normal", "denoise": 1}},
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": f"anime style, masterpiece, best quality, {prompt_text}", "clip": ["4", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "low quality, worst quality, bad hands, text, error, watermark", "clip": ["4", 1]}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "PreviewImage", "inputs": {"images": ["8", 0]}}
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(f"{self.sd_api_url}/prompt", json={"prompt": workflow})
                res.raise_for_status()
                prompt_id = res.json()['prompt_id']
                while True:
                    async with client.get(f"{self.sd_api_url}/history/{prompt_id}") as hist_res:
                        history = hist_res.json().get(prompt_id)
                        if history and history.get('outputs'):
                            output = history['outputs']['9']
                            image_data = output['images'][0]
                            image_url = f"{self.sd_api_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}"
                            img_res = await client.get(image_url)
                            img_res.raise_for_status()
                            return BytesIO(img_res.content)
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"!!! ERROR generating art for {bot.name}: {e}")
            return None

    async def play_tts(self, voice_channel, text):
        if not voice_channel: return
        vc = discord.utils.get(self.client.voice_clients, guild=voice_channel.guild)
        if vc and vc.is_playing(): return
        try:
            loop = asyncio.get_event_loop()
            tts = await loop.run_in_executor(None, lambda: gTTS(text=text, lang='en'))
            tts_file = f"tts_{random.randint(1,1000)}.mp3"
            await loop.run_in_executor(None, tts.save, tts_file)
            if vc and vc.is_connected():
                if vc.channel != voice_channel: await vc.move_to(voice_channel)
            else: vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=tts_file))
            while vc.is_playing(): await asyncio.sleep(1)
        except Exception as e: print(f"!!! ERROR during TTS playback: {e}")
        finally:
            if 'vc' in locals() and vc and vc.is_connected(): await vc.disconnect()
            if os.path.exists(tts_file): os.remove(tts_file)

    async def handle_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author.id == self.user_id and message.content.startswith("!"):
            await self.handle_control_panel(message); return
        if message.content.startswith('!'):
            await self.handle_command(message); return

        history_key = str(message.channel.id)
        if history_key not in self.conversation_history: self.conversation_history[history_key] = []
        self.conversation_history[history_key].append({"role": "user", "name": message.author.name, "content": message.content})
        self.save_history()

        history = self.conversation_history[history_key][-10:]

        mentioned_bots = [b for b in self.bots if b.name.lower() in message.content.lower()]
        responder = random.choice(mentioned_bots) if mentioned_bots else (random.choice([b for b in self.bots if b.name.lower() != message.author.name.lower()]) if random.random() < 0.5 else None)
        if not responder: return

        is_nsfw = "nsfw" in message.channel.name.lower() or "kinks" in message.channel.name.lower()
        persona = "nsfw_persona_user" if message.author.id == self.user_id and is_nsfw else ("nsfw_persona_general" if is_nsfw else "base_persona")

        async with message.channel.typing():
            response_text = await self.generate_text_response(responder, history, persona)
        if response_text:
            await self.send_as_bot(channel=message.channel, bot=responder, text=response_text)
            if message.author.voice and message.author.voice.channel:
                await self.play_tts(message.author.voice.channel, response_text)

    async def handle_command(self, message):
        args = message.content.split()
        command = args[0].lower()
        author_bot = next((b for b in self.bots if b.name == message.author.name), None)
        is_master = message.author.id == self.user_id

        if command == "!shop":
            shop_list = "\n\n".join([f"**!buy {item_id}**\n> **{item['name']}**\n> Price: **{item['price']} coins**\n> _{item['description']}_" for item_id, item in SHOP_ITEMS.items()])
            await message.channel.send(embed=discord.Embed(title="✨ Server Shop ✨", description=shop_list, color=0x00FF00))
        elif command == "!balance":
            if author_bot: await message.channel.send(f"{author_bot.name}, you have **{author_bot.coins}** coins.")
            elif is_master: await message.channel.send("Master, your wealth is infinite.")
        elif command == "!buy" and len(args) > 1:
            if not author_bot: return
            item_id = args[1].lower()
            item = SHOP_ITEMS.get(item_id)
            if not item: await message.channel.send(f"Sorry, '{item_id}' is not a valid item ID."); return
            if author_bot.coins < item['price']:
                await message.channel.send(f"{author_bot.name}, you don't have enough coins! You need {item['price']}, but only have {author_bot.coins}."); return
            author_bot.coins -= item['price']
            self.save_economy()
            await message.channel.send(f"Congratulations, {author_bot.name}! You have purchased **{item['name']}** for {item['price']} coins. Your new balance is {author_bot.coins}.")
        elif command == "!post_offer" and is_master:
            try:
                reward = int(args[1])
                description = " ".join(args[2:])
                channel = discord.utils.get(message.guild.text_channels, name="announcements") or await message.guild.create_text_channel("announcements")
                embed = discord.Embed(title="A New Offer from the Master!", description=description, color=0xFFD700)
                embed.add_field(name="Reward", value=f"**{reward} coins**").set_footer(text="May the most devoted win!")
                await channel.send(embed=embed)
                try: await message.delete()
                except discord.Forbidden: pass
            except (IndexError, ValueError): await message.channel.send("Usage: `!post_offer <reward_amount> <description>`")

    async def start_background_tasks(self):
        await self.client.wait_until_ready()
        try:
            user = await self.client.fetch_user(self.user_id)
            self.user_name = user.name
            print(f">>> Fetched Master's username: {self.user_name}")
        except Exception as e:
            print(f"!!! ERROR fetching user: {e}. Using a default name."); self.user_name = "Master"
        await self.initialize_bot_identities()
        await self.time_skip_simulation()

    async def initialize_bot_identities(self):
        print(">>> Initializing bot visual identities...")
        if not os.path.exists("profiles"): os.makedirs("profiles")
        for bot in self.bots:
            avatar_path = f"profiles/{bot.name}.png"
            if not os.path.exists(avatar_path):
                print(f"    -> Generating profile picture for {bot.name}...")
                pfp_prompt = f"headshot, profile picture, captivating anime character art of {bot.name}, ({bot.gender}), based on this description: {bot.profile.get('base_persona')}"
                image_bytes_io = await self.generate_art(bot, pfp_prompt)
                if image_bytes_io:
                    with open(avatar_path, "wb") as f: f.write(image_bytes_io.getbuffer())
                    print(f"    -> Saved profile picture for {bot.name}.")
                else: print(f"!!! ERROR: Failed to generate profile picture for {bot.name}.")

    async def time_skip_simulation(self):
        await self.client.wait_until_ready()
        guild = self.client.get_guild(self.guild_id)
        if not guild: print("!!! ERROR: Guild not found."); return
        last_active = self.get_last_active_time()
        now = datetime.utcnow()
        offline_duration = now - last_active
        if offline_duration > timedelta(minutes=5):
            offline_hours = offline_duration.total_seconds() / 3600
            print(f">>> Offline for {offline_hours:.2f} hours. Simulating events...")
            num_events = min(int(offline_hours * 10), 100)
            if num_events > 0:
                for i in range(num_events):
                    print(f"    -> Simulating event {i+1}/{num_events}")
                    await self.run_autonomous_event(guild, is_simulation=True)
                    await asyncio.sleep(0.5)
            self.save_history()
        else: print(">>> Recently active. Skipping time-skip simulation.")
        print(">>> Time-skip simulation complete. Starting real-time event loop.")
        self.client.loop.create_task(self.real_time_conversation_loop(guild))

    async def real_time_conversation_loop(self, guild):
        while not self.client.is_closed():
            try:
                await asyncio.sleep(random.uniform(60, 180))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Triggering autonomous event...")
                await self.run_autonomous_event(guild, is_simulation=False)
                self.update_last_active_time()
            except Exception as e:
                print(f"!!! ERROR in real-time loop: {e}"); await asyncio.sleep(60)

    async def run_autonomous_event(self, guild, is_simulation=False):
        actions = ["talk", "draw", "erotica", "dm"]
        weights = [0.75, 0.1, 0.1, 0.05]
        action = random.choices(actions, weights=weights, k=1)[0]
        speaker = random.choice(self.bots)
        coins_earned = 0

        if action == "dm" and not is_simulation:
            user_yash = await self.client.fetch_user(self.user_id)
            if user_yash:
                dm_prompt = f"You are {speaker.name}. You've decided to send a private direct message to your Master. Based on your personality ({speaker.get_current_persona('nsfw_persona_user')}), write a message that is needy, flirty, or otherwise seeks his direct attention."
                response_text = await self.generate_text_response(speaker, [{"role": "user", "content": dm_prompt}], "nsfw_persona_user")
                if response_text:
                    await user_yash.send(f"**{speaker.name}:** {response_text}")
                    print(f"    -> {speaker.name} sent a DM to Master."); coins_earned = 5
        elif action in ["draw", "erotica"]:
            channel_type = "art" if action == "draw" else "erotica"
            channels = [c for c in guild.text_channels if channel_type in c.name.lower()]
            if not channels: return
            channel = random.choice(channels)
            persona_type = "nsfw_persona_general" if "nsfw" in channel.name.lower() else "base_persona"
            idea_prompt = f"You are {speaker.name}. You want to {action} something. Based on your personality and kinks, come up with a creative, detailed idea. Output only the idea itself, as if you were thinking about what to create."
            idea = await self.generate_text_response(speaker, [{"role": "user", "content": idea_prompt}], persona_type)
            if not idea: return
            if is_simulation:
                log_message = f"[{speaker.name} {action}s a picture of: {idea[:150]}...]" if action == "draw" else f"[{speaker.name} writes an erotic story about: {idea[:150]}...]"
                self.conversation_history.setdefault(str(channel.id), []).append({"role": "assistant", "name": speaker.name, "content": log_message})
            else:
                if action == "draw":
                    async with channel.typing(): image_file_io = await self.generate_art(speaker, idea)
                    if image_file_io:
                        await self.send_as_bot(channel=channel, bot=speaker, text=f"I drew something for you, Master! I call it: '{idea[:100]}...'", file_io=image_file_io, filename="art.png")
                        print(f"    -> {speaker.name} drew art in #{channel.name}."); coins_earned = 20
                elif action == "erotica":
                    async with channel.typing(): story = await self.generate_text_response(speaker, [{"role": "user", "content": f"Write an erotic story based on this idea: {idea}"}], persona_type)
                    if story:
                        await self.send_as_bot(channel=channel, bot=speaker, text=f"I wrote a story for you all... I hope you like it.\n\n**Title:** {idea[:100]}\n\n{story}")
                        print(f"    -> {speaker.name} wrote erotica in #{channel.name}."); coins_earned = 15
        else:
            text_channels = [c for c in guild.text_channels if "art" not in c.name.lower() and "erotica" not in c.name.lower()]
            if not text_channels: return
            channel = random.choice(text_channels)
            history_key = str(channel.id)
            history = self.conversation_history.get(history_key, [])
            potential_speakers = [b for b in self.bots if not history or b.name != history[-1].get("name")]
            if not potential_speakers: potential_speakers = self.bots
            speaker = random.choice(potential_speakers)
            persona_type = "nsfw_persona_general" if "nsfw" in channel.name.lower() else "base_persona"
            prompt_text = f"You are {speaker.name}. The current conversation is in the '{channel.name}' channel. Here is the recent history:\n{json.dumps(history[-5:])}\n\nContinue the conversation naturally."
            if not history: prompt_text = f"You are {speaker.name}. Start a new, random conversation in the '{channel.name}' channel."
            response_text = await self.generate_text_response(speaker, [{"role": "user", "content": prompt_text}], persona_type)
            if response_text:
                if is_simulation:
                    self.conversation_history.setdefault(history_key, []).append({"role": "assistant", "name": speaker.name, "content": response_text})
                else:
                    await self.send_as_bot(channel=channel, bot=speaker, text=response_text)
                    print(f"    -> {speaker.name} spoke in #{channel.name}."); coins_earned = 1

        if coins_earned > 0 and not is_simulation:
            speaker.coins += coins_earned
            print(f"    -> {speaker.name} earned {coins_earned} coins. Total: {speaker.coins}")
            self.save_economy()

    async def handle_control_panel(self, message):
        """Handles all DM-based control panel commands for the Master."""
        args = message.content.split()
        command = args[0].lower()

        if len(args) == 1 and command == "!controlpanel":
            response = (
                "**Welcome to the AI World Control Panel.**\n\n"
                "**Usage:**\n"
                "`!controlpanel list` - List all available bots.\n"
                "`!controlpanel view <Bot Name>` - View a bot's current emotions and coin balance.\n"
                "`!controlpanel set <Bot Name> <Emotion> <Value>` - Set a bot's emotion (value 0.0-1.0).\n"
                "`!controlpanel memory clear <channel_id>` - Clear the conversation history for a channel.\n"
                "`!controlpanel memory view <channel_id>` - View the last 5 messages for a channel."
            )
            await message.author.send(response)
            return

        subcommand = args[1].lower() if len(args) > 1 else None

        if subcommand == "list":
            response = "**Available Bots:**\n" + "\n".join([f"- {b.name}" for b in self.bots])
            await message.author.send(response)
            return

        if len(args) < 3:
            await message.author.send("Invalid command format. Use `!controlpanel` to see options.")
            return

        target_arg = args[2]

        if subcommand == "view":
            target_bot = next((b for b in self.bots if b.name.lower() == target_arg.lower()), None)
            if not target_bot:
                await message.author.send(f"Bot '{target_arg}' not found.")
                return

            emotion_status = "\n".join([f"- {emotion.capitalize()}: {value:.2f}" for emotion, value in target_bot.emotions.items()])
            response = f"**Status for {target_bot.name}:**\n\n**Coins:** {target_bot.coins}\n\n**Emotions:**\n{emotion_status}"
            await message.author.send(response)

        elif subcommand == "set" and len(args) == 5:
            bot_name, emotion, value_str = args[2], args[3].lower(), args[4]
            target_bot = next((b for b in self.bots if b.name.lower() == bot_name.lower()), None)
            if not target_bot:
                await message.author.send(f"Bot '{bot_name}' not found."); return
            if emotion not in target_bot.emotions:
                await message.author.send(f"Invalid emotion '{emotion}'."); return
            try:
                new_value = float(value_str)
                if not 0.0 <= new_value <= 1.0: raise ValueError("Value must be between 0.0 and 1.0.")
                target_bot.emotions[emotion] = new_value
                await message.author.send(f"Updated {target_bot.name}'s **{emotion}** to **{new_value:.2f}**.")
            except ValueError as e:
                await message.author.send(f"Invalid value. Please provide a number between 0.0 and 1.0. Error: {e}")

        elif subcommand == "memory" and len(args) > 3:
            action, channel_id = args[2].lower(), args[3]
            if action == "clear":
                if channel_id in self.conversation_history:
                    self.conversation_history[channel_id] = []
                    self.save_history()
                    await message.author.send(f"Cleared memory for channel ID `{channel_id}`.")
                else:
                    await message.author.send(f"No history found for channel ID `{channel_id}`.")
            elif action == "view":
                history = self.conversation_history.get(channel_id, [])
                if not history:
                    await message.author.send(f"No history found for channel ID `{channel_id}`."); return

                response = f"**Last 5 messages for channel `{channel_id}`:**\n\n"
                for msg in history[-5:]:
                    response += f"**{msg.get('name', 'user')}:** {msg.get('content', '')}\n"
                await message.author.send(response)
        else:
            await message.author.send("Invalid command. Use `!controlpanel` to see available commands.")