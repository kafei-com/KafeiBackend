from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import settings
from app.utils.json_fix import safe_json_loads
from app.services.llm.base import BaseLLM


class GeminiLLMProvider(BaseLLM):
    def __init__(self, temperature: float = 0.2):
        self.temperature = temperature
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=self.temperature,
            google_api_key=settings.GEMINI_API_KEY,
        )

    async def generate_system_design(self, payload_text: str) -> str:
        prompt = PromptTemplate.from_file(
            "app/prompts/system_design.txt"
        )

        # payload_text = f"""
        # Project Name: {payload.project_name}
        # Description: {payload.description}
        # Use Case: {payload.use_case}
        # Requirements: {payload.requirements}
        # Tech Stack: {payload.tech_stack}
        # """

        chain = prompt | self.model
        result = chain.invoke({"input": payload_text})

        # print("SYSTEM DESIGN OUTPUT:", result.content)
        return result.content.strip()

    async def generate_component_tree(self, system_design: str) -> dict:
        prompt = PromptTemplate.from_file(
            "app/prompts/component_tree.txt"
        )

        chain = prompt | self.model
        result = chain.invoke({"input": system_design})

        # print("COMPONENT TREE RAW:", result.content)
        return safe_json_loads(result.content)

    async def shutdown(self):
        print("Gemini LLM shutdown complete.")
