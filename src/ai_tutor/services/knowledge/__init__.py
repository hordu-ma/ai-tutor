from .extractor import (
    KnowledgeExtractor,
    get_knowledge_extractor,
    register_extractor,
)

# Import subject-specific extractors to ensure they are registered
from . import math
from . import physics

__all__ = [
    "KnowledgeExtractor",
    "get_knowledge_extractor",
    "register_extractor",
    "math",
    "physics",
]
