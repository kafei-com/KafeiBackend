from enum import Enum

class Intent(str, Enum):
    CHAT = "chat"
    GENERATE_ARCHITECTURE = "generate_architecture"

class IntentService:
    @staticmethod
    def detect(message: str) -> Intent:
        msg = message.lower()

        keywords = [
            "build", "generate", "design", "architecture",
            "system", "backend", "frontend", "app", "website"
        ]

        if any(k in msg for k in keywords):
            return Intent.GENERATE_ARCHITECTURE

        return Intent.CHAT
