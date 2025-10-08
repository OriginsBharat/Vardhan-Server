import asyncio
import datetime
import random

class Scheduler:
    """
    Manages the daily schedules and autonomous actions of all bots.
    """
    def __init__(self, bot):
        self.bot = bot
        self.schedules = {}
        self._load_schedules()
        self.task = None

    def _load_schedules(self):
        """
        Loads the daily schedule for each character.
        Schedules are dictionaries mapping an hour (0-23) to an activity.
        """
        for persona in self.bot.persona_manager.get_all_personas():
            # Example simple schedule: work during the day, free at night
            schedule = {
                0: "Sleeping", 1: "Sleeping", 2: "Sleeping", 3: "Sleeping", 4: "Sleeping", 5: "Sleeping", 6: "Waking up",
                7: "Breakfast", 8: "Working", 9: "Working", 10: "Working", 11: "Working",
                12: "Lunch Break", 13: "Working", 14: "Working", 15: "Working", 16: "Working",
                17: "Finishing Work", 18: "Free Time", 19: "Free Time", 20: "Free Time",
                21: "Free Time", 22: "Winding Down", 23: "Sleeping"
            }
            self.schedules[persona.name] = schedule

    async def start(self):
        """Starts the main scheduler loop."""
        print("[Scheduler] The world's clock is now ticking.")
        self.task = asyncio.create_task(self._main_loop())

    async def _main_loop(self):
        """The main loop that triggers autonomous actions based on the schedule."""
        while True:
            await self._trigger_hourly_actions()
            # Wait until the next hour, with some randomness to prevent perfect sync
            now = datetime.datetime.now()
            next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            wait_seconds = (next_hour - now).total_seconds()
            await asyncio.sleep(wait_seconds + random.randint(1, 120)) # Jitter of up to 2 mins

    async def _trigger_hourly_actions(self):
        """Triggers actions for all bots based on their current scheduled activity."""
        current_hour = datetime.datetime.now().hour
        print(f"--- Scheduler Tick: Hour {current_hour} ---")

        for persona in self.bot.persona_manager.get_all_personas():
            # Check regeneration status first
            persona.check_regeneration()

            if persona.status != "Healthy":
                print(f"[Scheduler] Skipping actions for {persona.name} (Status: {persona.status})")
                continue

            # Check for high-priority emotional states
            if persona.emotions['loneliness'] > 85:
                await self.bot.trigger_proactive_dm(persona)
                persona.emotions['loneliness'] = 20 # Reset after acting

            if persona.emotions['lust'] > 75:
                await self.bot.trigger_non_con_check(persona)

            activity = self.schedules.get(persona.name, {}).get(current_hour, "Idle")

            if activity == "Working" and persona.servitude_owner is None:
                job = self.bot.job_manager.get_character_job(persona.name)
                if job:
                    earnings = self.bot.job_manager.perform_work(persona.name, 1) # 1 hour of work
                    if earnings > 0:
                        self.bot.economy_manager.adjust_balance(persona.name, earnings, f"1 hour of work as a {job.name}")

            # Trigger a general autonomous action based on their schedule
            await self.bot.trigger_autonomous_action(persona, activity)