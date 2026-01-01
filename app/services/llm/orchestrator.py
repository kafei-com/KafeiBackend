from app.services.llm.gemini_provider import GeminiLLMProvider
from app.services.llm.groq_provider import GroqLLMProvider
from app.core.config import settings
from app.services.input_normalizer import InputNormalizer

class LLMOrchestrator:
    def __init__(self):
        self.gemini = None
        self.groq = None

    def _get_gemini(self):
        if not self.gemini:
            self.gemini = GeminiLLMProvider(temperature=0.2)
        return self.gemini

    def _get_groq(self):
        if not self.groq:
            self.groq = GroqLLMProvider(temperature=0.1)
        return self.groq

    async def generate_system_design(self, payload, prefer="gemini"):
        if prefer == "gemini" and settings.GEMINI_API_KEY:
            return await self._get_gemini().generate_system_design(payload)
        return await self._get_groq().generate_system_design(payload)

    async def generate_component_tree(self, system_design):
        if not settings.GEMINI_API_KEY:
            return None
        return await self._get_gemini().generate_component_tree(system_design)

    async def shutdown(self):
        if self.gemini:
            await self.gemini.shutdown()
        if self.groq and hasattr(self.groq, "shutdown"):
            await self.groq.shutdown()
    
    async def stream_system_design(self, payload, prefer="gemini"):
        if prefer == "gemini" and settings.GEMINI_API_KEY:
            async for token in self._get_gemini().stream_system_design(payload):
                yield token
        else:
            # Groq fallback (non-streaming → chunked)
            text = await self._get_groq().generate_system_design(payload)
            for ch in text:
                yield ch
    
    async def expand_prompt_to_spec(self, prompt: str):
        if settings.GEMINI_API_KEY:
            return await self._get_gemini().expand_prompt_to_spec(prompt)
        return await self._get_groq().expand_prompt_to_spec(prompt)
    
    async def generate_structured_spec(self, prompt):
        """
        Always returns STRICT JSON.
        Never used for streaming.
        """
        provider = self._get_gemini() if settings.GEMINI_API_KEY else self._get_groq()
        return await provider.generate_structured_spec(prompt)

    async def chat(self, message: str) -> str:
        """
        Chat always uses Groq.
        """
        return await self._get_groq().chat(message)
