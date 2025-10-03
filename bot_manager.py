import httpx, os, json, asyncio, random, discord, base64
from io import BytesIO
from bot_profiles import PROFILES
from datetime import datetime
from economy_manager import EconomyManager
from TTS.api import TTS

class BotManager:
    def __init__(self, client):
        self.client = client; self.bots = []; self.load_bots()
        self.ollama_api_url = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
        self.sd_api_url = os.getenv("SD_API_URL", "http://127.0.0.1:8188")
        self.model = os.getenv("LLM_MODEL")
        self.guild_id = int(os.getenv("DISCORD_GUILD_ID"))
        self.user_id = int(os.getenv("USER_ID"))
        self.webhooks = {}
        self.history_file = "conversation_history.json"
        self.last_active_file = "last_active.txt"
        self.conversation_history = self.load_history()
        self.economy_manager = EconomyManager()

        # Initialize the XTTS Voice Model
        try:
            print("🔊 Initializing Coqui XTTS voice model... This may take a moment.")
            self.tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            print("✅ XTTS voice model loaded successfully.")
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Could not load Coqui XTTS model. Voice generation will be disabled. Error: {e}")
            self.tts_model = None

    def load_bots(self):
        for profile in PROFILES: self.bots.append(BotInstance(profile, self))
        print(f">>> Loaded {len(self.bots)} bot profiles.")

    def load_history(self):
        try:
            with open(self.history_file, 'r') as f: return json.load(f)
        except: return {}

    def save_history(self):
        with open(self.history_file, 'w') as f: json.dump(self.conversation_history, f, indent=4)

    def get_last_active_time(self):
        try:
            with open(self.last_active_file, 'r') as f: return datetime.fromisoformat(f.read())
        except: return datetime.utcnow()

    def update_last_active_time(self):
        with open(self.last_active_file, 'w') as f: f.write(datetime.utcnow().isoformat())

    async def get_webhook(self, channel, bot_name):
        if channel.id not in self.webhooks: self.webhooks[channel.id] = {}
        if bot_name in self.webhooks[channel.id]: return self.webhooks[channel.id][bot_name]
        webhooks = await channel.webhooks()
        for wh in webhooks:
            if wh.name == bot_name: self.webhooks[channel.id][bot_name] = wh; return wh
        new_wh = await channel.create_webhook(name=bot_name)
        self.webhooks[channel.id][bot_name] = new_wh; return new_wh

    async def generate_text_response(self, bot, history, persona_type):
        system_prompt = bot.get_current_persona(persona_type)
        prompt = {"model": self.model, "stream": False, "messages": [{"role": "system", "content": system_prompt}] + history}
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                r = await client.post(f"{self.ollama_api_url}/api/chat", json=prompt); r.raise_for_status()
                return r.json()["message"]["content"]
        except Exception as e: print(f"Error generating text: {e}"); return None

    async def generate_art(self, bot, prompt_text):
        workflow = {
            "3": { "class_type": "KSampler", "inputs": { "seed": random.randint(0, 18446744073709551615), "steps": 25, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0] } },
            "4": { "class_type": "CheckpointLoaderSimple", "inputs": { "ckpt_name": "v1-5-pruned-emaonly.safetensors" } },
            "5": { "class_type": "EmptyLatentImage", "inputs": { "width": 512, "height": 512, "batch_size": 1 } },
            "6": { "class_type": "CLIPTextEncode", "inputs": { "text": f"anime style, masterpiece, best quality, {prompt_text}", "clip": ["4", 1] } },
            "7": { "class_type": "CLIPTextEncode", "inputs": { "text": "low quality, worst quality, bad hands, text, error, blurry, deformed", "clip": ["4", 1] } },
            "8": { "class_type": "VAEDecode", "inputs": { "samples": ["3", 0], "vae": ["4", 2] } }
        }
        prompt_payload = {"prompt": workflow, "client_id": "AIWorldBot"}
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                res = await client.post(f"{self.sd_api_url}/prompt", json=prompt_payload)
                res.raise_for_status()
                prompt_id = res.json()['prompt_id']
                while True:
                    history_res = await client.get(f"{self.sd_api_url}/history/{prompt_id}")
                    history_res.raise_for_status()
                    history = history_res.json()
                    if prompt_id in history and history[prompt_id]['outputs']:
                        image_info = history[prompt_id]['outputs']['8']['images'][0]
                        break
                    await asyncio.sleep(2)
                image_res = await client.get(f"{self.sd_api_url}/view?filename={image_info['filename']}&subfolder={image_info.get('subfolder', '')}&type={image_info['type']}")
                image_res.raise_for_status()
                return BytesIO(image_res.content)
        except Exception as e:
            print(f"Error generating art with ComfyUI: {e}")
            return None

    async def send_as_bot(self, channel, bot, text=None, file=None):
        webhook = await self.get_webhook(channel, bot.name)
        await webhook.send(content=text, file=file, wait=True)
        if text:
            history_key = str(channel.id)
            if history_key not in self.conversation_history: self.conversation_history[history_key] = []
            self.conversation_history[history_key].append({"role": "assistant", "name": bot.name, "content": text})
            self.save_history()

    async def handle_control_panel(self, message):
        args = message.content.split()
        if len(args) == 1:
            response = "Welcome to the Bot Control Panel. To view a bot's emotions, use `!controlpanel <Bot Name>`.\n\n**Available Bots:**\n" + "\n".join([f"- {b.name}" for b in self.bots])
            await message.author.send(response)
            return
        bot_name_arg = args[1]
        target_bot = next((b for b in self.bots if b.name.lower() == bot_name_arg.lower()), None)
        if not target_bot:
            await message.author.send(f"Bot '{bot_name_arg}' not found.")
            return
        if len(args) == 2:
            emotion_status = "\n".join([f"- {emotion.capitalize()}: {value}" for emotion, value in target_bot.emotions.items()])
            response = f"**Current Emotions for {target_bot.name}:**\n{emotion_status}\n\nTo change an emotion, use `!controlpanel {target_bot.name} <Emotion> <Value>` (e.g., `!controlpanel {target_bot.name} arousal 0.9`)."
            await message.author.send(response)
            return
        if len(args) == 4:
            emotion_arg = args[2].lower()
            value_arg = args[3]
            if emotion_arg not in target_bot.emotions:
                await message.author.send(f"Invalid emotion '{emotion_arg}'. Available emotions: {', '.join(target_bot.emotions.keys())}")
                return
            try:
                new_value = float(value_arg)
                if not 0.0 <= new_value <= 1.0: raise ValueError("Value must be between 0.0 and 1.0.")
                target_bot.emotions[emotion_arg] = new_value
                await message.author.send(f"Updated {target_bot.name}'s **{emotion_arg}** to **{new_value}**.")
            except ValueError as e:
                await message.author.send(f"Invalid value. Please provide a number between 0.0 and 1.0. Error: {e}")
            return
        await message.author.send("Invalid command format. Use `!controlpanel`, `!controlpanel <Bot Name>`, or `!controlpanel <Bot Name> <Emotion> <Value>`.")

    async def handle_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author.id == self.user_id and message.content.startswith("!"):
            await self.handle_control_panel(message); return
        if message.content.lower().strip() == '!economy':
            actor_bot = random.choice(self.bots)
            response = "**World Economic Report:**\n\n**Bot Balances:**\n"
            for bot_name, balance in self.economy_manager.data['bot_wallets'].items():
                response += f"- {bot_name}: {balance} currency\n"
            response += "\n**Shop Inventory:**\n"
            shop_items = self.economy_manager.get_shop_items()
            if shop_items:
                for item, details in shop_items.items():
                    response += f"- **{item}** ({details['price']} currency): {details['description']}\n"
            else:
                response += "The shop is currently empty.\n"
            await self.send_as_bot(message.channel, actor_bot, text=response)
            return
        history_key = str(message.channel.id)
        if history_key not in self.conversation_history: self.conversation_history[history_key] = []
        self.conversation_history[history_key].append({"role": "user", "name": message.author.name, "content": message.content}); self.save_history()
        history = self.conversation_history[history_key][-10:]
        mentioned_bots = [b for b in self.bots if b.name.lower() in message.content.lower()]
        responder = random.choice(mentioned_bots) if mentioned_bots else (random.choice([b for b in self.bots if b.name.lower() != message.author.name.lower()]) if random.random() < 0.5 else None)
        if not responder: return
        is_nsfw = "nsfw" in message.channel.name.lower() or "kinks" in message.channel.name.lower()
        persona = "nsfw_persona_user" if message.author.id == self.user_id and is_nsfw else ("nsfw_persona_general" if is_nsfw else "base_persona")
        async with message.channel.typing(): response_text = await self.generate_text_response(responder, history, persona)
        if response_text:
            await self.send_as_bot(message.channel, responder, text=response_text)
            if message.author.voice and message.author.voice.channel:
                await self.play_tts(message.author.voice.channel, response_text, responder.name)

    async def play_tts(self, voice_channel, text, speaker_name):
        if not self.tts_model:
            print("🔊 TTS playback skipped: XTTS model not available.")
            return
        if not voice_channel: return
        vc = discord.utils.get(self.client.voice_clients, guild=voice_channel.guild)
        if vc and vc.is_playing():
            print("🔊 TTS request ignored, bot is currently speaking.")
            return
        try:
            speaker_wav_path = os.path.join("voices", f"{speaker_name}.wav")
            output_tts_file = "tts_output.wav"
            if os.path.exists(speaker_wav_path):
                print(f"🎤 Found custom voice for {speaker_name}. Generating speech...")
                self.tts_model.tts_to_file(text=text, speaker_wav=speaker_wav_path, language="en", file_path=output_tts_file)
            else:
                print(f"🎤 No custom voice for {speaker_name} found. Using default voice.")
                self.tts_model.tts_to_file(text=text, language="en", file_path=output_tts_file)
            print("  > Speech generation complete.")
            if not (vc and vc.is_connected()): vc = await voice_channel.connect()
            elif vc.channel != voice_channel: await vc.move_to(voice_channel)
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=output_tts_file))
            while vc.is_playing(): await asyncio.sleep(1)
            await vc.disconnect()
            if os.path.exists(output_tts_file): os.remove(output_tts_file)
        except Exception as e:
            print(f"❌ Error during XTTS playback: {e}")
            if 'vc' in locals() and vc and vc.is_connected(): await vc.disconnect()
            if os.path.exists("tts_output.wav"): os.remove("tts_output.wav")

    async def start_background_tasks(self):
        await self.time_skip_simulation()

    async def time_skip_simulation(self):
        await self.client.wait_until_ready()
        guild = self.client.get_guild(self.guild_id)
        if not guild: return
        last_active = self.get_last_active_time()
        now = datetime.utcnow()
        offline_duration_hours = (now - last_active).total_seconds() / 3600
        print(f">>> Offline for {offline_duration_hours:.2f} hours. Simulating events...")
        num_events = min(int(offline_duration_hours * 10), 100)
        if num_events > 0:
            for i in range(num_events):
                print(f"    -> Simulating event {i+1}/{num_events}")
                await self.run_autonomous_event(guild, is_simulation=True)
                await asyncio.sleep(0.2)
        print(">>> Time-skip simulation complete. Starting real-time loop.")
        self.client.loop.create_task(self.real_time_conversation_loop(guild))

    async def real_time_conversation_loop(self, guild):
        while not self.client.is_closed():
            try:
                await self.run_autonomous_event(guild, is_simulation=False)
                self.update_last_active_time()
                await asyncio.sleep(random.uniform(30, 90))
            except Exception as e: print(f"Error in real-time loop: {e}"); await asyncio.sleep(60)

    async def run_autonomous_event(self, guild, is_simulation=False):
        action = random.choices(["talk", "draw", "dm", "work", "shop"], weights=[0.6, 0.1, 0.1, 0.1, 0.1], k=1)[0]
        speaker = random.choice(self.bots)
        if action == "dm":
            user_yash = await self.client.fetch_user(self.user_id)
            if user_yash and not is_simulation:
                dm_prompt = f"You are {speaker.name}. Send a private DM to your Master, based on your personality."
                response_text = await self.generate_text_response(speaker, [{"role": "user", "content": dm_prompt}], "nsfw_persona_user")
                if response_text: await user_yash.send(f"**{speaker.name}:** {response_text}")
        elif action == "work":
            channel = random.choice(guild.text_channels)
            salary = self.economy_manager.grant_salary(speaker.name)
            if salary > 0 and not is_simulation:
                await self.send_as_bot(channel, speaker, text=f"I did some work and earned {salary} currency. My new balance is {self.economy_manager.get_balance(speaker.name)}.")
        elif action == "shop":
            channel = random.choice(guild.text_channels)
            shop_items = self.economy_manager.get_shop_items()
            if shop_items and not is_simulation:
                item_to_buy = random.choice(list(shop_items.keys()))
                purchase_result = self.economy_manager.buy_item(speaker.name, item_to_buy)
                await self.send_as_bot(channel, speaker, text=purchase_result)
        elif action == "draw":
            art_channels = [c for c in guild.text_channels if "art" in c.name.lower()]
            if art_channels:
                channel = random.choice(art_channels)
                persona_type = "nsfw_persona_general" if "nsfw" in channel.name.lower() else "base_persona"
                prompt_creation_prompt = f"You are {speaker.name}, an anime artist. Create a prompt for an image. Only output the prompt."
                art_prompt = await self.generate_text_response(speaker, [{"role": "user", "content": prompt_creation_prompt}], persona_type)
                if art_prompt:
                    if not is_simulation:
                        async with channel.typing(): image_file = await self.generate_art(speaker, art_prompt)
                        if image_file: await self.send_as_bot(channel, speaker, text=f"I drew: '{art_prompt[:100]}...'", file=discord.File(image_file, filename="art.png"))
                    else:
                        self.conversation_history.setdefault(str(channel.id), []).append({"role": "assistant", "name": speaker.name, "content": f"[Drew a picture of: {art_prompt[:150]}...]"}); self.save_history()
        else: # action == "talk"
            channel = random.choice(guild.text_channels)
            history_key = str(channel.id)
            history = self.conversation_history.get(history_key, [])
            potential_speakers = [b for b in self.bots if not history or b.name != history[-1]["name"]]
            if potential_speakers:
                speaker = random.choice(potential_speakers)
                persona_type = "nsfw_persona_general" if "nsfw" in channel.name.lower() else "base_persona"
                prompt_text = f"You are {speaker.name}. Continue the conversation in '{channel.name}'. History:\n{json.dumps(history[-5:])}" if history else f"You are {speaker.name}. Start a random conversation in '{channel.name}'."
                response_text = await self.generate_text_response(speaker, [{"role": "user", "content": prompt_text}], persona_type)
                if response_text:
                    if not is_simulation: await self.send_as_bot(channel, speaker, text=response_text)
                    else: self.conversation_history.setdefault(history_key, []).append({"role": "assistant", "name": speaker.name, "content": response_text}); self.save_history()

class BotInstance:
    def __init__(self, profile, manager):
        self.name = profile["name"]; self.profile = profile; self.manager = manager
        self.emotions = profile.get("default_emotions", {}).copy()

    def get_current_persona(self, persona_type):
        base_persona = self.profile.get(persona_type, self.profile["base_persona"])
        emotion_str = " ".join([f"Your current {emotion} level is {value}." for emotion, value in self.emotions.items()])
        kink_str = "Your main kinks are: " + ", ".join(self.profile.get("kinks", []))
        balance_str = f"Your current wallet balance is {self.manager.economy_manager.get_balance(self.name)} currency."
        return f"{base_persona} {emotion_str} {kink_str} {balance_str}"