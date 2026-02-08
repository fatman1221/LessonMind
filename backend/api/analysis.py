from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from database import get_db
from models import User, StudentData, QuestionBank
from services.ai_service import ai_service
from services.analysis_service import analysis_service
from api.auth import get_current_user
from config import settings

router = APIRouter()


class StudentDataCreate(BaseModel):
    student_id: str
    student_name: str
    subject: str
    grade: str
    homework_scores: Dict[str, float]
    learning_behavior: Dict[str, Any]
    knowledge_mastery: Dict[str, float]


class AnalysisResult(BaseModel):
    mastery_level: str
    mastery_score: float
    ability_score: float
    habit_score: float
    prediction_confidence: float
    recommendations: List[str]


class QuestionGenerateRequest(BaseModel):
    knowledge_point: str
    subject: str
    question_types: List[str] = ["choice", "fill", "short_answer"]
    count: int = 3


class QuestionItem(BaseModel):
    type: str
    question: str
    options: Optional[List[str]] = None
    answer: str
    explanation: str


class QuestionBankItem(BaseModel):
    id: int
    subject: str
    knowledge_point: str
    question_type: str
    question_content: str
    answer: str
    difficulty: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/student-data")
async def create_student_data(
    student_data: StudentDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导入学生数据"""
    try:
        db_student = StudentData(
            student_id=student_data.student_id,
            student_name=student_data.student_name,
            subject=student_data.subject,
            grade=student_data.grade,
            homework_scores=student_data.homework_scores,
            learning_behavior=student_data.learning_behavior,
            knowledge_mastery=student_data.knowledge_mastery
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        
        return {"message": "学生数据导入成功", "id": db_student.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入学生数据失败: {str(e)}")


@router.post("/analyze/{student_id}", response_model=AnalysisResult)
async def analyze_student(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """分析学生学情"""
    student_data = db.query(StudentData).filter(StudentData.student_id == student_id).first()
    
    if not student_data:
        raise HTTPException(status_code=404, detail="学生数据不存在")
    
    # 准备分析数据
    analysis_data = {
        "homework_scores": student_data.homework_scores,
        "learning_behavior": student_data.learning_behavior,
        "knowledge_mastery": student_data.knowledge_mastery
    }
    
    # 执行分析
    result = analysis_service.analyze_student(analysis_data)
    
    return result


@router.post("/train-model")
async def train_analysis_model(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """训练学情分析模型"""
    try:
        # 获取所有学生数据
        all_students = db.query(StudentData).all()
        
        if len(all_students) < 10:
            raise HTTPException(
                status_code=400,
                detail="训练数据不足，至少需要10条学生数据"
            )
        
        # 准备训练数据
        training_data = []
        for student in all_students:
            training_data.append({
                "homework_scores": student.homework_scores,
                "learning_behavior": student.learning_behavior,
                "knowledge_mastery": student.knowledge_mastery
            })
        
        # 训练模型
        analysis_service.train_model(training_data)
        
        return {"message": "模型训练成功", "training_samples": len(training_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型训练失败: {str(e)}")


@router.post("/questions/generate", response_model=List[QuestionItem])
async def generate_questions(
    request: QuestionGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成题目"""
    try:
        # 调用AI服务生成题目
        questions = ai_service.generate_questions(
            knowledge_point=request.knowledge_point,
            subject=request.subject,
            question_types=request.question_types,
            count=request.count
        )
        
        # 保存到题库
        for q in questions:
            question_bank = QuestionBank(
                subject=request.subject,
                knowledge_point=request.knowledge_point,
                question_type=q.get("type", "choice"),
                question_content=q.get("question", ""),
                answer=q.get("answer", ""),
                difficulty="medium"
            )
            db.add(question_bank)
        
        db.commit()
        
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成题目失败: {str(e)}")


@router.get("/questions", response_model=List[QuestionBankItem])
async def get_questions(
    subject: Optional[str] = None,
    knowledge_point: Optional[str] = None,
    question_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取题库题目"""
    query = db.query(QuestionBank)
    
    if subject:
        query = query.filter(QuestionBank.subject == subject)
    if knowledge_point:
        query = query.filter(QuestionBank.knowledge_point.contains(knowledge_point))
    if question_type:
        query = query.filter(QuestionBank.question_type == question_type)
    
    questions = query.order_by(QuestionBank.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return questions


@router.post("/questions/export")
async def export_questions(
    question_ids: List[int],
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出题目"""
    questions = db.query(QuestionBank)\
        .filter(QuestionBank.id.in_(question_ids))\
        .all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="未找到题目")
    
    if format == "json":
        result = []
        for q in questions:
            result.append({
                "id": q.id,
                "subject": q.subject,
                "knowledge_point": q.knowledge_point,
                "question_type": q.question_type,
                "question_content": q.question_content,
                "answer": q.answer,
                "difficulty": q.difficulty
            })
        return {"format": "json", "data": result}
    else:
        # 可以扩展为其他格式（如Word、Excel）
        raise HTTPException(status_code=400, detail="不支持的导出格式")


@router.post("/questions/export-word")
async def export_questions_to_word(
    question_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出题目为Word文档"""
    from fastapi.responses import FileResponse
    from services.multimedia_service import multimedia_service
    import os
    from datetime import datetime
    
    questions = db.query(QuestionBank)\
        .filter(QuestionBank.id.in_(question_ids))\
        .all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="未找到题目")
    
    # 准备题目数据
    questions_data = []
    for q in questions:
        questions_data.append({
            "subject": q.subject,
            "knowledge_point": q.knowledge_point,
            "question_type": q.question_type,
            "question_content": q.question_content,
            "answer": q.answer,
            "difficulty": q.difficulty
        })
    
    # 生成Word文档
    word_dir = os.path.join(settings.UPLOAD_DIR, "word")
    os.makedirs(word_dir, exist_ok=True)
    
    filename = f"question_bank_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
    file_path = os.path.join(word_dir, filename)
    
    # 创建Word文档
    from docx import Document
    from docx.shared import Pt, RGBColor as DocxRGBColor
    
    doc = Document()
    
    # 设置文档样式
    style = doc.styles['Normal']
    style.font.name = '微软雅黑'
    style.font.size = Pt(12)
    
    # 添加标题
    title = doc.add_heading('题库导出', 0)
    try:
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    except:
        pass
    
    # 添加题目
    for i, q in enumerate(questions_data, 1):
        # 题目编号和类型
        doc.add_heading(f'第{i}题 ({get_question_type_name(q["question_type"])})', 2)
        
        # 题目内容
        p = doc.add_paragraph()
        p.add_run('题目：').bold = True
        p.add_run(q['question_content'])
        
        # 答案
        p = doc.add_paragraph()
        p.add_run('答案：').bold = True
        p.add_run(q['answer'])
        
        # 分隔线
        if i < len(questions_data):
            doc.add_paragraph('_' * 50)
    
    # 保存文档
    doc.save(file_path)
    
    return FileResponse(
        file_path,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=filename
    )


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除题目"""
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    db.delete(question)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/questions/delete-batch")
async def delete_questions_batch(
    question_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量删除题目"""
    if not question_ids:
        raise HTTPException(status_code=400, detail="请选择要删除的题目")
    
    questions = db.query(QuestionBank).filter(QuestionBank.id.in_(question_ids)).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="未找到要删除的题目")
    
    for question in questions:
        db.delete(question)
    
    db.commit()
    
    return {"message": f"成功删除 {len(questions)} 道题目"}


def get_question_type_name(q_type: str) -> str:
    """获取题目类型名称"""
    type_map = {
        "choice": "选择题",
        "fill": "填空题",
        "short_answer": "简答题"
    }
    return type_map.get(q_type, q_type)

