from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)

class SourceReference(BaseModel):
    source: str
    page: str

class AskResponse(BaseModel):
    request_id: str
    answer: str
    sources: list[SourceReference]
