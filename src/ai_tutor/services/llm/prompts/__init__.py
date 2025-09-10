"""
提示词模板包
"""
from .math_grading import MathGradingPrompts
from .english_grading import EnglishGradingPrompts  
from .physics_grading import PhysicsGradingPrompts
from .base import PromptTemplate, PromptVersion

__all__ = [
    "MathGradingPrompts",
    "EnglishGradingPrompts", 
    "PhysicsGradingPrompts",
    "PromptTemplate",
    "PromptVersion"
]
