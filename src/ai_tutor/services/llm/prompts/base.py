"""
提示词模板基础框架
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
import json

class PromptVersion(Enum):
    """提示词版本枚举"""
    V1_0 = "v1.0"
    V1_1 = "v1.1"
    V2_0 = "v2.0"

@dataclass
class PromptTemplate:
    """提示词模板数据类"""
    template: str
    version: PromptVersion
    description: str
    parameters: Dict[str, str]
    expected_output_format: str
    
    def format(self, **kwargs) -> str:
        """格式化提示词模板"""
        # 验证所需参数
        missing_params = set(self.parameters.keys()) - set(kwargs.keys())
        if missing_params:
            raise ValueError(f"缺少必需参数: {missing_params}")
        
        return self.template.format(**kwargs)


class BaseGradingPrompts(ABC):
    """批改提示词基类"""
    
    @property
    @abstractmethod
    def subject_name(self) -> str:
        """科目名称"""
        pass
    
    @property 
    @abstractmethod
    def subject_name_cn(self) -> str:
        """科目中文名称"""
        pass
        
    @abstractmethod
    def get_grading_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        """获取批改提示词模板"""
        pass
    
    @abstractmethod
    def get_knowledge_extraction_prompt(self, version: PromptVersion = PromptVersion.V1_0) -> PromptTemplate:
        """获取知识点提取提示词模板"""
        pass
    
    def get_standard_output_format(self) -> Dict[str, Any]:
        """获取标准输出格式"""
        return {
            "questions": [
                {
                    "question_number": 1,
                    "question_text": "题目原文",
                    "student_answer": "学生答案",
                    "is_correct": True,
                    "score": 5,
                    "max_score": 5,
                    "correct_answer": "正确答案", 
                    "error_analysis": "错误分析（如有）",
                    "solution_steps": ["解题步骤1", "解题步骤2"],
                    "knowledge_points": ["知识点1", "知识点2"],
                    "difficulty_level": 3,
                    "mastery_level": 0.8
                }
            ],
            "overall_score": 85.0,
            "total_score": 100.0,
            "accuracy_rate": 0.85,
            "overall_suggestions": "整体评价和建议",
            "weak_knowledge_points": ["需要加强的知识点"],
            "study_recommendations": ["学习建议1", "学习建议2"]
        }


class PromptManager:
    """提示词管理器 - 支持A/B测试"""
    
    def __init__(self):
        self._ab_test_configs = {}
        self._default_versions = {}
    
    def set_ab_test(self, subject: str, version_a: PromptVersion, version_b: PromptVersion, traffic_split: float = 0.5):
        """设置A/B测试"""
        if not 0 <= traffic_split <= 1:
            raise ValueError("traffic_split必须在0-1之间")
        
        self._ab_test_configs[subject] = {
            "version_a": version_a,
            "version_b": version_b,
            "traffic_split": traffic_split
        }
    
    def get_prompt_version(self, subject: str, user_id: Optional[str] = None) -> PromptVersion:
        """根据A/B测试配置获取提示词版本"""
        if subject not in self._ab_test_configs:
            return self._default_versions.get(subject, PromptVersion.V1_0)
        
        config = self._ab_test_configs[subject]
        
        # 简单的哈希分桶策略
        if user_id:
            hash_value = hash(user_id) % 100
            if hash_value < config["traffic_split"] * 100:
                return config["version_a"]
            else:
                return config["version_b"]
        else:
            # 无用户ID时使用默认版本
            return config["version_a"]
    
    def set_default_version(self, subject: str, version: PromptVersion):
        """设置默认版本"""
        self._default_versions[subject] = version
