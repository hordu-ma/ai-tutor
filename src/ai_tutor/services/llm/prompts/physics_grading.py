"""
物理批改提示词模板
"""
import json
from .base import BaseGradingPrompts, PromptTemplate, PromptVersion


class PhysicsGradingPrompts(BaseGradingPrompts):
    """物理批改提示词类"""
    
    @property
    def subject_name(self) -> str:
        return "physics"
    
    @property 
    def subject_name_cn(self) -> str:
        return "物理"
    
    def get_grading_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        """获取物理批改提示词模板"""
        template = """你是一名专业的中学物理教师，请对以下物理作业进行批改。

物理学科特点：
1. 公式应用：检查物理公式使用是否正确，推导是否合理
2. 单位系统：重点关注物理单位的正确性和一致性
3. 物理思想：评估物理概念理解和物理思维方法
4. 实验分析：对于实验题，关注实验设计和数据分析
5. 图像理解：检查物理图像的读取和分析能力

批改要点：
- 物理量的定义和意义理解
- 物理定律和规律的应用
- 数学工具在物理中的运用
- 物理现象的解释和分析
- 实际问题的物理建模

严格输出JSON格式：
{format_example}

学生作业内容：
---
{ocr_text}
---

请仔细分析每道物理题，注意公式推导和单位换算。"""

        return PromptTemplate(
            template=template,
            version=version,
            description="物理批改基础版本",
            parameters={"ocr_text": "OCR识别的作业文本", "format_example": "JSON格式示例"},
            expected_output_format="标准JSON批改结果"
        )
    
    def get_knowledge_extraction_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        """获取物理知识点提取提示词模板"""
        template = """请分析以下物理题目，提取涉及的知识点：

题目内容：
{question_text}

请按以下JSON格式返回：
{{
  "physics_branch": "力学/电学/热学/光学/原子物理",
  "primary_concepts": ["主要物理概念1", "主要物理概念2"],
  "formulas_involved": ["涉及公式1", "涉及公式2"],
  "physical_laws": ["物理定律1", "物理定律2"],
  "grade_level": "年级",
  "difficulty_level": 1-5,
  "experiment_related": true/false
}}"""
        
        return PromptTemplate(
            template=template,
            version=version,
            description="物理知识点提取提示词",
            parameters={"question_text": "题目内容"},
            expected_output_format="JSON格式的物理知识点分析"
        )
    
    def get_format_example(self) -> str:
        """获取物理批改JSON格式示例"""
        example = self.get_standard_output_format()
        # 为物理科目添加特定字段
        if "questions" in example and len(example["questions"]) > 0:
            example["questions"][0].update({
                "formula_usage": "牛顿第二定律：F=ma",  # 公式使用
                "unit_consistency": True,              # 单位一致性
                "physical_reasoning": "良好",          # 物理推理
                "graph_analysis": "能正确读取图像"     # 图像分析
            })
        
        return json.dumps(example, ensure_ascii=False, indent=2)


# 单例模式的物理提示词管理器  
physics_prompts = PhysicsGradingPrompts()
