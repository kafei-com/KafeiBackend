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
        No architecture assumptions.
        """
        messages = [
            SystemMessage(
                content=(
                    "You are a helpful, friendly AI assistant. "
                    "Respond naturally and concisely like a normal chatbot."
                )
            ),
            HumanMessage(content=message),
        ]

        response = await self.model.ainvoke(messages)
        return response.content.strip()