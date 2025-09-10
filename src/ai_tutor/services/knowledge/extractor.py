from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type

from ai_tutor.core.logger import get_logger
from ai_tutor.services.llm.base import LLMService, get_llm_service

logger = get_logger(__name__)


class KnowledgeExtractor(ABC):
    """
    Abstract base class for knowledge point extraction services.
    Each implementation should be specific to a subject.
    """

    def __init__(self, llm_service: LLMService | None = None):
        """
        Initializes the extractor, optionally with a specific LLM service.
        """
        self.llm_service = llm_service or get_llm_service()

    @abstractmethod
    async def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts knowledge points from a given text.

        Args:
            text: The text content of the question or material.

        Returns:
            A list of dictionaries, where each dictionary represents a knowledge point.
        """
        pass

    @classmethod
    @abstractmethod
    def get_subject(cls) -> str:
        """
        Returns the subject supported by this extractor (e.g., 'math', 'physics').
        """
        pass


# --- Factory and Registry ---

_extractor_registry: Dict[str, Type[KnowledgeExtractor]] = {}


def register_extractor(cls: Type[KnowledgeExtractor]) -> Type[KnowledgeExtractor]:
    """
    A class decorator to register new knowledge extractor classes.
    """
    subject = cls.get_subject()
    if subject in _extractor_registry:
        logger.warning(f"Knowledge extractor for subject '{subject}' is being overridden.")
    logger.info(f"Registering knowledge extractor for subject: {subject}")
    _extractor_registry[subject] = cls
    return cls


def get_knowledge_extractor(subject: str) -> KnowledgeExtractor:
    """
    Factory function to get an instance of the appropriate knowledge extractor
    for a given subject.

    Args:
        subject: The subject for which to get the extractor.

    Returns:
        An instance of a KnowledgeExtractor subclass.

    Raises:
        ValueError: If no extractor is registered for the given subject.
    """
    extractor_class = _extractor_registry.get(subject)
    if not extractor_class:
        logger.error(f"No knowledge extractor found for subject: {subject}")
        raise ValueError(f"Unsupported subject for knowledge extraction: {subject}")

    logger.debug(f"Instantiating knowledge extractor for subject: {subject}")
    return extractor_class()
