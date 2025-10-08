import time
from datetime import datetime, timedelta
import asyncio

class SimulationManager:
    """
    Manages the 'Illusion of 24/7' by simulating world events that occurred
    while the bot was offline.
    Codename: 'The Simulation'
    """
    def __init__(self, bot):
        self.bot = bot
        self.last_online_path = Path("data/last_online.txt")

    def run_offline_simulation(self):
        """Calculates offline time and simulates events for that duration."""
        last_online = self._get_last_online_timestamp()
        now = datetime.now()
        offline_duration = now - last_online

        print(f"[Simulation] Bot was offline for: {offline_duration}")

        if offline_duration > timedelta(minutes=5): # Only run for significant downtime
            print("[Simulation] Running offline simulation...")
            self._simulate_time(offline_duration)

        self._update_last_online_timestamp()

    def _get_last_online_timestamp(self):
        """Reads the last online timestamp from a file."""
        try:
            with open(self.last_online_path, 'r') as f:
                return datetime.fromisoformat(f.read().strip())
        except (FileNotFoundError, ValueError):
            # If file doesn't exist or is corrupted, assume it's the first run
            return datetime.now()

    def _update_last_online_timestamp(self):
        """Writes the current timestamp to the last online file."""
        self.last_online_path.parent.mkdir(exist_ok=True)
        with open(self.last_online_path, 'w') as f:
            f.write(datetime.now().isoformat())

    def _simulate_time(self, duration):
        """
        Simulates the passage of time for all bots, affecting their economy and emotions.
        """
        num_hours = duration.total_seconds() / 3600
        if num_hours < 1:
            return

        report_parts = [f"**Waking World Report**\n*The world has progressed by {int(num_hours)} hours while you were away...*\n"]

        for persona in self.bot.persona_manager.get_all_personas():
            # 1. Simulate Job Earnings
            job = self.bot.job_manager.get_character_job(persona.name)
            if job and persona.servitude_owner is None: # Servants don't earn for themselves
                earnings = self.bot.job_manager.perform_work(persona.name, num_hours)
                if earnings > 0:
                    self.bot.economy_manager.adjust_balance(persona.name, earnings, f"Offline work ({int(num_hours)} hours)")
                    report_parts.append(f"💼 **{persona.name}** worked as a {job.name} and earned **{earnings:.2f} Rs**.")

            # 2. Simulate Emotional State Decay/Change
            # Loneliness increases over time if alone
            persona.adjust_emotion('loneliness', int(num_hours * 2))
            # Happiness slowly decays towards 50
            if persona.emotions['happiness'] > 50:
                persona.adjust_emotion('happiness', -int(num_hours))
            elif persona.emotions['happiness'] < 50:
                 persona.adjust_emotion('happiness', int(num_hours))


        final_report = "\n".join(report_parts)

        # Schedule the report to be sent after the bot is fully ready
        async def send_report():
            await self.bot.wait_until_ready()
            announcements_channel = self.bot.get_channel_by_name("announcements")
            if announcements_channel:
                await announcements_channel.send(final_report)
            else:
                print("[Simulation] Could not find #announcements channel to send report.")

        # Use asyncio.run_coroutine_threadsafe because this function is called from a non-async context
        asyncio.run_coroutine_threadsafe(send_report(), self.bot.loop)