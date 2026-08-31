from pydantic import BaseModel, Field

class EvaluationResult(BaseModel):
    """Schema for the LLM-as-a-judge automated RAG evaluation."""
    groundedness_score: int = Field(..., ge=1, le=5, description="1-5 score. 5 means the answer is perfectly supported by the context with zero hallucination. 1 means complete hallucination or contradiction.")
    relevance_score: int = Field(..., ge=1, le=5, description="1-5 score. 5 means the answer perfectly addresses the user's query. 1 means it is completely irrelevant.")
    pico_completeness: bool = Field(..., description="True if Population, Intervention, and Outcome were successfully extracted from the query/context.")
    reasoning: str = Field(..., description="Detailed explanation justifying the given scores.")
