"""
数学批改提示词模板
"""
import json
from .base import BaseGradingPrompts, PromptTemplate, PromptVersion


class MathGradingPrompts(BaseGradingPrompts):
    """数学批改提示词类"""
    
    @property
    def subject_name(self) -> str:
        return "math"
    
    @property 
    def subject_name_cn(self) -> str:
        return "数学"
    
    def get_grading_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        """获取数学批改提示词模板"""
        
        if version == PromptVersion.V1_0:
            return self._get_v1_0_grading_prompt()
        elif version == PromptVersion.V1_1:
            return self._get_v1_1_grading_prompt()
        elif version == PromptVersion.V2_0:
            return self._get_v2_0_grading_prompt()
        else:
            return self._get_v1_0_grading_prompt()
    
    def get_knowledge_extraction_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        """获取数学知识点提取提示词模板"""
        template = """请分析以下数学题目，提取涉及的知识点：

题目内容：
{question_text}

请按以下JSON格式返回：
{{
  "primary_knowledge_points": ["主要知识点1", "主要知识点2"],
  "secondary_knowledge_points": ["辅助知识点1", "辅助知识点2"],
  "grade_level": "年级",
  "chapter": "章节名称",
  "difficulty_level": 1-5
}}"""
        
        return PromptTemplate(
            template=template,
            version=version,
            description="数学知识点提取提示词",
            parameters={"question_text": "题目内容"},
            expected_output_format="JSON格式的知识点分析"
        )
    
    def _get_v1_0_grading_prompt(self) -> PromptTemplate:
        """V1.0版本数学批改提示词"""
        template = """你是一个严格且有耐心的中学数学老师，请对以下作业进行批改。

要求：
1) 对每道题给出：是否正确(is_correct: true/false)、得分(score)、满分(max_score)、正确答案(correct_answer)、错误分析(error_analysis)、必要时给出分步讲解(solution_steps)
2) 提取涉及的知识点(knowledge_points: ["..."]), 并估计每题难度(difficulty_level: 1-5)和本题掌握程度(mastery_level: 0.0-1.0)
3) 给出总体得分(overall_score)、总分(total_score)、正确率(accuracy_rate)与总体建议(overall_suggestions)
4) 识别薄弱知识点(weak_knowledge_points)和学习建议(study_recommendations)

注意事项：
- 数学计算要准确，步骤要清晰
- 对于几何题，注意图形理解和证明逻辑
- 对于应用题，重点关注解题思路和实际意义
- 答案格式要规范（如分数、小数、单位等）

严格输出JSON，字段：
{format_example}

作业OCR文本如下：
---
{ocr_text}
---
请直接返回JSON，不要包含任何额外解释。"""

        return PromptTemplate(
            template=template,
            version=PromptVersion.V1_0,
            description="数学批改基础版本",
            parameters={"ocr_text": "OCR识别的作业文本", "format_example": "JSON格式示例"},
            expected_output_format="标准JSON批改结果"
        )
    
    def _get_v1_1_grading_prompt(self) -> PromptTemplate:
        """V1.1版本数学批改提示词 - 增强版"""
        template = """你是一位经验丰富的中学数学教师，具有多年教学经验，请认真批改以下数学作业。

批改标准：
1. 准确性评估：计算是否正确，公式应用是否恰当
2. 过程评估：解题步骤是否完整，逻辑是否清晰
3. 格式规范：答案格式是否符合数学表达要求

针对不同题型的特殊要求：
- 计算题：重点检查运算准确性和步骤完整性
- 证明题：关注逻辑推理和证明过程的严谨性
- 应用题：评估建模能力和实际问题理解
- 几何题：注意图形分析和空间想象能力

评分细则：
- 答案完全正确：满分
- 方法正确但有计算错误：扣20%-30%
- 思路基本正确但步骤不完整：扣40%-50%  
- 方法错误：不超过20%

输出严格JSON格式：
{format_example}

学生作业内容：
---
{ocr_text}
---

请仔细分析每道题目，给出详细的批改结果。"""

        return PromptTemplate(
            template=template,
            version=PromptVersion.V1_1,
            description="数学批改增强版本 - 更详细的评分标准",
            parameters={"ocr_text": "OCR识别的作业文本", "format_example": "JSON格式示例"},
            expected_output_format="详细JSON批改结果"
        )
    
    def _get_v2_0_grading_prompt(self) -> PromptTemplate:
        """V2.0版本数学批改提示词 - 智能分析版"""
        template = """作为AI数学教学助手，我将为这份作业提供全面的智能分析和个性化指导。

智能分析维度：
1. 知识掌握度分析：基于解答质量评估各知识点掌握情况
2. 能力素养评估：运算能力、逻辑推理、空间想象、建模应用
3. 错误模式识别：常见错误类型和产生原因分析
4. 个性化建议：针对性的学习改进方案

数学核心素养评估：
- 数学抽象：从具体情境中抽象出数学概念和规律
- 逻辑推理：基于数学规则进行有效推理
- 数学建模：解决实际问题的数学化过程
- 数学运算：算理理解和运算求解
- 直观想象：几何直观和空间想象
- 数据分析：收集、整理、分析数据

学习诊断要点：
- 基础概念理解程度
- 方法技能熟练程度  
- 思维能力发展水平
- 学习习惯和态度

JSON输出格式：
{format_example}

同时增加以下字段：
- "capability_assessment": 能力素养评估
- "error_patterns": 错误模式分析
- "personalized_plan": 个性化学习计划

作业内容：
---
{ocr_text}
---

请进行深度智能分析。"""

        return PromptTemplate(
            template=template,
            version=PromptVersion.V2_0,
            description="数学批改智能分析版本 - 核心素养和个性化指导",
            parameters={"ocr_text": "OCR识别的作业文本", "format_example": "JSON格式示例"},
            expected_output_format="智能分析JSON结果"
        )
    
    def get_format_example(self) -> str:
        """获取数学批改JSON格式示例"""
        example = self.get_standard_output_format()
        # 为数学科目添加特定字段
        if "questions" in example and len(example["questions"]) > 0:
            example["questions"][0].update({
                "calculation_accuracy": 0.9,  # 计算准确性
                "method_correctness": True,    # 方法正确性
                "step_completeness": 0.8,     # 步骤完整性
                "answer_format": "规范"       # 答案格式
            })
        
        return json.dumps(example, ensure_ascii=False, indent=2)


# 单例模式的数学提示词管理器
math_prompts = MathGradingPrompts()
