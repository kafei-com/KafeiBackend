import uuid
from app.services.llm.gemini_provider import GeminiLLMProvider
from app.services.zip_builder import build_zip
from app.embedding.embedding_service import store_generation_embedding
from app.utils.validator import validate_scaffold
from app.core.llm_retry import MAX_RETRIES, TEMPERATURE_SEQUENCE

class GenerationService:
    def __init__(self):
        self.llm = GeminiLLMProvider()

    async def generate_architecture(self, payload):
        payload_text = f"""
            Project Name: {payload.project_name}
            Description: {payload.description}
            Use Case: {payload.use_case}
            Requirements: {payload.requirements}
            Tech Stack: {payload.tech_stack}
        """

        last_error = None
        for attempt in range(MAX_RETRIES):
            temperature = TEMPERATURE_SEQUENCE[attempt]
            try:
                llm = GeminiLLMProvider(temperature=temperature)

                system_design = await llm.generate_system_design(payload_text)
                
                component_tree = await llm.generate_component_tree(system_design)
                
                result = {
                    "system_design": system_design,
                    "component_tree": component_tree
                }

                validate_scaffold(result)

                zip_path = build_zip(result)

                # await store_generation_embedding(system_design)

                return {
                    "id": str(uuid.uuid4()),
                    "result": result,
                    "zip_url": f"/artifacts/download/{zip_path}"
                }
            except Exception as e:
                last_error = e
                print(
                    f"[Retry {attempt + 1}/{MAX_RETRIES}]"
                    f"Temperature={temperature} -> {str(e)}"
                )

        # If all retries fail
        raise RuntimeError(
            f"Generation failed after {MAX_RETRIES} attempts: {last_error}"
        )
