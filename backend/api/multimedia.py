from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os
import html

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
    teaching_design_id: int


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


def _default_ppt_content(design: TeachingDesign) -> List[Dict]:
    content = design.content if isinstance(design.content, dict) else {}
    return [
        {
            "slide_number": 1,
            "title": f"{design.subject} - {design.topic}",
            "content": [f"学段：{design.grade}", "教学目标与课堂流程概览"],
            "notes": "封面页",
        },
        {
            "slide_number": 2,
            "title": "导入环节",
            "content": [content.get("import", {}).get("content", "结合生活场景引入本课主题")],
            "notes": "导入",
        },
        {
            "slide_number": 3,
            "title": "讲授重点",
            "content": content.get("teaching", {}).get("key_points", ["核心知识点讲解", "易错点提醒"]),
            "notes": "讲授",
        },
        {
            "slide_number": 4,
            "title": "课堂互动",
            "content": [
                a.get("content", "课堂互动")
                for a in content.get("interaction", {}).get("activities", [])
            ] or ["提问互动", "小组讨论", "课堂练习"],
            "notes": "互动",
        },
        {
            "slide_number": 5,
            "title": "课堂总结",
            "content": [content.get("summary", {}).get("content", "总结本课知识并布置课后任务")],
            "notes": "总结",
        },
    ]


@router.post("/image", response_model=MultimediaResourceResponse)
async def generate_image(
    request: GenerateImageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成教学图片"""
    try:
        design = db.query(TeachingDesign).filter(
            TeachingDesign.id == request.teaching_design_id,
            TeachingDesign.user_id == current_user.id
        ).first()
        if not design:
            raise HTTPException(status_code=404, detail="教学设计不存在")

        # 生成图片描述（实际项目中可以调用图片生成API）
        description = ai_service.generate_image_description(
            knowledge_point=request.knowledge_point,
            subject=request.subject
        )
        
        # 这里应该调用实际的图片生成服务（如Stable Diffusion API）
        # 目前返回描述信息
        image_dir = os.path.join(settings.UPLOAD_DIR, "images")
        os.makedirs(image_dir, exist_ok=True)
        
        filename = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}.svg"
        abs_file_path = os.path.join(image_dir, filename)
        # 生成可见的 SVG 占位教学图，避免透明 PNG 导致“打开看不到内容”
        subject_text = html.escape(request.subject or "学科")
        kp_text = html.escape((request.knowledge_point or "知识点").strip())
        desc_text = html.escape((description or "教学图片").strip())
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f5f7ff"/>
      <stop offset="100%" stop-color="#e6f7ff"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="720" fill="url(#bg)"/>
  <rect x="60" y="60" width="1160" height="600" rx="24" fill="#ffffff" stroke="#d9ecff" stroke-width="2"/>
  <text x="100" y="150" font-size="44" fill="#1f2d3d" font-family="Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif">AI 教学示意图</text>
  <text x="100" y="220" font-size="30" fill="#409eff" font-family="Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif">学科：{subject_text}</text>
  <text x="100" y="280" font-size="30" fill="#606266" font-family="Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif">知识点：{kp_text[:80]}</text>
  <text x="100" y="350" font-size="26" fill="#303133" font-family="Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif">说明：</text>
  <foreignObject x="100" y="370" width="1080" height="250">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font:24px 'PingFang SC','Microsoft YaHei',Arial,sans-serif;color:#606266;line-height:1.6;">
      {desc_text[:400]}
    </div>
  </foreignObject>
</svg>"""
        with open(abs_file_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        file_path = f"/uploads/images/{filename}"
        
        # 保存资源记录
        resource = MultimediaResource(
            teaching_design_id=design.id,
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
        ppt_content = ai_service.generate_ppt_content(design.content or {})
        
        if not ppt_content:
            # AI不可用时兜底，保证可生成下载
            ppt_content = _default_ppt_content(design)
        
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

