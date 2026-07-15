from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class TicketInput(BaseModel):
    id: str
    subject: str
    body: str


class TicketResult(BaseModel):
    id: str
    category: str = Field(
        description="Billing, Technical, Account, or General")
    urgency: int = Field(ge=1, le=5, description="1 (low) to 5 (critical)")
    sentiment: Sentiment
    draft_reply: str
    confidence: float = Field(ge=0.0, le=1.0)
    error: Optional[str] = None


class BatchStatus(BaseModel):
    id: str
    total: int
    completed: int
    failed: int
    status: str  # "processing" ou "completed"
