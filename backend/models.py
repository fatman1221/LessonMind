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
    role = Column(String(20), default="teacher")  # teacher, admin, student
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # 关系
    teaching_designs = relationship("TeachingDesign", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")
    favorites = relationship("UserFavorite", back_populates="user")
    created_classes = relationship("Class", back_populates="teacher", foreign_keys="Class.teacher_id")
    class_memberships = relationship("ClassStudent", back_populates="student")
    assignments = relationship("Assignment", back_populates="teacher")
    submissions = relationship("AssignmentSubmission", back_populates="student")


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


class UserFavorite(Base):
    """用户收藏表"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)  # 收藏标题
    content_type = Column(String(50), nullable=False)  # 内容类型：teaching_design, chat, question, custom
    content = Column(Text, nullable=False)  # 收藏内容（支持富文本）
    tags = Column(String(500))  # 标签，逗号分隔
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="favorites")


class Class(Base):
    """班级表"""
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)  # 班级名称
    description = Column(Text)  # 班级描述
    subject = Column(String(50))  # 学科
    grade = Column(String(20))  # 学段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    teacher = relationship("User", back_populates="created_classes", foreign_keys=[teacher_id])
    students = relationship("ClassStudent", back_populates="class_obj", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="class_obj", cascade="all, delete-orphan")


class ClassStudent(Base):
    """班级学生关系表"""
    __tablename__ = "class_students"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    class_obj = relationship("Class", back_populates="students")
    student = relationship("User", back_populates="class_memberships")


class Assignment(Base):
    """作业表"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    title = Column(String(200), nullable=False)  # 作业标题
    description = Column(Text)  # 作业描述
    questions = Column(JSON, nullable=False)  # 题目列表（从题库选择或自定义）
    deadline = Column(DateTime)  # 截止时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = Column(Boolean, default=False)  # 是否已发布
    
    # 关系
    teacher = relationship("User", back_populates="assignments")
    class_obj = relationship("Class", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentSubmission(Base):
    """作业提交表"""
    __tablename__ = "assignment_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answers = Column(JSON, nullable=False)  # 学生答案 {question_id: answer}
    score = Column(Float)  # 得分
    total_score = Column(Float)  # 总分
    is_graded = Column(Boolean, default=False)  # 是否已批改
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime)  # 批改时间
    
    # 关系
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")

