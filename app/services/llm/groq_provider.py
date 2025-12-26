from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.core.config import settings

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
