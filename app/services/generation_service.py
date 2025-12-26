from app.services.llm.orchestrator import LLMOrchestrator

class GenerationService:
    def __init__(self):
        self.llm = LLMOrchestrator()

    async def generate_architecture(self, payload):
        payload_text = f"""
        Project Name: {payload.project_name}
        Description: {payload.description}
        Use Case: {payload.use_case}
        Requirements: {payload.requirements}
        Tech Stack: {payload.tech_stack}
        """

        system_design = await self.llm.generate_system_design(payload_text)
        component_tree = await self.llm.generate_component_tree(system_design)

        result = {
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
        payload_text = f"""
        Project Name: {payload.project_name}
        Description: {payload.description}
        Use Case: {payload.use_case}
        Requirements: {payload.requirements}
        Tech Stack: {payload.tech_stack}
        """

        async for token in self.llm.stream_system_design(payload_text):
            yield token

    async def generate_component_tree_from_design(self, system_design):
        return await self.llm.generate_component_tree(system_design)