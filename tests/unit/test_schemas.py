import pytest
from pydantic import ValidationError
from enterprise_rag.api.schemas import AskRequest

def test_empty_question_rejected():
    with pytest.raises(ValidationError):
        AskRequest(question="")

def test_valid_question():
    assert AskRequest(question="What is RAG?").question == "What is RAG?"
