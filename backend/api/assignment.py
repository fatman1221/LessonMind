# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re

from database import get_db
from models import User, Class, ClassStudent, Assignment, AssignmentSubmission, QuestionBank
from api.auth import get_current_user

router = APIRouter()


class AssignmentCreate(BaseModel):
    class_id: int
    title: str
    description: Optional[str] = None
    question_ids: List[int]  # 从题库选择的题目ID
    deadline: Optional[datetime] = None


class AssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    class_id: int
    title: str
    description: Optional[str]
    questions: Dict[str, Any]
    deadline: Optional[datetime]
    created_at: datetime
    is_published: bool
    submission_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class SubmissionRequest(BaseModel):
    answers: Dict[str, str]  # {question_id: answer}


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    student_username: Optional[str] = None
    answers: Dict[str, str]
    score: Optional[float]
    total_score: Optional[float]
    is_graded: bool
    is_late: Optional[bool] = False
    submitted_at: datetime
    results: Optional[Dict[str, Any]] = None  # 每道题的判题结果
    
    class Config:
        from_attributes = True


def _normalize_assignment_questions(raw: Any) -> List[Dict]:
    """从作业记录中解析题目列表，兼容 JSON 字符串或异常数据。"""
    if raw is None:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return []
    if not isinstance(raw, dict):
        return []
    qs = raw.get("questions", [])
    return qs if isinstance(qs, list) else []


def _normalize_answer_keys(answers: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """将提交的答案 key 统一为字符串，兼容数据库反序列化后的整型 key。"""
    if not answers:
        return {}
    out: Dict[str, str] = {}
    for k, v in answers.items():
        s = v if isinstance(v, str) else str(v if v is not None else "")
        out[str(k)] = s.strip()
    return out


def grade_answers(questions: List[Dict], answers: Dict[str, str]) -> Dict[str, Any]:
    """自动判题"""
    answers = _normalize_answer_keys(answers)
    results = {}
    total_score = 0
    correct_count = 0
    
    for question in questions:
        q_id = str(question.get("id", ""))
        student_answer = answers.get(q_id, "").strip()
        correct_answer = question.get("answer", "").strip()
        question_type = question.get("type", "")
        
        is_correct = False
        score = 0
        
        if question_type == "choice":
            # 选择题：答案通常是A、B、C、D
            if student_answer.upper() == correct_answer.upper():
                is_correct = True
                score = 1
        elif question_type == "fill":
            # 填空题：去除空格后比较
            if student_answer.replace(" ", "") == correct_answer.replace(" ", ""):
                is_correct = True
                score = 1
        elif question_type == "short_answer":
            # 简答题：简单关键词匹配（可以后续改进为AI判题）
            student_lower = student_answer.lower()
            correct_lower = correct_answer.lower()
            # 如果学生答案包含正确答案的关键词，认为正确
            if correct_lower in student_lower or student_lower in correct_lower:
                is_correct = True
                score = 1
        
        if is_correct:
            correct_count += 1
            total_score += score
        
        results[q_id] = {
            "is_correct": is_correct,
            "score": score,
            "student_answer": student_answer,
            "correct_answer": correct_answer
        }
    
    return {
        "results": results,
        "total_score": total_score,
        "correct_count": correct_count,
        "total_questions": len(questions)
    }


@router.post("/assignments", response_model=AssignmentResponse)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建作业（仅教师）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以创建作业")
    
    # 验证班级
    cls = db.query(Class).filter(
        Class.id == assignment_data.class_id,
        Class.teacher_id == current_user.id
    ).first()
    
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")

    if assignment_data.deadline:
        # 截止时间不能早于今天（允许今天和未来）
        if assignment_data.deadline.date() < datetime.now().date():
            raise HTTPException(status_code=400, detail="截止时间不能早于今天")
    
    # 获取题目详情
    questions = []
    for q_id in assignment_data.question_ids:
        question = db.query(QuestionBank).filter(QuestionBank.id == q_id).first()
        if question:
            # 解析选择题选项（如果题目内容包含选项）
            options = None
            if question.question_type == "choice":
                # 尝试从题目内容中提取选项
                content = question.question_content
                # 简单解析：查找A. B. C. D. 开头的行
                option_pattern = r'([A-D])\.\s*([^\n]+)'
                matches = re.findall(option_pattern, content)
                if matches:
                    options = [match[1].strip() for match in matches]
                else:
                    # 如果没有找到，使用默认选项
                    options = ["选项A", "选项B", "选项C", "选项D"]
            
            questions.append({
                "id": question.id,
                "type": question.question_type,
                "question": question.question_content,
                "answer": question.answer,
                "options": options
            })
    
    if not questions:
        raise HTTPException(status_code=400, detail="至少需要选择一道题目")
    
    assignment = Assignment(
        teacher_id=current_user.id,
        class_id=assignment_data.class_id,
        title=assignment_data.title,
        description=assignment_data.description,
        questions={"questions": questions},
        deadline=assignment_data.deadline,
        is_published=False
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return AssignmentResponse(
        id=assignment.id,
        teacher_id=assignment.teacher_id,
        class_id=assignment.class_id,
        title=assignment.title,
        description=assignment.description,
        questions=assignment.questions,
        deadline=assignment.deadline,
        created_at=assignment.created_at,
        is_published=assignment.is_published,
        submission_count=0
    )


@router.post("/assignments/{assignment_id}/publish")
async def publish_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布作业（仅教师）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以发布作业")
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    assignment.is_published = True
    db.commit()
    
    return {"message": "作业已发布"}


@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_assignments(
    class_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取作业列表"""
    try:
        if current_user.role == "teacher":
            # 教师查看自己创建的作业
            query = db.query(Assignment).filter(Assignment.teacher_id == current_user.id)
            if class_id:
                query = query.filter(Assignment.class_id == class_id)
            assignments = query.order_by(desc(Assignment.created_at)).all()
        elif current_user.role == "student":
            # 学生查看自己班级的已发布作业
            # 获取学生所在的班级ID
            class_ids = db.query(ClassStudent.class_id).filter(
                ClassStudent.student_id == current_user.id
            ).all()
            class_ids = [c[0] for c in class_ids]
            
            if not class_ids:
                return []
            
            query = db.query(Assignment).filter(
                Assignment.class_id.in_(class_ids),
                Assignment.is_published == True
            )
            if class_id:
                query = query.filter(Assignment.class_id == class_id)
            assignments = query.order_by(desc(Assignment.created_at)).all()
        else:
            # 管理员查看所有作业
            query = db.query(Assignment)
            if class_id:
                query = query.filter(Assignment.class_id == class_id)
            assignments = query.order_by(desc(Assignment.created_at)).all()
        
        result = []
        for assignment in assignments:
            try:
                submission_count = db.query(AssignmentSubmission).filter(
                    AssignmentSubmission.assignment_id == assignment.id
                ).count()
                
                # 确保questions字段是字典类型
                questions_data = assignment.questions
                if isinstance(questions_data, str):
                    import json
                    questions_data = json.loads(questions_data)
                elif questions_data is None:
                    questions_data = {"questions": []}
                
                result.append(AssignmentResponse(
                    id=assignment.id,
                    teacher_id=assignment.teacher_id,
                    class_id=assignment.class_id,
                    title=assignment.title,
                    description=assignment.description,
                    questions=questions_data,
                    deadline=assignment.deadline,
                    created_at=assignment.created_at,
                    is_published=assignment.is_published,
                    submission_count=submission_count
                ))
            except Exception as e:
                # 如果单个作业处理失败，记录错误但继续处理其他作业
                print(f"处理作业 {assignment.id} 时出错: {str(e)}")
                continue
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取作业列表失败: {str(e)}")


@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取作业详情"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 权限检查
    if current_user.role == "teacher" and assignment.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此作业")
    elif current_user.role == "student":
        # 检查学生是否在作业的班级中
        membership = db.query(ClassStudent).filter(
            ClassStudent.class_id == assignment.class_id,
            ClassStudent.student_id == current_user.id
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="您无权访问此作业")
        if not assignment.is_published:
            raise HTTPException(status_code=403, detail="作业尚未发布")
    
    submission_count = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment.id
    ).count()
    
    return AssignmentResponse(
        id=assignment.id,
        teacher_id=assignment.teacher_id,
        class_id=assignment.class_id,
        title=assignment.title,
        description=assignment.description,
        questions=assignment.questions,
        deadline=assignment.deadline,
        created_at=assignment.created_at,
        is_published=assignment.is_published,
        submission_count=submission_count
    )


@router.post("/assignments/{assignment_id}/submit", response_model=SubmissionResponse)
async def submit_assignment(
    assignment_id: int,
    submission_data: SubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交作业（仅学生）"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="只有学生可以提交作业")
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 检查学生是否在班级中
    membership = db.query(ClassStudent).filter(
        ClassStudent.class_id == assignment.class_id,
        ClassStudent.student_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="您无权提交此作业")
    
    if not assignment.is_published:
        raise HTTPException(status_code=400, detail="作业尚未发布")
    
    # 检查是否已提交
    existing = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="您已经提交过此作业")
    
    questions = _normalize_assignment_questions(assignment.questions)
    
    # 自动判题
    grading_result = grade_answers(questions, submission_data.answers)
    
    # 创建提交记录
    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        answers=submission_data.answers,
        score=grading_result["total_score"],
        total_score=len(questions),
        is_graded=True,
        graded_at=datetime.utcnow()
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    is_late = bool(assignment.deadline and submission.submitted_at and submission.submitted_at > assignment.deadline)
    
    return SubmissionResponse(
        id=submission.id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        student_username=None,
        answers=submission.answers,
        score=submission.score,
        total_score=submission.total_score,
        is_graded=submission.is_graded,
        is_late=is_late,
        submitted_at=submission.submitted_at,
        results=grading_result
    )


@router.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionResponse])
async def get_submissions(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取作业提交列表（教师或管理员）"""
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="只有教师或管理员可以查看提交情况")
    
    q = db.query(Assignment).filter(Assignment.id == assignment_id)
    if current_user.role == "teacher":
        q = q.filter(Assignment.teacher_id == current_user.id)
    assignment = q.first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).order_by(desc(AssignmentSubmission.submitted_at)).all()
    
    questions = _normalize_assignment_questions(assignment.questions)
    
    result = []
    for submission in submissions:
        grading_result = grade_answers(questions, submission.answers or {})
        student = db.query(User).filter(User.id == submission.student_id).first()
        is_late = bool(assignment.deadline and submission.submitted_at and submission.submitted_at > assignment.deadline)
        result.append(SubmissionResponse(
            id=submission.id,
            assignment_id=submission.assignment_id,
            student_id=submission.student_id,
            student_username=student.username if student else None,
            answers=submission.answers or {},
            score=submission.score,
            total_score=submission.total_score,
            is_graded=submission.is_graded,
            is_late=is_late,
            submitted_at=submission.submitted_at,
            results=grading_result
        ))
    
    return result


@router.get("/assignments/{assignment_id}/my-submission", response_model=Optional[SubmissionResponse])
async def get_my_submission(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的提交（学生）"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="只有学生可以查看自己的提交")
    
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()
    
    if not submission:
        return None
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    questions = _normalize_assignment_questions(assignment.questions) if assignment else []
    grading_result = grade_answers(questions, submission.answers or {})
    is_late = bool(
        assignment and assignment.deadline and submission.submitted_at and submission.submitted_at > assignment.deadline
    )
    
    return SubmissionResponse(
        id=submission.id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        student_username=None,
        answers=submission.answers,
        score=submission.score,
        total_score=submission.total_score,
        is_graded=submission.is_graded,
        is_late=is_late,
        submitted_at=submission.submitted_at,
        results=grading_result
    )

