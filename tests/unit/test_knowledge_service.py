import pytest
from unittest.mock import patch

from ai_tutor.services.knowledge import get_knowledge_extractor
from ai_tutor.services.knowledge.math import MathKnowledgeExtractor
from ai_tutor.services.knowledge.physics import PhysicsKnowledgeExtractor

def test_get_knowledge_extractor_factory():
    """
    Tests the get_knowledge_extractor factory function to ensure it returns
    the correct extractor instance and handles unsupported subjects.
    """
    # Test for a registered subject: math
    math_extractor = get_knowledge_extractor("math")
    assert isinstance(math_extractor, MathKnowledgeExtractor)

    # Test for a registered subject: physics
    physics_extractor = get_knowledge_extractor("physics")
    assert isinstance(physics_extractor, PhysicsKnowledgeExtractor)

    # Test that it raises a ValueError for an unregistered subject
    with pytest.raises(ValueError, match="Unsupported subject for knowledge extraction: chemistry"):
        get_knowledge_extractor("chemistry")


@pytest.mark.asyncio
async def test_math_knowledge_extractor_llm_call(mocker):
    """
    Tests the MathKnowledgeExtractor's real LLM call behavior for the success path.
    """
    # 1. Setup: Create an extractor instance and mock the LLM's responses
    extractor = MathKnowledgeExtractor()
    test_text = "What is the solution to x + 5 = 10?"
    mock_llm_response_str = '''
    {
      "knowledge_points": [
        {"name": "一元一次方程", "category": "代数"}
      ]
    }
    '''
    mock_llm_response_json = {
        "knowledge_points": [
            {"name": "一元一次方程", "category": "代数"}
        ]
    }

    # Mock the methods on the llm_service instance that will be called
    mock_generate = mocker.patch.object(extractor.llm_service, 'generate', return_value=mock_llm_response_str)
    mock_safe_parse = mocker.patch.object(extractor.llm_service, 'safe_json_parse', return_value=mock_llm_response_json)

    # 2. Execution: Call the method under test
    result = await extractor.extract(test_text)

    # 3. Assertions: Verify the behavior
    mock_generate.assert_awaited_once()
    mock_safe_parse.assert_called_once_with(mock_llm_response_str)
    assert result == [
        {"name": "一元一次方程", "category": "代数", "subject": "math"}
    ]


@pytest.mark.asyncio
async def test_math_knowledge_extractor_llm_error(mocker):
    """
    Tests the MathKnowledgeExtractor's error handling when the LLM call fails.
    """
    # 1. Setup: Mock the generate method to raise an exception
    extractor = MathKnowledgeExtractor()
    mocker.patch.object(extractor.llm_service, 'generate', side_effect=Exception("LLM API Error"))
    mock_error_logger = mocker.patch('ai_tutor.services.knowledge.math.logger.error')

    # 2. Execution: Call the method under test
    result = await extractor.extract("Some math problem.")

    # 3. Assertions: Verify the error handling
    assert result == []
    mock_error_logger.assert_called_once()


@pytest.mark.asyncio
async def test_physics_knowledge_extractor_placeholder():
    """
    Tests the PhysicsKnowledgeExtractor's current placeholder behavior.
    """
    extractor = PhysicsKnowledgeExtractor()
    assert extractor.get_subject() == "physics"

    with patch('ai_tutor.services.knowledge.physics.logger.warning') as mock_logger_warning:
        result = await extractor.extract("A car accelerates from 0 to 60 mph.")

        # Assert that the placeholder warning was logged
        mock_logger_warning.assert_called_with("Physics knowledge extraction is using placeholder data.")

        # Assert that the placeholder data is returned correctly
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['subject'] == 'physics'
        assert result[0]['name'] == '牛顿运动定律'
