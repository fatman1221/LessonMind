# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, Class, ClassStudent
from api.auth import get_current_user, require_admin

router = APIRouter()


class ClassCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None


class ClassResponse(BaseModel):
    id: int
    teacher_id: int
    name: str
    description: Optional[str]
    subject: Optional[str]
    grade: Optional[str]
    created_at: datetime
    student_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class StudentAddRequest(BaseModel):
    student_ids: List[int]


@router.post("/classes", response_model=ClassResponse)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建班级（仅教师）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以创建班级")
    
    new_class = Class(
        teacher_id=current_user.id,
        name=class_data.name,
        description=class_data.description,
        subject=class_data.subject,
        grade=class_data.grade
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    
    return ClassResponse(
        id=new_class.id,
        teacher_id=new_class.teacher_id,
        name=new_class.name,
        description=new_class.description,
        subject=new_class.subject,
        grade=new_class.grade,
        created_at=new_class.created_at,
        student_count=0
    )


@router.get("/classes", response_model=List[ClassResponse])
async def get_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取班级列表"""
    if current_user.role == "teacher":
        # 教师查看自己创建的班级
        classes = db.query(Class).filter(
            Class.teacher_id == current_user.id
        ).order_by(desc(Class.created_at)).all()
    elif current_user.role == "student":
        # 学生查看自己加入的班级
        class_ids = db.query(ClassStudent.class_id).filter(
            ClassStudent.student_id == current_user.id
        ).all()
        class_ids = [c[0] for c in class_ids]
        if class_ids:
            classes = db.query(Class).filter(Class.id.in_(class_ids)).all()
        else:
            classes = []
    else:
        # 管理员查看所有班级
        classes = db.query(Class).order_by(desc(Class.created_at)).all()
    
    result = []
    for cls in classes:
        student_count = db.query(ClassStudent).filter(
            ClassStudent.class_id == cls.id
        ).count()
        result.append(ClassResponse(
            id=cls.id,
            teacher_id=cls.teacher_id,
            name=cls.name,
            description=cls.description,
            subject=cls.subject,
            grade=cls.grade,
            created_at=cls.created_at,
            student_count=student_count
        ))
    
    return result


@router.get("/classes/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取班级详情"""
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 权限检查
    if current_user.role == "teacher" and cls.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此班级")
    elif current_user.role == "student":
        membership = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == current_user.id
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="您不是此班级的成员")
    
    student_count = db.query(ClassStudent).filter(
        ClassStudent.class_id == cls.id
    ).count()
    
    return ClassResponse(
        id=cls.id,
        teacher_id=cls.teacher_id,
        name=cls.name,
        description=cls.description,
        subject=cls.subject,
        grade=cls.grade,
        created_at=cls.created_at,
        student_count=student_count
    )


@router.put("/classes/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新班级信息（仅教师）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以修改班级")
    
    cls = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user.id
    ).first()
    
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    if class_data.name is not None:
        cls.name = class_data.name
    if class_data.description is not None:
        cls.description = class_data.description
    if class_data.subject is not None:
        cls.subject = class_data.subject
    if class_data.grade is not None:
        cls.grade = class_data.grade
    
    cls.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(cls)
    
    student_count = db.query(ClassStudent).filter(
        ClassStudent.class_id == cls.id
    ).count()
    
    return ClassResponse(
        id=cls.id,
        teacher_id=cls.teacher_id,
        name=cls.name,
        description=cls.description,
        subject=cls.subject,
        grade=cls.grade,
        created_at=cls.created_at,
        student_count=student_count
    )


@router.delete("/classes/{class_id}")
async def delete_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除班级（仅教师）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以删除班级")
    
    cls = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user.id
    ).first()
    
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    db.delete(cls)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/classes/{class_id}/students", response_model=dict)
async def add_students(
    class_id: int,
    request: StudentAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加学生到班级（仅教师）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以添加学生")
    
    cls = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user.id
    ).first()
    
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    added_count = 0
    for student_id in request.student_ids:
        # 检查学生是否存在且是学生角色
        student = db.query(User).filter(
            User.id == student_id,
            User.role == "student"
        ).first()
        
        if not student:
            continue
        
        # 检查是否已经在班级中
        existing = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == student_id
        ).first()
        
        if not existing:
            membership = ClassStudent(
                class_id=class_id,
                student_id=student_id
            )
            db.add(membership)
            added_count += 1
    
    db.commit()
    
    return {"message": f"成功添加 {added_count} 名学生"}


@router.delete("/classes/{class_id}/students/{student_id}")
async def remove_student(
    class_id: int,
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从班级移除学生（仅教师）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以移除学生")
    
    cls = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user.id
    ).first()
    
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    membership = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == student_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="学生不在该班级中")
    
    db.delete(membership)
    db.commit()
    
    return {"message": "移除成功"}


@router.get("/classes/{class_id}/students", response_model=List[dict])
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取班级学生列表"""
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 权限检查
    if current_user.role == "teacher" and cls.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此班级")
    elif current_user.role == "student":
        membership = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == current_user.id
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="您不是此班级的成员")
    
    memberships = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id
    ).all()
    
    students = []
    for membership in memberships:
        student = db.query(User).filter(User.id == membership.student_id).first()
        if student:
            students.append({
                "id": student.id,
                "username": student.username,
                "email": student.email,
                "joined_at": membership.joined_at
            })
    
    return students


@router.get("/students/available", response_model=List[dict])
async def get_available_students(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取可用的学生列表（教师和管理员）"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="只有教师和管理员可以查看学生列表")
    
    # 获取所有学生用户
    students = db.query(User).filter(User.role == "student").order_by(User.username).all()
    
    result = []
    for student in students:
        result.append({
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "is_active": student.is_active,
            "created_at": student.created_at
        })
    
    return result

