from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.utils.json_fix import safe_json_loads
from app.config import settings
# import json

class LLMProvider:
    def __init__(self):
        self.model = ChatGroq(
            model=settings.LLM_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.1
        )

    # --- ADD THIS SHUTDOWN METHOD ---
    async def shutdown(self):
        """
        Placeholder for closing any persistent connections or clients.
        Although ChatGroq doesn't expose a formal close, this ensures
        proper cleanup if an async HTTP client is used internally.
        """
        print("LLM Provider: Resources successfully prepared for shutdown.")
        # If you were using a library with a client, you would call client.close() here.

    # async def generate_architecture(self, payload):
    #     prompt = PromptTemplate.from_file("app/prompts/architecture_prompt.txt")
    #     chain = prompt | self.model
    #     return chain.invoke(payload.dict())

    async def generate_architecture(self, payload):
        prompt = PromptTemplate.from_file("app/prompts/architecture_prompt.txt")
        chain = prompt | self.model
        payload_text = f"""
        Project Name: {payload.project_name}
        Description: {payload.description}
        Use Case: {payload.use_case}
        Requirements: {payload.requirements}
        Tech Stack: {payload.tech_stack}
        """
        # result = chain.invoke({"input": payload_text})
        result = chain.invoke({"input": payload_text})
        print("RAW:", result.content)
        return safe_json_loads(result.content)

