"""Configuration settings for the RAG chatbot backend."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Keys
    openai_api_key: str
    # Google Gemini (Generative AI) API key (optional)
    gemini_api_key: Optional[str] = None
    # Anthropic Claude API key (optional)
    claude_api_key: Optional[str] = None
    # LLM provider: 'openai' (default) or 'google' or 'claude'
    llm_provider: str = "openai"
    
    # Qdrant Configuration
    qdrant_api_key: str
    qdrant_url: str = "https://your-qdrant-cluster.qdrant.io"
    qdrant_collection_name: str = "ai-robotics-textbook"
    
    # Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:3000/",
        "http://localhost:3000/ai-robotics-textbook",
        "http://localhost:3000/ai-robotics-textbook/",
        "http://localhost:8000",
        "https://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]
    
    # RAG Configuration
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4"
    max_tokens: int = 2048
    temperature: float = 0.7
    top_k_results: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
