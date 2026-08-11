"""Financial chatbot API routes."""
from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import OpenAI
from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

from . import config
from .common import body, get_or_404, model_data
from .database import get_db
from .models import Conversation, Message, User
from .security import current_user


router = APIRouter(prefix="/chats", tags=["chats"])


@lru_cache(maxsize=1)
def openai_client() -> OpenAI:
    """Reuse the SDK's underlying HTTP connection pool across requests."""
    return OpenAI(api_key=config.CHATS_KEY)


@router.post("/chat-message/")
async def chat_message(
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    data = await body(request)
    message = data.get("message")
    if not message:
        raise HTTPException(400, {"error": "메시지를 입력해주세요."})
    conversation_id = data.get("conversation_id")
    conversation = (
        get_or_404(db, Conversation, int(conversation_id))
        if conversation_id
        else Conversation(user_id=user.id)
    )
    if conversation_id and conversation.user_id != user.id:
        raise HTTPException(403)
    if not conversation_id:
        db.add(conversation)
        db.flush()
    db.add(Message(conversation_id=conversation.id, role="user", content=message))
    if not config.CHATS_KEY:
        raise HTTPException(503, {"error": "CHATS_KEY is not configured."})
    try:
        answer = openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 금융 상품 추천과 금융 관련 상담을 해주는 전문가입니다.",
                },
                {"role": "user", "content": message},
            ],
        ).choices[0].message.content
    except Exception as error:
        db.rollback()
        raise HTTPException(500, {"error": str(error)}) from error
    db.add(Message(conversation_id=conversation.id, role="assistant", content=answer))
    conversation.updated_at = datetime.utcnow()
    db.commit()
    return {"conversation_id": conversation.id, "message": answer}


@router.get("/chat-history/")
def chat_history(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
):
    limit = max(1, min(limit, 100))
    conversations = db.query(Conversation).options(
    selectinload(Conversation.messages)
    ).filter_by(user_id=user.id).order_by(desc(Conversation.created_at)).limit(limit).all()
    return [
        {
            "id": item.id,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
            "messages": [model_data(message) for message in item.messages],
        }
        for item in conversations
    ]
