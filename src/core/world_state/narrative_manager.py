import logging
import discord
from datetime import datetime

class NarrativeManager:
    """
    Manages the creation and logging of narrative events for the Master's Journal.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.daily_events = []

    def log_event(self, event_text: str, level: str = "normal"):
        """
        Logs a significant event to be included in the daily summary.

        Args:
            event_text: A string describing the event.
            level: The significance level ('normal', 'major', 'critical').
        """
        timestamp = datetime.now().strftime("%H:%M")
        self.daily_events.append(f"({timestamp}, {level.upper()}) - {event_text}")
        self.logger.info(f"Narrative event logged: {event_text}")

    async def generate_and_post_journal(self):
        """
        Generates the daily journal entry using Maya's persona and posts it.
        """
        journal_channel = discord.utils.get(self.bot.get_all_channels(), name="masters-journal")
        if not journal_channel:
            self.logger.warning("Could not find #masters-journal channel to post the daily summary.")
            return

        if not self.daily_events:
            self.logger.info("No significant events today for the Master's Journal.")
            await journal_channel.send("*A quiet day passes in the Vardhan Empire. The world is calm.*")
            return

        self.logger.info("Generating Master's Journal for the day...")

        maya_persona = self.bot.persona_manager.get_persona("Maya")
        if not maya_persona:
            self.logger.error("Could not generate journal: Maya's persona not found.")
            return

        events_str = "\n- ".join(self.daily_events)
        prompt = (
            f"{maya_persona.get_full_prompt()}\n\n"
            "Here are the key events that occurred in the world over the last 24 hours:\n"
            f"- {events_str}\n\n"
            "Based on these events, write a beautiful, insightful, and narrative-style journal entry for the Master. "
            "Recount the day's happenings as a historian or a chronicler, capturing the mood and significance of the events. "
            "Address the entry to the Master."
        )

        journal_text = await self.bot.ollama_client.generate_text(prompt, self.bot.config.llm_model)

        if "Error:" in journal_text or not journal_text:
            self.logger.error(f"Failed to generate journal entry from Ollama: {journal_text}")
            return

        embed = discord.Embed(
            title=f"The Master's Journal: {datetime.now().strftime('%B %d, %Y')}",
            description=journal_text,
            color=maya_persona.aura_color
        )
        embed.set_footer(text="Faithfully recorded by Maya.")

        try:
            await journal_channel.send(embed=embed)
            self.logger.info("Master's Journal posted successfully.")
            self.daily_events.clear()
        except Exception as e:
            self.logger.error(f"Failed to post journal entry: {e}")