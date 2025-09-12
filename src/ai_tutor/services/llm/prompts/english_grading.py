"""
英语批改提示词模板 - 专业版
"""
import json
from .base import BaseGradingPrompts, PromptTemplate, PromptVersion


class EnglishGradingPrompts(BaseGradingPrompts):
    """英语批改提示词类 - 支持语法、词汇、写作等全面评估"""
    
    @property
    def subject_name(self) -> str:
        return "english"

    @property
    def subject_name_cn(self) -> str:
        return "英语"

    def get_grading_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        """获取英语批改提示词模板"""
        
        if version == PromptVersion.V1_0:
            return self._get_v1_0_grading_prompt()
        elif version == PromptVersion.V1_1:
            return self._get_v1_1_grading_prompt()
        elif version == PromptVersion.V2_0:
            return self._get_v2_0_grading_prompt()
        else:
            return self._get_v1_0_grading_prompt()

    def get_knowledge_extraction_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        """获取英语知识点提取提示词模板"""
        template = """请分析以下英语题目，提取涉及的知识点：

题目内容：
{question_text}

请按以下JSON格式返回：
{{
  "grammar_points": ["语法点1", "语法点2"],
  "vocabulary_level": "基础/中级/高级",
  "skills_tested": ["阅读理解", "语法应用", "词汇运用"],
  "question_type": "选择题/填空题/作文题/阅读理解",
  "grade_level": "年级",
  "difficulty_level": 1-5,
  "language_features": ["时态", "语态", "句型结构"]
}}"""
        
        return PromptTemplate(
            template=template,
            version=version,
            description="英语知识点提取提示词",
            parameters={"question_text": "题目内容"},
            expected_output_format="JSON格式的英语知识点分析"
        )
    
    def _get_v1_0_grading_prompt(self) -> PromptTemplate:
        """V1.0版本英语批改提示词 - 基础版"""
        template = """你是一位经验丰富的英语教师，请对以下英语作业进行专业批改。

批改重点：
1) 语法准确性：检查时态、语态、句型结构等语法要素
2) 词汇使用：评估词汇选择的准确性和多样性
3) 句式结构：分析句子结构的完整性和复杂性
4) 表达流畅性：评估整体表达的连贯性和逻辑性
5) 拼写准确性：检查单词拼写和标点符号使用

评分标准：
- 语法正确且表达自然：满分
- 语法基本正确但表达略显生硬：扣10-20%
- 有语法错误但意思可理解：扣30-50%
- 语法错误较多影响理解：扣60-70%
- 基本无法理解：扣80%以上

对每道题给出：
- 是否正确(is_correct)、得分(score)、满分(max_score)
- 语法错误分析(grammar_errors)
- 词汇使用评价(vocabulary_assessment)
- 改进建议(improvement_suggestions)
- 知识点涉及(knowledge_points)

严格输出JSON格式：
{format_example}

学生作业内容：
---
{ocr_text}
---

请仔细分析并给出详细的英语批改结果。"""

        return PromptTemplate(
            template=template,
            version=PromptVersion.V1_0,
            description="英语批改基础版本 - 语法词汇重点",
            parameters={"ocr_text": "OCR识别的作业文本", "format_example": "JSON格式示例"},
            expected_output_format="标准JSON批改结果"
        )
    
    def _get_v1_1_grading_prompt(self) -> PromptTemplate:
        """V1.1版本英语批改提示词 - 增强版"""
        template = """作为专业的英语教学专家，我将为这份英语作业提供全面的批改和指导。

英语学科特色评估：
1. 语言准确性：语法、词汇、拼写的准确程度
2. 语言流畅性：句子连接、段落过渡、整体连贯性
3. 语言复杂性：句式多样性、词汇丰富度、表达层次
4. 语言得体性：语域选择、文体一致性、表达恰当性
5. 交际有效性：信息传达、意图表达、读者意识

不同题型批改重点：
- 语法填空：关注语法规则掌握和语境理解
- 完形填空：重视语篇理解和词汇运用
- 阅读理解：评估阅读技巧和信息处理能力
- 书面表达：综合评价写作技能和创新思维
- 翻译题：检查语言转换和文化理解

错误分析分类：
- 语法错误：时态、语态、句法结构等
- 词汇错误：词义、搭配、词性等
- 拼写错误：单词拼写、标点符号
- 语篇错误：逻辑、衔接、组织结构

JSON输出格式：
{format_example}

学生作业：
---
{ocr_text}
---

请提供详细的英语学习诊断和改进方案。"""

        return PromptTemplate(
            template=template,
            version=PromptVersion.V1_1,
            description="英语批改增强版本 - 语言技能全面评估",
            parameters={"ocr_text": "OCR识别的作业文本", "format_example": "JSON格式示例"},
            expected_output_format="详细JSON批改结果"
        )
    
    def _get_v2_0_grading_prompt(self) -> PromptTemplate:
        """V2.0版本英语批改提示词 - 智能分析版"""
        template = """作为AI英语教学助手，我将运用先进的语言分析技术为这份作业提供智能化批改和个性化指导。

英语核心素养评估：
1. 语言能力：语音、词汇、语法、语篇的综合运用
2. 文化意识：中外文化理解、跨文化交际能力
3. 思维品质：逻辑性、批判性、创新性思维
4. 学习能力：语言学习策略、自主学习能力

智能分析维度：
- 语言复杂度分析：句法复杂度、词汇多样性指标
- 错误模式识别：系统性错误、偶发性错误分类
- 学习进度评估：与年级水平对比、个人进步轨迹
- 个性化诊断：优势领域识别、薄弱环节定位

写作评估框架（适用于作文题）：
- 内容维度：思想深度、信息完整性、创意表达
- 结构维度：组织逻辑、段落安排、过渡自然
- 语言维度：准确性、流畅性、多样性、得体性
- 效果维度：目标达成、读者意识、交际效果

学习建议个性化：
- 基于错误分析的针对性练习
- 词汇扩展和语法强化方案
- 阅读策略和写作技巧提升
- 文化背景知识补充

JSON输出格式（增强字段）：
{format_example}

新增评估字段：
- "language_complexity": 语言复杂度分析
- "error_patterns": 错误模式识别
- "cultural_awareness": 文化意识评估
- "learning_strategies": 学习策略建议
- "personalized_plan": 个性化学习计划

学生作业：
---
{ocr_text}
---

请进行全面的智能化英语学习分析。"""

        return PromptTemplate(
            template=template,
            version=PromptVersion.V2_0,
            description="英语批改智能分析版本 - 核心素养和个性化指导",
            parameters={"ocr_text": "OCR识别的作业文本", "format_example": "JSON格式示例"},
            expected_output_format="智能分析JSON结果"
        )
    
    def get_format_example(self) -> str:
        """获取英语批改JSON格式示例"""
        example = self.get_standard_output_format()
        # 为英语科目添加特定字段
        if "questions" in example and len(example["questions"]) > 0:
            example["questions"][0].update({
                "grammar_accuracy": 0.85,           # 语法准确性
                "vocabulary_appropriateness": 0.9,  # 词汇恰当性
                "sentence_structure": "良好",       # 句子结构
                "spelling_accuracy": 0.95,          # 拼写准确性
                "fluency_score": 0.8,               # 流畅性得分
                "grammar_errors": [                 # 语法错误详情
                    "时态错误：should be 'went' instead of 'go'",
                    "主谓一致：'he have' should be 'he has'"
                ],
                "vocabulary_assessment": {           # 词汇评估
                    "level": "中级",
                    "diversity": 0.7,
                    "suggestions": ["可使用更多高级词汇"]
                },
                "writing_quality": {                # 写作质量（适用于作文）
                    "content_score": 0.8,
                    "organization_score": 0.85,
                    "language_score": 0.75,
                    "effectiveness_score": 0.8
                }
            })
            
            # 添加整体评估字段
            example.update({
                "language_level": "中级",              # 整体语言水平
                "improvement_priority": [             # 优先改进项
                    "语法准确性", "词汇多样性"
                ],
                "strengths": [                        # 优势
                    "句式结构较好", "表达清晰"
                ],
                "cultural_awareness_score": 0.7,      # 文化意识得分
                "learning_suggestions": [             # 学习建议
                    "加强时态练习",
                    "扩大词汇量",
                    "多读英文原著"
                ]
            })
        
        return json.dumps(example, ensure_ascii=False, indent=2)


# 单例模式的英语提示词管理器
english_prompts = EnglishGradingPrompts()

