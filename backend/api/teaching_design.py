from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import os

from database import get_db
from models import User, TeachingDesign
from services.ai_service import ai_service
from services.multimedia_service import multimedia_service
from api.auth import get_current_user
from config import settings

router = APIRouter()


class TeachingDesignCreate(BaseModel):
    subject: str
    grade: str
    topic: str
    teaching_objectives: str


class TeachingDesignResponse(BaseModel):
    id: int
    subject: str
    grade: str
    topic: str
    teaching_objectives: str
    content: Dict[str, Any]
    word_file_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/generate", response_model=TeachingDesignResponse)
async def generate_teaching_design(
    design_data: TeachingDesignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成教学设计"""
    try:
        # 调用AI服务生成教学设计
        content = ai_service.generate_teaching_design(
            subject=design_data.subject,
            grade=design_data.grade,
            topic=design_data.topic,
            objectives=design_data.teaching_objectives
        )
        
        # 保存到数据库
        teaching_design = TeachingDesign(
            user_id=current_user.id,
            subject=design_data.subject,
            grade=design_data.grade,
            topic=design_data.topic,
            teaching_objectives=design_data.teaching_objectives,
            content=content
        )
        db.add(teaching_design)
        db.commit()
        db.refresh(teaching_design)
        
        return teaching_design
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成教学设计失败: {str(e)}")


@router.get("/", response_model=list[TeachingDesignResponse])
async def get_teaching_designs(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教学设计列表"""
    designs = db.query(TeachingDesign)\
        .filter(TeachingDesign.user_id == current_user.id)\
        .order_by(TeachingDesign.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return designs


@router.get("/{design_id}", response_model=TeachingDesignResponse)
async def get_teaching_design(
    design_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个教学设计"""
    design = db.query(TeachingDesign)\
        .filter(
            TeachingDesign.id == design_id,
            TeachingDesign.user_id == current_user.id
        )\
        .first()
    
    if not design:
        raise HTTPException(status_code=404, detail="教学设计不存在")
    
    return design


@router.put("/{design_id}", response_model=TeachingDesignResponse)
async def update_teaching_design(
    design_id: int,
    content: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新教学设计"""
    design = db.query(TeachingDesign)\
        .filter(
            TeachingDesign.id == design_id,
            TeachingDesign.user_id == current_user.id
        )\
        .first()
    
    if not design:
        raise HTTPException(status_code=404, detail="教学设计不存在")
    
    design.content = content
    design.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(design)
    
    return design


@router.post("/{design_id}/export-word")
async def export_to_word(
    design_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出为Word文档"""
    from fastapi.responses import FileResponse
    
    design = db.query(TeachingDesign)\
        .filter(
            TeachingDesign.id == design_id,
            TeachingDesign.user_id == current_user.id
        )\
        .first()
    
    if not design:
        raise HTTPException(status_code=404, detail="教学设计不存在")
    
    # 生成Word文档
    word_dir = os.path.join(settings.UPLOAD_DIR, "word")
    os.makedirs(word_dir, exist_ok=True)
    
    filename = f"teaching_design_{design_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
    file_path = os.path.join(word_dir, filename)
    
    teaching_design_data = {
        "subject": design.subject,
        "grade": design.grade,
        "topic": design.topic,
        "teaching_objectives": design.teaching_objectives,
        "content": design.content
    }
    
    multimedia_service.generate_word_document(teaching_design_data, file_path)
    
    # 更新数据库
    design.word_file_path = f"/uploads/word/{filename}"
    db.commit()
    
    return FileResponse(
        file_path,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=filename
    )

