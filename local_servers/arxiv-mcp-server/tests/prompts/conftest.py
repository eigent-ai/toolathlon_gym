"""Test fixtures for prompt tests."""

import pytest
from typing import Dict, Any


@pytest.fixture
def mock_paper_content() -> str:
    """Sample paper content for testing."""
    return """# Test Paper Title

## Abstract
This is a test paper abstract.

## Introduction
Test introduction content.

## Methods
Test methodology section.

## Results
Test results section.

## Discussion
Test discussion section.

## References
1. Test reference
"""


@pytest.fixture
def research_discovery_args() -> Dict[str, Any]:
    """Sample arguments for research discovery prompt."""
    return {
        "topic": "machine learning",
        "expertise_level": "intermediate",
        "time_period": "2023-present",
    }


@pytest.fixture
def paper_analysis_args() -> Dict[str, Any]:
    """Sample arguments for paper analysis prompt."""
    return {"paper_id": "2401.12345", "focus_area": "methodology"}


@pytest.fixture
def literature_synthesis_args() -> Dict[str, Any]:
    """Sample arguments for literature synthesis prompt."""
    return {"paper_ids": ["2401.12345", "2401.67890"], "synthesis_type": "themes"}


@pytest.fixture(autouse=True)
def clean_paper_manager():
    """Reset the paper manager singleton between tests."""
    # Reset before each test
    global paper_manager
    paper_manager = None
    yield
    # Reset after each test
    paper_manager = None
