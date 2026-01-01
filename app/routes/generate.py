from fastapi import APIRouter, HTTPException
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.generation_service import GenerationService
from fastapi.responses import StreamingResponse
import json

router = APIRouter()
service = GenerationService()

@router.post("/", response_model=GenerateResponse)
async def generate_architecture(payload: GenerateRequest):
    try:
        result = await service.generate_architecture(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def generate_architecture_stream(payload: GenerateRequest):
    async def event_generator():
        full_system_design = []

        # 1️⃣ NORMALIZE ONCE
        spec = await service.normalizer.normalize(payload)

        # 2️⃣ SEND INPUT SPEC FIRST
        yield f"data: {json.dumps({
            'type': 'input_spec',
            'chunk': spec.dict()
        })}\n\n"

        # 3️⃣ BUILD PROMPT TEXT
        payload_text = f"""
        Project Name: {spec.project_name}
        Description: {spec.description}
        Use Case: {spec.use_case}
        Requirements: {spec.requirements}
        Tech Stack: {spec.tech_stack}
        """

        # 4️⃣ STREAM SYSTEM DESIGN
        async for token in service.llm.stream_system_design(payload_text):
            full_system_design.append(token)
            yield f"data: {json.dumps({
                'type': 'system_design',
                'chunk': token
            })}\n\n"

        # 5️⃣ COMPONENT TREE (non-streamed)
        system_design = "".join(full_system_design)
        component_tree = await service.generate_component_tree_from_design(system_design)

        yield f"data: {json.dumps({
            'type': 'component_tree',
            'chunk': component_tree
        })}\n\n"

        yield f"data: {json.dumps({
            'type': 'done'
        })}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
