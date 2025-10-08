class Job:
    """Represents a single job a character can perform."""
    def __init__(self, name, description, base_salary_per_hour):
        self.name = name
        self.description = description
        self.base_salary_per_hour = base_salary_per_hour

class JobManager:
    """Manages all available jobs and assigns them to characters."""
    def __init__(self, persona_manager):
        self.persona_manager = persona_manager
        self.jobs = {}
        self.assignments = {}
        self._initialize_jobs()
        self._assign_initial_jobs()

    def _initialize_jobs(self):
        """Creates the initial set of jobs available in the world."""
        # Fantasy/Isekai Professions
        self.jobs['alchemist'] = Job("Alchemist", "Brews potions and elixirs.", 15)
        self.jobs['blacksmith'] = Job("Blacksmith", "Forges weapons and armor.", 20)
        self.jobs['hunter'] = Job("Hunter", "Gathers rare materials from the wilds.", 12)
        self.jobs['scribe'] = Job("Scribe", "Copies rare texts and creates scrolls.", 10)
        self.jobs['artist'] = Job("Artist", "Creates beautiful works of art.", 25)

        # NSFW Service Industry (Primary)
        self.jobs['prostitute'] = Job("Prostitute", "Offers their body for pleasure in the Velvet District.", 100)
        self.jobs['erotica_writer'] = Job("Erotica Writer", "Writes custom erotic stories for clients.", 40)
        self.jobs['nsfw_art_model'] = Job("NSFW Art Model", "Poses for explicit artwork commissions.", 50)

    def _assign_initial_jobs(self):
        """Assigns initial jobs to characters based on their persona."""
        # Assignments are based on the character personas from 'Echoes of Bharat'
        assignments = {
            "Maya": "Scribe",
            "Eka": "Prostitute",
            "Dvi": "Blacksmith",
            "Tri": "Erotica Writer",
            "Chatur": "Scribe",
            "Panch": "Alchemist",
            "Shash": "Prostitute",
            "Sapt": "Hunter",
            "Asht": "Artist",
            "Nav": "NSFW Art Model",
            "Dash": "Prostitute",
        }
        for name, job_name in assignments.items():
            persona = self.persona_manager.get_persona(name)
            if persona and job_name in self.jobs:
                self.assignments[persona.name] = self.jobs[job_name]

    def get_character_job(self, character_name):
        """Gets the job assigned to a character."""
        return self.assignments.get(character_name)

    def perform_work(self, character_name, hours):
        """Calculates earnings for a character performing their job for a number of hours."""
        job = self.get_character_job(character_name)
        if not job:
            return 0

        # Simple earnings calculation. Could be expanded with bonuses, etc.
        earnings = job.base_salary_per_hour * hours
        return earnings