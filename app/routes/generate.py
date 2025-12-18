from fastapi import APIRouter, HTTPException
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.generation_service import GenerationService

router = APIRouter()
service = GenerationService()

@router.post("/", response_model=GenerateResponse)
async def generate_architecture(payload: GenerateRequest):
    try:
        result = await service.generate_architecture(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
