from app.services.llm.orchestrator import LLMOrchestrator
from app.services.intent_service import IntentService, Intent
from app.services.generation_service import GenerationService
from app.schemas.generate import GenerateRequest

class ChatService:
    def __init__(self):
        self.llm = LLMOrchestrator()
        self.generator = GenerationService()

    async def chat(self, message: str):
        intent = IntentService.detect(message)
        # lowered = message.lower().strip()

        # if lowered in ["who are you", "who are you?", "what is your name"]:
        #     return {
        #         "mode": "chat",
        #         "reply": "Hello! I am Tenna. I help you think through system design and "
        #         "turn rough ideas into solid architectures. How can I help you today?"
        #     }

        if intent == Intent.CHAT:
            return {
                "mode": "chat",
                "reply": await self.llm.chat(message)
            }

        # GENERATE FLOW
        analysis = await self.llm.analyze_prompt_completeness(message)

        if not analysis["is_clear"]:
            return {
                "mode": "clarify",
                "questions": analysis["questions"],
                "original_prompt": message
            }

        return {
            "mode": "generate",
            "payload": {
                "prompt": message
            }
        }
