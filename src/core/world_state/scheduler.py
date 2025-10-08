import asyncio
import logging
from datetime import datetime, time

class Scheduler:
    """
    Manages the daily schedules and autonomous actions of the bots.
    This creates the illusion of a persistent, 24/7 world.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self._task = None

    def start(self):
        """Starts the main scheduling loop."""
        if self._task is None:
            self._task = asyncio.create_task(self._run_scheduler())
            self.logger.info("Scheduler started.")

    def stop(self):
        """Stops the main scheduling loop."""
        if self._task:
            self._task.cancel()
            self._task = None
            self.logger.info("Scheduler stopped.")

    async def _run_scheduler(self):
        """The main loop that checks schedules every minute."""
        await self.bot.wait_until_ready()
        self.logger.info("Scheduler loop is now running.")
        while not self.bot.is_closed():
            try:
                now = datetime.now().time()

                for persona in self.bot.persona_manager.personas.values():
                    await self.check_and_trigger_action(persona, now)

            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")

            await asyncio.sleep(60) # Check every minute

    async def check_and_trigger_action(self, persona, current_time):
        """
        Checks a persona's schedule and triggers actions if the time matches.
        """
        for event, event_time_str in persona.schedule.items():
            event_time = datetime.strptime(event_time_str, '%H:%M').time()

            # Check if the current time is within a minute of the scheduled event time
            if event_time.hour == current_time.hour and event_time.minute == current_time.minute:
                self.logger.info(f"Triggering '{event}' for {persona.name} at {current_time}.")
                await self.handle_scheduled_event(persona, event)

    async def handle_scheduled_event(self, persona, event_name: str):
        """
        Handles the logic for a specific scheduled event.
        This is where you would define what "work" or "sleep" means.
        """
        # Example: Announce the action in a general channel
        channel = discord.utils.get(self.bot.get_all_channels(), name='general-chat')
        if not channel:
            self.logger.warning("Could not find 'general-chat' to announce schedule event.")
            return

        message = ""
        if event_name == "wake_up":
            message = f"{persona.name} is waking up and starting their day."
            # Here you could modify emotional state, e.g., reset sleepiness
        elif event_name == "go_to_work":
            message = f"{persona.name} is now heading to work."
            # Trigger economic activity
            await self.bot.economy_manager.perform_work(persona)
        elif event_name == "free_time":
            message = f"{persona.name} is now enjoying some free time."
            # Could trigger autonomous interactions, art generation, etc.
        elif event_name == "go_to_sleep":
            message = f"{persona.name} is heading to bed for the night."
            # Modify emotional state for rest

        if message:
            try:
                await channel.send(message)
            except Exception as e:
                self.logger.error(f"Failed to send schedule message for {persona.name}: {e}")