import asyncio
import logging
from datetime import datetime
import discord

class Scheduler:
    """
    Manages daily schedules, autonomous actions, and periodic system checks.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self._task = None
        self.last_default_check_minute = -1
        self.last_neediness_check_minute = -1
        self.last_journal_post_day = -1

    def start(self):
        """Starts the main scheduling loop."""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run_scheduler())
            self.logger.info("Scheduler started.")

    def stop(self):
        """Stops the main scheduling loop."""
        if self._task:
            self._task.cancel()
            self._task = None
            self.logger.info("Scheduler stopped.")

    async def _run_scheduler(self):
        """The main loop that checks schedules and loan defaults."""
        await self.bot.wait_until_ready()
        self.logger.info("Scheduler loop is now running.")
        while not self.bot.is_closed():
            try:
                now = datetime.now()

                # 1. Handle per-minute character schedules
                for persona in self.bot.persona_manager.personas.values():
                    await self.handle_scheduled_event(persona, now.time())

                # 2. Handle periodic loan default checks (every 10 minutes)
                current_minute = now.minute
                if current_minute % 10 == 0 and current_minute != self.last_default_check_minute:
                    self.last_default_check_minute = current_minute
                    await self.check_loan_defaults()

                # 3. Handle daily journal posting (e.g., at 23:55)
                if now.hour == 23 and now.minute == 55:
                    if self.last_journal_post_day != now.day:
                        self.last_journal_post_day = now.day
                        await self.bot.narrative_manager.generate_and_post_journal()

                # 4. Handle proactive DM checks (e.g., every 5 minutes)
                if current_minute % 5 == 0 and current_minute != self.last_neediness_check_minute:
                    self.last_neediness_check_minute = current_minute
                    await self.check_bot_needs()

            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}", exc_info=True)

            await asyncio.sleep(60) # Check again in one minute

    async def check_bot_needs(self):
        """Checks if a bot's neediness is high enough to DM the Master."""
        self.logger.info("Scheduler: Checking for bot neediness...")
        try:
            master_user = await self.bot.fetch_user(self.bot.config.user_id)
        except discord.NotFound:
            self.logger.error("Could not find Master user to send proactive DMs.")
            return

        thresholds = {
            "Maya": 30, "Eka": 50, "Dvi": 70, "Tri": 40, "Chatur": 80,
            "Panch": 60, "Shash": 65, "Sapt": 55, "Asht": 50, "Nav": 45, "Dash": 60
        }

        for name, persona in self.bot.persona_manager.personas.items():
            neediness = persona.emotions.get("neediness", 0)
            threshold = thresholds.get(name, 70)

            if neediness > threshold:
                self.logger.info(f"{name}'s neediness ({neediness}) is above threshold ({threshold}). Triggering proactive DM.")

                # For now, we'll just implement the text-based seduction.
                # Art/Voice can be added as an enhancement later.
                prompt = (
                    f"{persona.get_full_prompt()}\n\n"
                    "You are feeling incredibly needy and lonely for your Master. "
                    "Write a short, direct, and seductive message to him in a DM, expressing how much you miss him and want his attention. "
                    "You must adhere to the *action* text *action* format."
                )

                dm_text = await self.bot.ollama_client.generate_text(prompt, self.bot.config.llm_model)

                if "Error:" not in dm_text and dm_text:
                    try:
                        await master_user.send(f"__**A message from {name}:**__\n{dm_text}")
                        # Reset neediness to prevent spamming
                        persona.emotions['neediness'] = 20
                        self.bot.narrative_manager.log_event(f"{name} felt needy and sent a private message to the Master.", level="normal")
                    except Exception as e:
                        self.logger.error(f"Failed to send proactive DM from {name}: {e}")
                else:
                    self.logger.error(f"Failed to generate proactive DM text for {name}: {dm_text}")


    async def check_loan_defaults(self):
        """Checks for and announces loan defaults."""
        self.logger.info("Scheduler: Checking for loan defaults...")
        defaulted_loans = self.bot.loan_manager.check_for_defaults()
        if not defaulted_loans:
            return

        bank_channel = discord.utils.get(self.bot.get_all_channels(), name="bank-of-vardhan")
        if not bank_channel:
            self.logger.warning("Could not find #bank-of-vardhan channel to announce loan defaults.")
            return

        for loan in defaulted_loans:
            embed = discord.Embed(
                title="‼️ LOAN DEFAULT AND ENSLAVEMENT NOTICE ‼️",
                description=(
                    f"The debt for loan `{loan['loan_id']}` has not been settled by the due date.\n"
                    f"As per the laws of this world, the borrower is now the property of the lender."
                ),
                color=discord.Color.red()
            )
            embed.add_field(name="New Master", value=loan['lender_name'], inline=True)
            embed.add_field(name="New Servant", value=loan['borrower_name'], inline=True)
            embed.set_footer(text="A debt unpaid is a soul for sale.")
            await bank_channel.send(embed=embed)

    async def handle_scheduled_event(self, persona, current_time):
        """
        Checks a persona's schedule and triggers actions. Usable by both live scheduler and offline simulation.
        """
        if not persona.schedule:
            return

        announcements = set()
        for event, event_time_str in persona.schedule.items():
            try:
                event_time = datetime.strptime(event_time_str, '%H:%M').time()
                if event_time.hour == current_time.hour and event_time.minute == current_time.minute:
                    self.logger.info(f"Scheduler: Triggering '{event}' for {persona.name} at {current_time}.")

                    message = ""
                    if event == "wake_up":
                        message = f"☀️ *{persona.name} is waking up and starting their day.*"
                    elif event == "go_to_work":
                        work_result = await self.bot.job_manager.perform_work(persona)
                        message = f"💼 {work_result}"
                    elif event == "free_time":
                        message = f"☕ *{persona.name} is now enjoying some free time, free to cause chaos or relax.*"
                    elif event == "go_to_sleep":
                        message = f"🌙 *{persona.name} is heading to bed for the night.*"

                    if message:
                        announcements.add(message)
            except ValueError:
                self.logger.error(f"Invalid time format for event '{event}' in {persona.name}'s schedule: {event_time_str}")

        if announcements:
            channel = discord.utils.get(self.bot.get_all_channels(), name='general-chat')
            if not channel:
                self.logger.warning("Could not find 'general-chat' to announce schedule event.")
                return

            for announcement in announcements:
                try:
                    await channel.send(announcement)
                except Exception as e:
                    self.logger.error(f"Failed to send schedule message for {persona.name}: {e}")