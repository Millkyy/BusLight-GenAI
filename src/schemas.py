from typing import Literal
from pydantic import BaseModel, Field

class Citation(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    url: str = ""

class AssistantResponse(BaseModel):
    status: Literal["answered", "abstained"]
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    reason: str = ""
