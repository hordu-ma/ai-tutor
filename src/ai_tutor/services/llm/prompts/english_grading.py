"""
英语批改提示词模板（占位，后续可细化）
"""
from .base import BaseGradingPrompts, PromptTemplate, PromptVersion


class EnglishGradingPrompts(BaseGradingPrompts):
    @property
    def subject_name(self) -> str:
        return "english"

    @property
    def subject_name_cn(self) -> str:
        return "英语"

    def get_grading_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        template = "请对以下英语作业进行批改，并按标准JSON输出。\n---\n{ocr_text}\n---"
        return PromptTemplate(
            template=template,
            version=version,
            description="英语批改基础版本",
            parameters={"ocr_text": "OCR识别的作业文本"},
            expected_output_format="标准JSON批改结果"
        )

    def get_knowledge_extraction_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        template = "请对以下英语题目提取知识点：\n{question_text}"
        return PromptTemplate(
            template=template,
            version=version,
            description="英语知识点提取提示词",
            parameters={"question_text": "题目内容"},
            expected_output_format="JSON"
        )

