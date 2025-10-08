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
            {"name": "Festival of Lights", "description": "A week-long festival of lights begins! Joy and celebration fill the air, and special goods appear in the market.", "effects": {"happiness": 20}},
            {"name": "Sudden Monsoon", "description": "A heavy monsoon sweeps across the land, making travel difficult and causing prices for food to rise.", "effects": {"happiness": -10, "loneliness": 10}},
            {"name": "Economic Boom", "description": "A trade caravan has arrived, flush with foreign currency! All job payouts are doubled for the next 24 hours.", "effects": {"job_multiplier": 2}},
            {"name": "Mysterious Plague", "description": "A strange sickness is spreading. The Healers are working overtime, but many are falling ill.", "effects": {"sanity": -15}},
            {"name": "Auspicious Alignment", "description": "The stars have aligned in a favorable position. All artistic and creative endeavors are blessed with inspiration.", "effects": {"creativity_boost": True}},
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
            # Wait for a random duration (e.g., 6 to 24 hours)
            await asyncio.sleep(random.randint(21600, 86400))

            # Select and trigger a new event
            event_data = random.choice(self.possible_events)
            self.current_event = event_data

            # Announce the event
            announcement = f"**WORLD EVENT: {event_data['name']}**\n\n{event_data['description']}"
            await self.bot.send_to_event_channel(announcement)
            print(f"[EventAI] Started new event: {event_data['name']}")

            # Apply global effects to all personas
            if "effects" in event_data:
                for persona in self.bot.persona_manager.get_all_personas():
                    for effect, value in event_data['effects'].items():
                        if effect in persona.emotions:
                            persona.adjust_emotion(effect, value)

            # The event itself doesn't have a duration in this simple model,
            # a new one just replaces it. A more complex system could have durations.

    async def trigger_manual_event(self, event_name, channel):
        """Allows the Master to manually trigger an event."""
        event_data = next((event for event in self.possible_events if event['name'].lower() == event_name.lower()), None)
        if not event_data:
            await channel.send(f"Error: Event '{event_name}' not found.")
            return

        self.current_event = event_data
        announcement = f"**MASTER'S DECREE: {event_data['name']}**\n\n{event_data['description']}"
        await self.bot.send_to_event_channel(announcement)
        print(f"[EventAI] Master manually triggered event: {event_data['name']}")

        # Apply effects
        if "effects" in event_data:
            for persona in self.bot.persona_manager.get_all_personas():
                for effect, value in event_data['effects'].items():
                    if effect in persona.emotions:
                        persona.adjust_emotion(effect, value)
        await channel.send(f"Successfully triggered the **{event_data['name']}** event.")