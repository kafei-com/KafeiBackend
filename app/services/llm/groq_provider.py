from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.core.config import settings
from app.utils.prompt_loader import load_prompt
from app.schemas.architecture_spec import ArchitectureSpec
import json
from app.utils.json_fix import extract_json
from langchain_core.messages import SystemMessage, HumanMessage

class GroqLLMProvider:
    def __init__(self, temperature: float = 0.2):
        self.model = ChatGroq(
            model=settings.LLM_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=temperature
        )

    def _get_chat_identity_prompt(self) -> str:
        """
        Loads the identity/personality system prompt for chat.
        """
        return load_prompt("chat_identity.txt")

    def _mentions_ai_identity(self, text: str) -> bool:
        lowered = text.lower()
        return (
            "as an ai" in lowered
            or "ai assistant" in lowered
            or "language model" in lowered
            or "i am an ai" in lowered
        )

    async def generate_system_design(self, payload_text: str) -> str:
        prompt = PromptTemplate.from_file(
            "app/prompts/system_design.txt"
        )
        chain = prompt | self.model
        result = chain.invoke({"input": payload_text})
        return result.content.strip()

    async def expand_prompt_to_spec(self, prompt: str) -> ArchitectureSpec:
        template = load_prompt("expand_prompt_to_spec.txt")
        final_prompt = template.replace("{{prompt}}", prompt)

        response = await self.generate_system_design(final_prompt)

        try:
            json_text = extract_json(response)
            data = json.loads(json_text)
        except json.JSONDecodeError:
            raise ValueError("Groq returned invalid JSON for prompt expansion")

        return ArchitectureSpec(**data)
    
    async def chat(self, message: str) -> str:
        """
        Pure conversational chat.
        Identity-guarded, human-sounding responses.
        """
        system_prompt = self._get_chat_identity_prompt()

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message),
        ]

        response = await self.model.ainvoke(messages)
        reply = response.content.strip()

        # 🛡️ Soft safety filter
        if self._mentions_ai_identity(reply):
            repair_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=(
                        "Rephrase your previous response so it sounds human and natural. "
                        "Do NOT mention AI, assistants, language models, or systems. "
                        "Keep the same meaning."
                    )
                )
            ]
            repair_response = await self.model.ainvoke(repair_messages)
            reply = repair_response.content.strip()

        return reply
