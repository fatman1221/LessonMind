# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api import chat, teaching_design, multimedia, analysis, auth, user, admin, class_management, assignment
from database import engine, Base
from config import settings

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建上传目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "ppt"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "word"), exist_ok=True)

app = FastAPI(
    title="AI辅助教师备课系统",
    description="基于通义千问的教师备课辅助系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/chat", tags=["聊天对话"])
app.include_router(teaching_design.router, prefix="/api/teaching-design", tags=["教学设计"])
app.include_router(multimedia.router, prefix="/api/multimedia", tags=["多媒体资源"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["学情分析"])
app.include_router(user.router, prefix="/api/user", tags=["用户管理"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理员"])
app.include_router(class_management.router, prefix="/api", tags=["班级管理"])
app.include_router(assignment.router, prefix="/api", tags=["作业管理"])


@app.get("/")
async def root():
    return {"message": "AI辅助教师备课系统API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

