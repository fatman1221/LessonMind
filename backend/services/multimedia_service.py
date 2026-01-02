from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from docx import Document
from docx.shared import Pt, RGBColor as DocxRGBColor
import os
from typing import List, Dict
from config import settings


class MultimediaService:
    """多媒体资源生成服务"""
    
    def generate_ppt(
        self,
        ppt_content: List[Dict],
        output_path: str,
        style: str = "default"
    ) -> str:
        """生成PPT课件"""
        prs = Presentation()
        
        # 设置幻灯片尺寸（16:9）
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
        
        for slide_data in ppt_content:
            slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白布局
            
            # 添加标题
            if "title" in slide_data:
                title_box = slide.shapes.add_textbox(
                    Inches(0.5), Inches(0.5), Inches(9), Inches(1)
                )
                title_frame = title_box.text_frame
                title_frame.text = slide_data["title"]
                title_para = title_frame.paragraphs[0]
                title_para.font.size = Pt(32)
                title_para.font.bold = True
                title_para.font.color.rgb = RGBColor(0, 0, 0)
            
            # 添加内容
            if "content" in slide_data and slide_data["content"]:
                content_y = Inches(2)
                for i, item in enumerate(slide_data["content"]):
                    if i >= 6:  # 限制每页最多6条
                        break
                    
                    content_box = slide.shapes.add_textbox(
                        Inches(1), content_y, Inches(8), Inches(0.8)
                    )
                    content_frame = content_box.text_frame
                    content_frame.text = f"• {item}"
                    content_para = content_frame.paragraphs[0]
                    content_para.font.size = Pt(18)
                    content_para.font.color.rgb = RGBColor(50, 50, 50)
                    content_y += Inches(0.9)
        
        # 保存PPT
        prs.save(output_path)
        return output_path
    
    def generate_word_document(
        self,
        teaching_design: Dict,
        output_path: str
    ) -> str:
        """生成Word文档"""
        doc = Document()
        
        # 设置文档样式
        style = doc.styles['Normal']
        style.font.name = '微软雅黑'
        style.font.size = Pt(12)
        
        # 添加标题
        title_para = doc.add_heading('教学设计', 0)
        # 设置标题居中
        try:
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            title_para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except (ImportError, AttributeError):
            # 如果导入失败，尝试使用数字常量
            try:
                title_para.paragraph_format.alignment = 1  # 1 表示居中
            except:
                pass  # 如果设置失败，继续执行（标题仍然会添加，只是不居中）
        
        # 添加基本信息
        doc.add_heading('一、基本信息', 1)
        p = doc.add_paragraph()
        p.add_run('学科：').bold = True
        p.add_run(teaching_design.get('subject', ''))
        
        p = doc.add_paragraph()
        p.add_run('学段：').bold = True
        p.add_run(teaching_design.get('grade', ''))
        
        p = doc.add_paragraph()
        p.add_run('课时主题：').bold = True
        p.add_run(teaching_design.get('topic', ''))
        
        p = doc.add_paragraph()
        p.add_run('教学目标：').bold = True
        p.add_run(teaching_design.get('teaching_objectives', ''))
        
        # 添加教学设计内容
        content = teaching_design.get('content', {})
        
        if 'import' in content:
            doc.add_heading('二、导入环节', 1)
            import_data = content['import']
            p = doc.add_paragraph()
            p.add_run(f"时间：{import_data.get('time', 0)}分钟")
            doc.add_paragraph(import_data.get('content', ''))
        
        if 'teaching' in content:
            doc.add_heading('三、讲授环节', 1)
            teaching_data = content['teaching']
            p = doc.add_paragraph()
            p.add_run(f"时间：{teaching_data.get('time', 0)}分钟")
            doc.add_paragraph(teaching_data.get('content', ''))
            
            if 'key_points' in teaching_data:
                doc.add_paragraph('重点知识点：')
                for point in teaching_data['key_points']:
                    doc.add_paragraph(f"• {point}", style='List Bullet')
        
        if 'interaction' in content:
            doc.add_heading('四、互动环节', 1)
            interaction_data = content['interaction']
            p = doc.add_paragraph()
            p.add_run(f"时间：{interaction_data.get('time', 0)}分钟")
            
            if 'activities' in interaction_data:
                for activity in interaction_data['activities']:
                    p = doc.add_paragraph()
                    p.add_run(f"{activity.get('type', '')}：").bold = True
                    p.add_run(activity.get('content', ''))
                    p.add_run(f"（{activity.get('time', 0)}分钟）")
        
        if 'summary' in content:
            doc.add_heading('五、总结环节', 1)
            summary_data = content['summary']
            p = doc.add_paragraph()
            p.add_run(f"时间：{summary_data.get('time', 0)}分钟")
            doc.add_paragraph(summary_data.get('content', ''))
        
        if 'expected_outcomes' in content:
            doc.add_heading('六、预期成果', 1)
            doc.add_paragraph(content['expected_outcomes'])
        
        # 保存文档
        doc.save(output_path)
        return output_path


multimedia_service = MultimediaService()

