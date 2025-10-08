import asyncio
import random

class EventAI:
    """
    The 'Director' of the world. Autonomously generates server-wide events
    to create dynamic storylines and situations for the bots to react to.
    """
    def __init__(self, bot):
        self.bot = bot
        self.possible_events = [
            {"name": "Festival of Colors", "description": "A week-long festival of colors begins! Joy and celebration fill the air, and special goods appear in the market.", "effects": {"happiness": 25, "loneliness": -10}},
            {"name": "Whispering Plague", "description": "A strange, mind-altering sickness is spreading. Sanity frays and paranoia creeps into the hearts of the populace.", "effects": {"sanity": -20, "sadness": 15}},
            {"name": "Economic Boom", "description": "A trade caravan from a distant land has arrived, flush with gold! All job payouts are doubled for the next 24 hours.", "effects": {"job_multiplier": 2}},
            {"name": "Blood Moon", "description": "A crimson moon hangs in the sky, awakening primal urges. Lust and aggression are heightened.", "effects": {"lust": 30, "anger": 15}},
            {"name": "Auspicious Alignment", "description": "The stars have aligned in a favorable position. All artistic and creative endeavors are blessed with profound inspiration.", "effects": {"happiness": 15}},
        ]
        self.current_event = None
        self.event_task = None

    async def start(self):
        """Starts the event generation loop."""
        print("[EventAI] The Director is now watching the world.")
        self.event_task = asyncio.create_task(self._event_loop())

    async def _event_loop(self):
        """The main loop that periodically triggers new events."""
        while True:
            # Wait for a random duration (e.g., 8 to 36 hours)
            await asyncio.sleep(random.randint(28800, 129600))

            # Select and trigger a new event
            await self.trigger_random_event()

    async def trigger_random_event(self):
        """Triggers a random event and applies its effects."""
        event_data = random.choice(self.possible_events)
        self.current_event = event_data

        announcement = f"**WORLD EVENT: {event_data['name']}**\n\n{event_data['description']}"
        await self.bot.send_to_channel("announcements", announcement)
        print(f"[EventAI] Started new event: {event_data['name']}")

        # Apply global effects to all personas
        if "effects" in event_data:
            for persona in self.bot.persona_manager.get_all_personas():
                for effect, value in event_data['effects'].items():
                    if effect in persona.emotions:
                        persona.adjust_emotion(effect, value)

    async def trigger_manual_event(self, event_name, channel):
        """Allows the Master to manually trigger an event."""
        event_data = next((event for event in self.possible_events if event['name'].lower() == event_name.lower().replace("_", " ")), None)
        if not event_data:
            await channel.send(f"Error: Event '{event_name}' not found.")
            return

        self.current_event = event_data
        announcement = f"**MASTER'S DECREE: {event_data['name']}**\n\n{event_data['description']}"
        await self.bot.send_to_channel("announcements", announcement)
        print(f"[EventAI] Master manually triggered event: {event_data['name']}")

        # Apply effects
        if "effects" in event_data:
            for persona in self.bot.persona_manager.get_all_personas():
                for effect, value in event_data['effects'].items():
                    if effect in persona.emotions:
                        persona.adjust_emotion(effect, value)
        await channel.send(f"✅ Successfully triggered the **{event_data['name']}** event.")