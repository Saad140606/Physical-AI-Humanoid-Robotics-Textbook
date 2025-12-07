"""Main FastAPI application for RAG chatbot."""

import os
import sys

# Initialize settings before importing routes
if not os.path.exists('.env'):
    print("WARNING: .env file not found. Copy .env.example to .env and configure it.")

from config import settings

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.routes import chat, documents, health

    app = FastAPI(
        title="AI Robotics RAG Chatbot API",
        description="FastAPI backend for RAG-powered chatbot with Qdrant vector database",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/health", tags=["Health"])
    app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
    app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])

    print("[STARTUP] Starting AI Robotics RAG Chatbot Backend")
except Exception as e:
    print(f"ERROR during app initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Robotics RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
