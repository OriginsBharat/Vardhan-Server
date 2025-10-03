import httpx
import os
import json
import asyncio
import random
import discord
import base64
from io import BytesIO
from bot_profiles import PROFILES
from datetime import datetime, timedelta

class BotManager:
    def __init__(self, client):
        self.client = client
        self.bots = []
        self.load_bots()
        self.ollama_api_url = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
        self.sd_api_url = os.getenv("SD_API_URL", "http://127.0.0.1:7860")
        self.model = os.getenv("LLM_MODEL")
        self.guild_id = int(os.getenv("DISCORD_GUILD_ID"))
        self.user_id = int(os.getenv("USER_ID"))
        self.webhooks = {}
        self.history_file = "conversation_history.json"
        self.last_active_file = "last_active.txt"
        self.conversation_history = self.load_history()

    def load_bots(self):
        for profile in PROFILES:
            self.bots.append(BotInstance(profile, self))
        print(f"Loaded {len(self.bots)} bot profiles.")

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
        if channel.id in self.webhooks and bot_name in self.webhooks[channel.id]: return self.webhooks[channel.id][bot_name]
        webhooks = await channel.webhooks()
        for wh in webhooks:
            if wh.name == bot_name:
                if channel.id not in self.webhooks: self.webhooks[channel.id] = {}
                self.webhooks[channel.id][bot_name] = wh; return wh
        new_wh = await channel.create_webhook(name=bot_name)
        if channel.id not in self.webhooks: self.webhooks[channel.id] = {}
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
        payload = {"prompt": f"anime style, {prompt_text}", "negative_prompt": "low quality, worst quality", "steps": 25}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(f"{self.sd_api_url}/sdapi/v1/txt2img", json=payload); r.raise_for_status()
                return BytesIO(base64.b64decode(r.json()['images'][0]))
        except Exception as e: print(f"Error generating art: {e}"); return None

    async def send_as_bot(self, channel, bot, text=None, file=None):
        webhook = await self.get_webhook(channel, bot.name)
        message = await webhook.send(content=text, file=file, wait=True)
        if text:
            history_key = str(channel.id)
            if history_key not in self.conversation_history: self.conversation_history[history_key] = []
            self.conversation_history[history_key].append({"role": "assistant", "name": bot.name, "content": text})
            self.save_history()
        return message

    async def handle_control_panel(self, message):
        # ... (same as before) ...
        pass

    async def handle_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author.id == self.user_id and message.content.startswith("!"):
            await self.handle_control_panel(message)
            return

        if message.webhook_id: return
        history_key = str(message.channel.id)
        if history_key not in self.conversation_history: self.conversation_history[history_key] = []
        self.conversation_history[history_key].append({"role": "user", "name": message.author.name, "content": message.content}); self.save_history()
        history = self.conversation_history[history_key][-10:]

        mentioned_bots = [b for b in self.bots if b.name.lower() in message.content.lower()]
        responder = random.choice(mentioned_bots) if mentioned_bots else None
        if not responder and random.random() < 0.5:
             potential_responders = [b for b in self.bots if b.name.lower() != message.author.name.lower()]
             if potential_responders: responder = random.choice(potential_responders)
        if not responder: return

        is_nsfw = "nsfw" in message.channel.name.lower() or "kinks" in message.channel.name.lower()
        persona = "nsfw_persona_user" if message.author.id == self.user_id and is_nsfw else ("nsfw_persona_general" if is_nsfw else "base_persona")

        async with message.channel.typing(): response_text = await self.generate_text_response(responder, history, persona)
        if response_text: await self.send_as_bot(message.channel, responder, text=response_text)

    async def start_background_tasks(self):
        self.client.loop.create_task(self.time_skip_simulation())
        # The trial check loop can be added here later if needed

    async def time_skip_simulation(self):
        await self.client.wait_until_ready()
        guild = self.client.get_guild(self.guild_id)
        if not guild: return

        last_active = self.get_last_active_time()
        now = datetime.utcnow()
        offline_duration_hours = (now - last_active).total_seconds() / 3600

        print(f"Offline for {offline_duration_hours:.2f} hours. Running time-skip simulation...")

        # Simulate events for every hour the bot was offline (max 24 hours to avoid spam)
        num_events = min(int(offline_duration_hours), 24)
        if num_events > 0:
            print(f"Simulating {num_events} events...")
            for _ in range(num_events):
                await self.run_autonomous_event(guild, is_simulation=True)
                await asyncio.sleep(1) # Small delay to prevent rate limiting

        print("Time-skip simulation complete. Starting real-time loop.")
        self.client.loop.create_task(self.real_time_conversation_loop(guild))

    async def real_time_conversation_loop(self, guild):
        while not self.client.is_closed():
            try:
                await self.run_autonomous_event(guild, is_simulation=False)
                self.update_last_active_time()
                await asyncio.sleep(random.uniform(30, 90))
            except Exception as e:
                print(f"Error in real-time loop: {e}")
                await asyncio.sleep(60)

    async def run_autonomous_event(self, guild, is_simulation=False):
        """Runs a single autonomous event (talk, draw, etc.)."""
        all_channels = guild.text_channels
        action = random.choices(["talk", "draw", "dm"], weights=[0.7, 0.1, 0.2], k=1)[0]
        speaker = random.choice(self.bots)

        if action == "dm":
            user_yash = await self.client.fetch_user(self.user_id)
            if user_yash:
                dm_prompt = f"You are {speaker.name}. You've decided to send a private direct message to your master, Yashvardhan. Based on your personality and your specific NSFW persona for him, write a message that is needy, flirty, or otherwise seeks his direct attention."
                response_text = await self.generate_text_response(speaker, [{"role": "user", "content": dm_prompt}], "nsfw_persona_user")
                if response_text and not is_simulation: await user_yash.send(f"**{speaker.name}:** {response_text}")

        elif action == "draw":
            art_channels = [c for c in all_channels if "art" in c.name.lower()]
            if art_channels:
                channel = random.choice(art_channels)
                persona_type = "nsfw_persona_general" if "nsfw" in channel.name.lower() else "base_persona"
                prompt_creation_prompt = f"You are {speaker.name}, an artist with a flair for anime style. Based on your personality ({persona_type}), come up with a creative, detailed text prompt for an image you want to draw. Only output the prompt itself, nothing else."
                art_prompt = await self.generate_text_response(speaker, [{"role": "user", "content": prompt_creation_prompt}], persona_type)
                if art_prompt:
                    if not is_simulation:
                        async with channel.typing(): image_file = await self.generate_art(speaker, art_prompt)
                        if image_file: await self.send_as_bot(channel, speaker, text=f"I drew something! '{art_prompt[:100]}...'", file=discord.File(image_file, filename="art.png"))
                    else: # In simulation, just log the idea
                        self.conversation_history.setdefault(str(channel.id), []).append({"role": "assistant", "name": speaker.name, "content": f"[Drew a picture of: {art_prompt[:150]}...]"})

        else: # action == "talk"
            channel = random.choice(all_channels)
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
                    else: self.conversation_history.setdefault(history_key, []).append({"role": "assistant", "name": speaker.name, "content": response_text})

class BotInstance:
    def __init__(self, profile, manager):
        self.name = profile["name"]
        self.profile = profile
        self.manager = manager
        self.emotions = profile.get("default_emotions", {}).copy()

    def get_current_persona(self, persona_type):
        base_persona = self.profile.get(persona_type, self.profile["base_persona"])
        emotion_str = " ".join([f"Your current {emotion} level is {value}." for emotion, value in self.emotions.items()])
        return f"{base_persona} {emotion_str}"

    def __str__(self):
        return self.name