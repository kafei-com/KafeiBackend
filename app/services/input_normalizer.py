from app.schemas.architecture_spec import ArchitectureSpec

class InputNormalizer:
    def __init__(self, llm):
        self.llm = llm

    async def normalize(self, payload) -> ArchitectureSpec:
        if payload.project_name is not None:
            if not payload.project_name.strip():
                raise ValueError("Project name cannot be empty")

            return ArchitectureSpec(
                project_name=payload.project_name.strip(),
                description=(payload.description or "").strip(),
                use_case=(payload.use_case or "").strip(),
                requirements=[r for r in (payload.requirements or []) if r.strip()],
                tech_stack=[t for t in (payload.tech_stack or []) if t.strip()],
                inferred=False
            )

        if payload.prompt is not None:
            if not payload.prompt.strip():
                raise ValueError("Prompt cannot be empty")
            
            spec = await self.llm.expand_prompt_to_spec(payload.prompt.strip())
            spec.inferred = True
            return spec

        raise ValueError("Either structured fields or prompt must be provided")
