# src/core/world_state/event_ai.py
# Contains the "Event AI" or "Director" responsible for creating world events.

import asyncio
import random
import logging
import discord
from datetime import datetime, timedelta
from typing import List, Optional

from src.config import Config
from src.utils.discord_utils import create_embed

class Event:
    """Represents a single world event."""
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description

class EventAI:
    """
    An autonomous agent that creates and announces server-wide events
    to create dynamic scenarios and stimulate character interaction.
    """
    def __init__(self, config: Config, client: discord.Client):
        self.config = config
        self.client = client
        self.channel_id = self.config.DISCORD_EVENT_CHANNEL_ID
        self.trigger_chance = 0.2 # 20% chance to trigger per cycle
        self.cooldown = timedelta(hours=8) # 8-hour cooldown between events
        self.last_event_time: Optional[datetime] = None
        self.events: List[Event] = self._load_events()
        self._loop_task: Optional[asyncio.Task] = None
        logging.info("EventAI (Director) initialized.")

    def _load_events(self) -> List[Event]:
        """Loads a list of potential events."""
        return [
            Event("A Festival is Announced!", "The city has declared a week-long summer festival! Markets will be bustling and spirits will be high."),
            Event("A Mysterious Sickness", "A strange, magical ailment is spreading, causing minor, unusual symptoms. Alchemists are baffled."),
            Event("Rumors of an Artifact", "Whispers speak of a powerful artifact, lost for centuries, rediscovered in a nearby ruin."),
            Event("A Rare Merchant Arrives", "A traveling merchant known for exotic goods has set up shop in the market square for a limited time."),
            Event("Whispers of War", "Tensions between the two largest kingdoms have reached a boiling point. The threat of war looms."),
            Event("A Bounty is Posted", "The city guard has posted a lucrative bounty for a troublesome beast harassing travelers."),
            Event("An Unnatural Season", "The weather has taken a strange turn, becoming unseasonably cold. Snow falls in mid-summer."),
        ]

    def start_loop(self):
        """Starts the background loop to periodically try and trigger an event."""
        if self._loop_task is None or self._loop_task.done():
            self._loop_task = asyncio.create_task(self._run_event_loop())
            logging.info("EventAI background loop started.")

    async def _run_event_loop(self):
        """The main loop for the Event AI."""
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            # Check every 2 hours
            await asyncio.sleep(7200)

            if self.last_event_time and (datetime.now() - self.last_event_time < self.cooldown):
                logging.info("EventAI is on cooldown. Skipping event trigger.")
                continue

            if random.random() < self.trigger_chance:
                await self.trigger_random_event()
            else:
                logging.info("EventAI decided not to trigger an event this cycle.")

    async def trigger_random_event(self):
        """Selects a random event and announces it in the designated channel."""
        if not self.events:
            logging.warning("No events loaded for EventAI.")
            return

        event = random.choice(self.events)
        channel = self.client.get_channel(self.channel_id)

        if not isinstance(channel, discord.TextChannel):
            logging.error(f"EventAI cannot trigger event: Channel ID {self.channel_id} is not a valid text channel.")
            return

        logging.info(f"EventAI is triggering a new event: {event.title}")

        embed = create_embed(
            title=f"World Event: {event.title}",
            description=event.description,
            color=discord.Color.gold()
        )
        embed.set_footer(text="The world changes... react accordingly.")

        try:
            await channel.send(embed=embed)
            self.last_event_time = datetime.now()
        except (discord.Forbidden, discord.HTTPException) as e:
            logging.error(f"EventAI failed to send event message to channel {self.channel_id}: {e}")