from pydantic import BaseModel
from typing import List, Optional
from typing_extensions import TypedDict


class ChatMemory(BaseModel):
    user: str
    assistant: Optional[str] = None
    sentiment_score: float
    sentiment_type: str

class ShortTermMemory(BaseModel):
    chats: List[ChatMemory]
    max_chats: int = 5

class ExtractedMemory(TypedDict):
    name: Optional[str] = None
    age: Optional[str] = None
    location: Optional[str] = None
    current_mood: Optional[str] = None

class SummaryEntry(BaseModel):
    summary: str
    general_mood: str
    timestamp: str

class SummaryMemory(BaseModel):
    summaries: List[SummaryEntry]
    max_summaries: int = 10

class Context(BaseModel):
    user_id: str = "default_user"

class local(BaseModel):
    chat: List[ChatMemory]

class moodshift(BaseModel):
    moodshift: local
