from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="teacher")  # teacher, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # 关系
    teaching_designs = relationship("TeachingDesign", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")


class TeachingDesign(Base):
    """教学设计表"""
    __tablename__ = "teaching_designs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(50), nullable=False)  # 学科
    grade = Column(String(20), nullable=False)  # 学段
    topic = Column(String(200), nullable=False)  # 课时主题
    teaching_objectives = Column(Text)  # 教学目标
    content = Column(JSON)  # 教学设计内容（JSON格式）
    word_file_path = Column(String(500))  # Word文件路径
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="teaching_designs")
    multimedia_resources = relationship("MultimediaResource", back_populates="teaching_design")


class MultimediaResource(Base):
    """多媒体资源表"""
    __tablename__ = "multimedia_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    teaching_design_id = Column(Integer, ForeignKey("teaching_designs.id"))
    resource_type = Column(String(20), nullable=False)  # image, ppt
    file_path = Column(String(500), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    teaching_design = relationship("TeachingDesign", back_populates="multimedia_resources")


class ChatHistory(Base):
    """聊天历史表"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="chat_history")


class StudentData(Base):
    """学生数据表"""
    __tablename__ = "student_data"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True, nullable=False)
    student_name = Column(String(50))
    subject = Column(String(50))
    grade = Column(String(20))
    homework_scores = Column(JSON)  # 作业成绩
    learning_behavior = Column(JSON)  # 学习行为数据
    knowledge_mastery = Column(JSON)  # 知识点掌握情况
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QuestionBank(Base):
    """题库表"""
    __tablename__ = "question_bank"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50), nullable=False)
    knowledge_point = Column(String(200), nullable=False)
    question_type = Column(String(20), nullable=False)  # choice, fill, short_answer
    question_content = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    difficulty = Column(String(10), default="medium")  # easy, medium, hard
    created_at = Column(DateTime, default=datetime.utcnow)

