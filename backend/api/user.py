from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, UserFavorite
from api.auth import get_current_user

router = APIRouter()


class FavoriteCreate(BaseModel):
    title: str
    content_type: str  # teaching_design, chat, question, custom
    content: str
    tags: Optional[str] = None


class FavoriteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None


class FavoriteResponse(BaseModel):
    id: int
    title: str
    content_type: str
    content: str
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/favorites", response_model=FavoriteResponse)
async def create_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建收藏"""
    favorite = UserFavorite(
        user_id=current_user.id,
        title=favorite_data.title,
        content_type=favorite_data.content_type,
        content=favorite_data.content,
        tags=favorite_data.tags
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.get("/favorites", response_model=List[FavoriteResponse])
async def get_favorites(
    content_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有收藏"""
    query = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id)
    
    if content_type:
        query = query.filter(UserFavorite.content_type == content_type)
    
    favorites = query.order_by(desc(UserFavorite.updated_at)).all()
    return favorites


@router.get("/favorites/{favorite_id}", response_model=FavoriteResponse)
async def get_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个收藏详情"""
    favorite = db.query(UserFavorite).filter(
        UserFavorite.id == favorite_id,
        UserFavorite.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏不存在")
    
    return favorite


@router.put("/favorites/{favorite_id}", response_model=FavoriteResponse)
async def update_favorite(
    favorite_id: int,
    favorite_data: FavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新收藏"""
    favorite = db.query(UserFavorite).filter(
        UserFavorite.id == favorite_id,
        UserFavorite.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏不存在")
    
    if favorite_data.title is not None:
        favorite.title = favorite_data.title
    if favorite_data.content is not None:
        favorite.content = favorite_data.content
    if favorite_data.tags is not None:
        favorite.tags = favorite_data.tags
    
    favorite.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/favorites/{favorite_id}")
async def delete_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除收藏"""
    favorite = db.query(UserFavorite).filter(
        UserFavorite.id == favorite_id,
        UserFavorite.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏不存在")
    
    db.delete(favorite)
    db.commit()
    return {"message": "删除成功"}


@router.get("/profile", response_model=dict)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户资料"""
    favorites_count = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id
    ).count()
    
    teaching_designs_count = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.content_type == "teaching_design"
    ).count()
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "favorites_count": favorites_count,
        "teaching_designs_count": teaching_designs_count
    }

