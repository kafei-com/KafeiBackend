# app/services/chat_service.py

from app.services.llm.orchestrator import LLMOrchestrator

class ChatService:
    def __init__(self):
        self.llm = LLMOrchestrator()

    async def chat(self, message: str) -> str:
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        return await self.llm.chat(message.strip())
