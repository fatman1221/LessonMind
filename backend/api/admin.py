from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User
from api.auth import get_current_user, require_admin, get_password_hash
from api.auth import UserResponse

router = APIRouter()


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserCreateByAdmin(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "teacher"
    is_active: bool = True


class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    teacher_count: int
    student_count: int
    admin_count: int


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取所有用户列表（仅管理员）"""
    users = db.query(User).order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取单个用户信息（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreateByAdmin,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """创建新用户（仅管理员）"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 验证角色
    if user_data.role not in ["teacher", "admin", "student"]:
        raise HTTPException(status_code=400, detail="无效的角色，支持的角色：teacher, student, admin")
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新用户信息（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能修改自己的角色（防止误操作）
    if user_id == current_user.id and user_data.role and user_data.role != user.role:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")
    
    # 更新字段
    if user_data.username is not None:
        # 检查用户名是否已被其他用户使用
        existing = db.query(User).filter(
            User.username == user_data.username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已被使用")
        user.username = user_data.username
    
    if user_data.email is not None:
        # 检查邮箱是否已被其他用户使用
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
        user.email = user_data.email
    
    if user_data.role is not None:
        if user_data.role not in ["teacher", "admin", "student"]:
            raise HTTPException(status_code=400, detail="无效的角色，支持的角色：teacher, student, admin")
        user.role = user_data.role
    
    if user_data.is_active is not None:
        # 不能禁用自己的账户
        if user_id == current_user.id and not user_data.is_active:
            raise HTTPException(status_code=400, detail="不能禁用自己的账户")
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账户")
    
    db.delete(user)
    db.commit()
    return {"message": "用户删除成功"}


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户统计信息（仅管理员）"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    teacher_count = db.query(User).filter(User.role == "teacher").count()
    student_count = db.query(User).filter(User.role == "student").count()
    admin_count = db.query(User).filter(User.role == "admin").count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "teacher_count": teacher_count,
        "student_count": student_count,
        "admin_count": admin_count
    }
