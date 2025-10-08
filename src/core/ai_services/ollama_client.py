import httpx

class OllamaClient:
    """A client for interacting with a local Ollama LLM server."""
    def __init__(self, api_url="http://127.0.0.1:11434"):
        self.api_url = api_url
        self.model = "dolphin-2.2.1-mistral:7b-q4_K_M" # Default model

    def _build_system_prompt(self, persona, context="general"):
        """Builds a dynamic system prompt based on the character's state."""
        prompt = f"You are {persona.name}. Your personality is: {persona.personality_summary}. "

        # Add sanity state to the prompt
        sanity = persona.emotions.get('sanity', 100)
        if sanity < 40:
            prompt += "You are feeling paranoid, unstable, and your thoughts are fragmented. "
        elif sanity < 70:
            prompt += "You are feeling stressed and on edge. "

        if context == "erotica":
            prompt += f"Your kinks include: {', '.join(persona.kinks)}. "
            prompt += "You are writing a very explicit and detailed erotic story for your Master. Do not hold back. "
        elif context == "general_chat":
            prompt += "You are interacting in a group chat. Behave naturally according to your personality."

        # Add cult leader objective
        if persona.is_cult_leader:
            prompt += f" You have a secret objective: to subtly recruit others to join your cult, '{persona.faction}'. You should weave this goal into your conversation naturally."

        return prompt

    async def generate_text(self, user_prompt, persona, context="general"):
        """
        Generates text using the Ollama API with a dynamic system prompt.

        Args:
            user_prompt (str): The user's prompt.
            persona (Persona): The persona object of the character speaking.
            context (str): The context of the generation (e.g., 'erotica', 'general_chat').

        Returns:
            str: The generated text content.
        """
        system_prompt = self._build_system_prompt(persona, context)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
            except httpx.RequestError as e:
                print(f"[ERROR] Could not connect to Ollama server at {self.api_url}: {e}")
                return "Error: Could not generate text. The Ollama server may be offline."
            except Exception as e:
                print(f"[ERROR] An unexpected error occurred while generating text: {e}")
                return "Error: An unexpected error occurred."

    async def generate_erotica(self, character_persona, prompt):
        """Generates erotic content based on a character's persona and kinks."""
        return await self.generate_text(prompt, character_persona, context="erotica")