from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os

from database import get_db
from models import User, TeachingDesign, MultimediaResource
from services.ai_service import ai_service
from services.multimedia_service import multimedia_service
from api.auth import get_current_user
from config import settings

router = APIRouter()


class GenerateImageRequest(BaseModel):
    knowledge_point: str
    subject: str
    teaching_design_id: Optional[int] = None


class GeneratePPTRequest(BaseModel):
    teaching_design_id: int
    style: str = "default"


class MultimediaResourceResponse(BaseModel):
    id: int
    teaching_design_id: Optional[int]
    resource_type: str
    file_path: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/image", response_model=MultimediaResourceResponse)
async def generate_image(
    request: GenerateImageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成教学图片"""
    try:
        # 生成图片描述（实际项目中可以调用图片生成API）
        description = ai_service.generate_image_description(
            knowledge_point=request.knowledge_point,
            subject=request.subject
        )
        
        # 这里应该调用实际的图片生成服务（如Stable Diffusion API）
        # 目前返回描述信息
        image_dir = os.path.join(settings.UPLOAD_DIR, "images")
        os.makedirs(image_dir, exist_ok=True)
        
        # 模拟图片路径（实际应该保存生成的图片）
        filename = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        file_path = f"/uploads/images/{filename}"
        
        # 保存资源记录
        resource = MultimediaResource(
            teaching_design_id=request.teaching_design_id,
            resource_type="image",
            file_path=file_path,
            description=description
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        
        return resource
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成图片失败: {str(e)}")


@router.post("/ppt", response_model=MultimediaResourceResponse)
async def generate_ppt(
    request: GeneratePPTRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成PPT课件"""
    try:
        # 获取教学设计
        design = db.query(TeachingDesign)\
            .filter(
                TeachingDesign.id == request.teaching_design_id,
                TeachingDesign.user_id == current_user.id
            )\
            .first()
        
        if not design:
            raise HTTPException(status_code=404, detail="教学设计不存在")
        
        # 生成PPT内容
        ppt_content = ai_service.generate_ppt_content(design.content)
        
        if not ppt_content:
            raise HTTPException(status_code=500, detail="PPT内容生成失败")
        
        # 生成PPT文件
        ppt_dir = os.path.join(settings.UPLOAD_DIR, "ppt")
        os.makedirs(ppt_dir, exist_ok=True)
        
        filename = f"ppt_{request.teaching_design_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pptx"
        file_path = os.path.join(ppt_dir, filename)
        
        multimedia_service.generate_ppt(ppt_content, file_path, request.style)
        
        # 保存资源记录
        resource = MultimediaResource(
            teaching_design_id=request.teaching_design_id,
            resource_type="ppt",
            file_path=f"/uploads/ppt/{filename}",
            description=f"PPT课件 - {design.topic}"
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        
        return resource
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PPT失败: {str(e)}")


@router.get("/resources/{teaching_design_id}", response_model=List[MultimediaResourceResponse])
async def get_resources(
    teaching_design_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教学设计的多媒体资源"""
    # 验证教学设计所有权
    design = db.query(TeachingDesign)\
        .filter(
            TeachingDesign.id == teaching_design_id,
            TeachingDesign.user_id == current_user.id
        )\
        .first()
    
    if not design:
        raise HTTPException(status_code=404, detail="教学设计不存在")
    
    resources = db.query(MultimediaResource)\
        .filter(MultimediaResource.teaching_design_id == teaching_design_id)\
        .order_by(MultimediaResource.created_at.desc())\
        .all()
    
    return resources


@router.get("/ppt/list", response_model=List[MultimediaResourceResponse])
async def get_all_ppts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有PPT资源"""
    # 获取当前用户的所有教学设计ID
    design_ids = db.query(TeachingDesign.id)\
        .filter(TeachingDesign.user_id == current_user.id)\
        .all()
    design_ids = [d[0] for d in design_ids]
    
    if not design_ids:
        return []
    
    # 获取这些教学设计的所有PPT资源
    resources = db.query(MultimediaResource)\
        .filter(
            MultimediaResource.teaching_design_id.in_(design_ids),
            MultimediaResource.resource_type == "ppt"
        )\
        .order_by(MultimediaResource.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return resources


@router.get("/ppt/download/{resource_id}")
async def download_ppt(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载PPT文件"""
    from fastapi.responses import FileResponse
    
    # 获取资源
    resource = db.query(MultimediaResource).filter(
        MultimediaResource.id == resource_id,
        MultimediaResource.resource_type == "ppt"
    ).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="PPT资源不存在")
    
    # 验证教学设计所有权
    if resource.teaching_design_id:
        design = db.query(TeachingDesign).filter(
            TeachingDesign.id == resource.teaching_design_id,
            TeachingDesign.user_id == current_user.id
        ).first()
        if not design:
            raise HTTPException(status_code=403, detail="无权访问此资源")
    
    # 构建文件路径
    file_path = os.path.join(settings.UPLOAD_DIR, resource.file_path.replace("/uploads/", ""))
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PPT文件不存在")
    
    # 从路径中提取文件名
    filename = os.path.basename(file_path)
    
    return FileResponse(
        file_path,
        media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        filename=filename
    )


@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除多媒体资源"""
    # 获取资源
    resource = db.query(MultimediaResource).filter(
        MultimediaResource.id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    # 验证教学设计所有权
    if resource.teaching_design_id:
        design = db.query(TeachingDesign).filter(
            TeachingDesign.id == resource.teaching_design_id,
            TeachingDesign.user_id == current_user.id
        ).first()
        if not design:
            raise HTTPException(status_code=403, detail="无权删除此资源")
    
    # 删除文件
    file_path = os.path.join(settings.UPLOAD_DIR, resource.file_path.replace("/uploads/", ""))
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            # 文件删除失败不影响数据库记录删除
            pass
    
    # 删除数据库记录
    db.delete(resource)
    db.commit()
    
    return {"message": "删除成功"}

