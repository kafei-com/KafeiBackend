from app.services.llm.orchestrator import LLMOrchestrator
from app.services.input_normalizer import InputNormalizer
import uuid

class GenerationService:
    def __init__(self):
        self.llm = LLMOrchestrator()
        self.normalizer = InputNormalizer(self.llm)

    async def generate_architecture(self, payload):
        spec = await self.normalizer.normalize(payload)

        payload_text = f"""
        Project Name: {spec.project_name}
        Description: {spec.description}
        Use Case: {spec.use_case}
        Requirements: {spec.requirements}
        Tech Stack: {spec.tech_stack}
        """

        system_design = await self.llm.generate_system_design(payload_text)
        component_tree = await self.llm.generate_component_tree(system_design)

        result = {
            "input_spec": spec.dict(),
            "system_design": system_design,
            "component_tree": component_tree,
        }

        # validate_scaffold(result)
        zip_path = build_zip(result)

        return {
            "id": str(uuid.uuid4()),
            "result": result,
            "zip_url": f"/artifacts/download/{zip_path}",
        }

    async def shutdown(self):
        await self.llm.shutdown()

    async def stream_system_design(self, payload):
        spec = await self.normalize_payload(payload)
        
        payload_text = f"""
        Project Name: {spec['project_name']}
        Description: {spec['description']}
        Use Case: {spec['use_case']}
        Requirements: {spec['requirements']}
        Tech Stack: {spec['tech_stack']}
        """

        async for token in self.llm.stream_system_design(payload_text):
            yield token

    async def generate_component_tree_from_design(self, system_design):
        return await self.llm.generate_component_tree(system_design)
    
    async def normalize_payload(self, payload):
        """
        Converts ANY input shape into a full ArchitectureSpec
        """
        if getattr(payload, "prompt", None):
            return await self.llm.generate_structured_spec(
                load_prompt("expand_prompt_to_spec.txt").replace(
                    "{{prompt}}", payload.prompt
                )
            )

        # already structured
        return {
            "project_name": payload.project_name,
            "description": payload.description,
            "use_case": payload.use_case,
            "requirements": payload.requirements,
            "tech_stack": payload.tech_stack,
        }
