import dashscope
from dashscope import Generation
from typing import List, Dict, Optional
from config import settings
import json

dashscope.api_key = settings.DASHSCOPE_API_KEY


class QwenAIService:
    """通义千问AI服务"""
    
    def __init__(self):
        self.model = "qwen-turbo"  # 或 "qwen-plus", "qwen-max"
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """聊天对话"""
        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                temperature=temperature,
                result_format='message'
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                return f"AI服务错误: {response.message}"
        except Exception as e:
            return f"AI服务异常: {str(e)}"
    
    def generate_teaching_design(
        self,
        subject: str,
        grade: str,
        topic: str,
        objectives: str
    ) -> Dict:
        """生成教学设计"""
        prompt = f"""你是一位经验丰富的{subject}教师，需要为{grade}学生设计一堂关于"{topic}"的课程。

教学目标：
{objectives}

请生成一份完整的教学设计，要求包含以下内容：
1. 导入环节（5分钟）：设计吸引学生注意力的导入方式
2. 讲授环节（25分钟）：详细的教学内容讲解
3. 互动环节（10分钟）：至少3个互动设计，包括提问、讨论、活动等
4. 总结环节（5分钟）：课程总结和知识巩固
5. 时间分配：明确每个环节的时间安排
6. 预期成果：学生应该达到的学习效果

请以JSON格式返回，格式如下：
{{
    "import": {{
        "title": "导入环节",
        "time": 5,
        "content": "...",
        "method": "..."
    }},
    "teaching": {{
        "title": "讲授环节",
        "time": 25,
        "content": "...",
        "key_points": ["知识点1", "知识点2", ...]
    }},
    "interaction": {{
        "title": "互动环节",
        "time": 10,
        "activities": [
            {{"type": "提问", "content": "...", "time": 3}},
            {{"type": "讨论", "content": "...", "time": 4}},
            {{"type": "活动", "content": "...", "time": 3}}
        ]
    }},
    "summary": {{
        "title": "总结环节",
        "time": 5,
        "content": "..."
    }},
    "expected_outcomes": "..."
}}"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的教学设计师，擅长根据学科特点和教学目标设计高质量的教学方案。"},
            {"role": "user", "content": prompt}
        ]
        
        response = self.chat(messages, temperature=0.7)
        
        # 尝试解析JSON
        try:
            # 提取JSON部分
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            design_data = json.loads(json_str)
            return design_data
        except:
            # 如果解析失败，返回结构化文本
            return {
                "raw_response": response,
                "import": {"title": "导入环节", "time": 5, "content": response[:200]},
                "teaching": {"title": "讲授环节", "time": 25, "content": response[200:600]},
                "interaction": {"title": "互动环节", "time": 10, "activities": []},
                "summary": {"title": "总结环节", "time": 5, "content": response[-200:]},
                "expected_outcomes": "学生能够理解并掌握本节课的核心知识点"
            }
    
    def generate_image_description(self, knowledge_point: str, subject: str) -> str:
        """生成图片描述（用于图片生成）"""
        prompt = f"""为{subject}学科的知识点"{knowledge_point}"生成一张教学图片的描述。
要求：
1. 图片应该清晰展示该知识点的核心内容
2. 适合{subject}学科的教学场景
3. 描述要具体，包含颜色、构图、元素等细节

请直接返回图片描述，不要包含其他内容。"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的教学资源设计师。"},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat(messages, temperature=0.8)
    
    def generate_ppt_content(self, teaching_design: Dict) -> List[Dict]:
        """生成PPT内容"""
        prompt = f"""根据以下教学设计，生成PPT课件的内容大纲。
教学设计：
{json.dumps(teaching_design, ensure_ascii=False, indent=2)}

请为每个教学环节生成对应的PPT页面内容，以JSON数组格式返回，每个元素包含：
{{
    "slide_number": 1,
    "title": "页面标题",
    "content": ["要点1", "要点2", ...],
    "notes": "备注说明"
}}

请生成8-12页PPT内容。"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的PPT设计师，擅长制作教学课件。"},
            {"role": "user", "content": prompt}
        ]
        
        response = self.chat(messages, temperature=0.7)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            ppt_content = json.loads(json_str)
            return ppt_content if isinstance(ppt_content, list) else []
        except:
            return []
    
    def generate_questions(
        self,
        knowledge_point: str,
        subject: str,
        question_types: List[str] = ["choice", "fill", "short_answer"],
        count: int = 3
    ) -> List[Dict]:
        """生成题目"""
        prompt = f"""为{subject}学科的知识点"{knowledge_point}"生成{count}道题目。

要求：
1. 题目类型包括：{', '.join(question_types)}
2. 每道题目包含：题目内容、正确答案、解析
3. 题目难度适中，符合教学要求

请以JSON数组格式返回，格式如下：
[
    {{
        "type": "choice",
        "question": "题目内容",
        "options": ["选项A", "选项B", "选项C", "选项D"],
        "answer": "A",
        "explanation": "解析说明"
    }},
    ...
]"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的题目设计师，擅长根据知识点生成高质量的题目。"},
            {"role": "user", "content": prompt}
        ]
        
        response = self.chat(messages, temperature=0.7)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            questions = json.loads(json_str)
            return questions if isinstance(questions, list) else []
        except:
            return []


ai_service = QwenAIService()

