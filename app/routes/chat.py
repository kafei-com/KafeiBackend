# app/routes/chat.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])
service = ChatService()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    try:
        reply = await service.chat(payload.message)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
