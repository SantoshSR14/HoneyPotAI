# models.py
from pydantic import BaseModel
from typing import List, Optional, Literal

class Message(BaseModel):
    sender: Literal["scammer", "user"]
    text: str
    timestamp: int

class Metadata(BaseModel):
    channel: Optional[str]
    language: Optional[str]
    locale: Optional[str]

class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[Metadata]

class HoneypotResponse(BaseModel):
    status: str
    reply: str
