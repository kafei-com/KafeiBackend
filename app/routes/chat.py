from fastapi import APIRouter
from app.services.chat_service import ChatService
from app.schemas.generate import GenerateRequest
from app.services.generation_service import GenerationService
from fastapi.responses import StreamingResponse
import json

router = APIRouter(prefix="/chat", tags=["Chat"])
chat_service = ChatService()
generation_service = GenerationService()

@router.post("/")
async def chat(payload: dict):
    result = await chat_service.chat(payload["message"])

    # 🟢 Normal chat
    if result["mode"] == "chat":
        return {
            "type": "chat",
            "reply": result["reply"]
        }

    # 🟡 Clarification
    if result["mode"] == "clarify":
        return {
            "type": "clarification",
            "questions": result["questions"],
            # "original_prompt": result["original_prompt"]
        }

    # 🔵 Generate → STREAM
    async def event_generator():
        # 1️⃣ Handoff message (human)
        yield f"data: {json.dumps({
            'type': 'handoff',
            'message': result.get(
                'handoff',
                "Alright — I will put together a system design for this."
            )
        })}\n\n"

        # 2️⃣ Normalize input
        spec = await generation_service.normalizer.normalize(
            GenerateRequest(prompt=result["payload"]["prompt"])
        )

        yield f"data: {json.dumps({
            'type': 'input_spec',
            'chunk': spec.dict()
        })}\n\n"

        # 3️⃣ Stream system design
        full_design = []
        async for token in generation_service.llm.stream_system_design(
            spec.description
        ):
            full_design.append(token)
            yield f"data: {json.dumps({
                'type': 'system_design',
                'chunk': token
            })}\n\n"

        # 4️⃣ Component tree
        system_design = "".join(full_design)
        component_tree = await generation_service.generate_component_tree_from_design(system_design)

        yield f"data: {json.dumps({
            'type': 'component_tree',
            'chunk': component_tree
        })}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
