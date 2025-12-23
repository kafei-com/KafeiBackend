from app.services.llm.gemini_provider import GeminiLLMProvider

class LLMOrchestrator:
    """
    Responsible for deciding WHICH LLM handles WHICH task.
    For now: only Gemini for system design.
    """

    def __init__(self):
        self.gemini = GeminiLLMProvider()

    async def generate_system_design(self, payload):
        return await self.gemini.generate_system_design(payload)

    async def generate_component_tree(self, system_design: str):
        return await self.gemini.generate_component_tree(system_design)

    async def shutdown(self):
        await self.gemini.shutdown()
