import json
from app.core.config import settings
from app.services.llm.base import BaseLLM
from app.utils.json_fix import safe_json_loads
from app.utils.prompt_loader import load_prompt
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas.architecture_spec import ArchitectureSpec
from app.utils.json_fix import extract_json
from app.utils.spec_coercion import coerce_architecture_spec

class GeminiLLMProvider(BaseLLM):
    def __init__(self, temperature: float = 0.2):
        self.temperature = temperature
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=self.temperature,
            google_api_key=settings.GEMINI_API_KEY,
            streaming=True,
        )

    async def generate_system_design(self, payload_text: str) -> str:
        prompt = PromptTemplate.from_file(
            "app/prompts/system_design.txt"
        )

        chain = prompt | self.model
        result = await chain.invoke({"input": payload_text})

        # print("SYSTEM DESIGN OUTPUT:", result.content)
        return result.content.strip()

    async def generate_component_tree(self, system_design: str) -> dict:
        prompt = PromptTemplate.from_file(
            "app/prompts/component_tree.txt"
        )

        chain = prompt | self.model
        result = await chain.ainvoke({"input": system_design})

        # print("COMPONENT TREE RAW:", result.content)
        return safe_json_loads(result.content)

    async def shutdown(self):
        print("Gemini LLM shutdown complete.")

    async def stream_system_design(self, payload_text: str):
        prompt = PromptTemplate.from_file("app/prompts/system_design.txt")
        chain = prompt | self.model

        # 🔥 Native async token streaming
        async for chunk in chain.astream({"input": payload_text}):
            if chunk.content:
                yield chunk.content


    async def expand_prompt_to_spec(self, prompt: str) -> ArchitectureSpec:
        template = load_prompt("expand_prompt_to_spec.txt")
        final_prompt = template.replace("{{prompt}}", prompt)

        response = await self.generate_text(final_prompt)

        try:
            json_text = extract_json(response)
            data = json.loads(json_text)
            data = coerce_architecture_spec(data)
        except Exception as e:
            print("Raw response:", response)
            raise ValueError("Invalid JSON from Gemini")

        return ArchitectureSpec(**data)

    async def generate_structured_spec(self, prompt: str):
        """
        Prompt MUST instruct Gemini to return JSON only.
        """
        response = await self.generate_text(prompt)

        try:
            json_text = extract_json(response)
            return json.loads(json_text)
        except Exception:
            print("RAW STRUCTURED RESPONSE:\n", response)
            raise ValueError("Invalid JSON from Gemini")

    async def generate_text(self, prompt: str) -> str:
        """
        Raw text generation.
        NO formatting assumptions.
        """
        response = await self.model.ainvoke(prompt)
        return response.content
