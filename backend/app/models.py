from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class ConfigUpdate(BaseModel):
    START: Optional[int] = Field(None, description="Starting lecture index")
    NUM_LECS: Optional[int] = Field(None, description="Number of lectures to process")
    MODEL: Optional[str] = Field(None, description="OpenAI model to use")
    GET_TRANSCRIPTS: Optional[bool] = Field(None, description="Generate transcripts")
    GET_KEY_POINTS: Optional[bool] = Field(None, description="Generate key points")
    GET_Q_AND_A: Optional[bool] = Field(None, description="Generate questions and answers")
    TRY_REUSE_NOTES: Optional[bool] = Field(None, description="Try to reuse existing notes")
    IS_BOOK: Optional[bool] = Field(None, description="Content is from a book rather than lectures")

class LectureData(BaseModel):
    index: int
    title: str
    content: str

class ProcessedLecture(BaseModel):
    index: int
    title: str
    study_notes: str
    transcript: Optional[str] = None
    questions: Optional[str] = None
    answers: Optional[str] = None
    key_points: Optional[str] = None
    cost: float

class MergeResponse(BaseModel):
    message: str
    page_count: int
    bookmark_count: int

class ExtractionResponse(BaseModel):
    message: str
    lecture_count: int
    lectures: List[LectureData]

class ProcessingResponse(BaseModel):
    message: str
    total_cost: float
    processed_count: int
    results: List[ProcessedLecture]

class StatusResponse(BaseModel):
    status: str
    config: Dict[str, Any]
