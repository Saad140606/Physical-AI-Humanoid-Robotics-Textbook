"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., description="User query")
    conversation_history: Optional[List[dict]] = Field(
        None,
        description="Conversation history for context"
    )
    top_k: Optional[int] = Field(
        5,
        description="Number of documents to retrieve"
    )
    use_agent: Optional[str] = Field(
        None,
        description="Optional subagent to use (e.g., 'document_search', 'code_agent', 'citation_agent')"
    )


class ChatWithSelectionRequest(BaseModel):
    """Chat request with text selection."""
    query: str = Field(..., description="User query")
    selected_text: str = Field(..., description="Selected text from the textbook")


class DocumentChunk(BaseModel):
    """Document chunk model."""
    id: str
    text: str
    score: float
    metadata: dict
    source: str


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    retrieved_documents: List[DocumentChunk]
    model: str
    agent_used: Optional[str] = Field(
        None,
        description="Subagent used to generate this response (if any)"
    )


class UploadDocumentRequest(BaseModel):
    """Upload document request model."""
    title: str
    content: str
    source: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    vector_db_connected: bool
    message: Optional[str] = None
