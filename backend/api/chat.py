from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, ChatHistory
from services.ai_service import ai_service
from api.auth import get_current_user

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


class ChatHistoryItem(BaseModel):
    id: int
    message: str
    response: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """聊天对话接口"""
    try:
        # 构建消息历史（可以扩展为支持多轮对话）
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的AI教学助手，擅长帮助教师进行备课、解答教学问题、提供教学建议。"
            },
            {
                "role": "user",
                "content": chat_message.message
            }
        ]
        
        # 调用AI服务
        response_text = ai_service.chat(messages)
        
        # 保存聊天历史
        chat_history = ChatHistory(
            user_id=current_user.id,
            message=chat_message.message,
            response=response_text
        )
        db.add(chat_history)
        db.commit()
        
        return ChatResponse(
            response=response_text,
            conversation_id=str(chat_history.id)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天服务错误: {str(e)}")


@router.get("/history", response_model=List[ChatHistoryItem])
async def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取聊天历史"""
    history = db.query(ChatHistory)\
        .filter(ChatHistory.user_id == current_user.id)\
        .order_by(ChatHistory.created_at.desc())\
        .limit(limit)\
        .all()
    
    return history

