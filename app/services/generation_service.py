import uuid
from app.services.llm_provider import LLMProvider
from app.services.zip_builder import build_zip
from app.embedding.embedding_service import store_generation_embedding
from app.utils.validator import validate_scaffold

class GenerationService:
    def __init__(self):
        self.llm = LLMProvider()

    async def generate_architecture(self, payload):
        response = await self.llm.generate_architecture(payload)
        validate_scaffold(response)
        zip_path = build_zip(response)
        await store_generation_embedding(response)
        return {"id": str(uuid.uuid4()), "result": response, "zip_url": f"/artifacts/download/{zip_path}"}
        # return {"id": str(uuid.uuid4()), "result": response, "zip_url": f"will be available in future updates"}
