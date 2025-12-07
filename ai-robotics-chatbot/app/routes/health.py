"""Health check routes."""

from fastapi import APIRouter, HTTPException
from app.models import HealthCheckResponse
from app.vector_db import vector_db
from app.agents import get_subagent_registry
from config import settings

router = APIRouter()


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Check API health and dependencies."""
    try:
        # Check Qdrant connection
        try:
            vector_db.client.get_collection(vector_db.collection_name)
            db_connected = True
        except Exception as e:
            print(f"Qdrant connection error: {e}")
            db_connected = False
        
        # Get subagent count
        try:
            registry = get_subagent_registry()
            agent_count = len(registry.list_all())
        except Exception:
            agent_count = 0
        
        # Build response with provider info
        if db_connected:
            return HealthCheckResponse(
                status="healthy",
                vector_db_connected=True,
                message=f"All systems operational (LLM: {settings.llm_provider}, Agents: {agent_count})"
            )
        else:
            return HealthCheckResponse(
                status="degraded",
                vector_db_connected=False,
                message=f"Qdrant vector database connection failed (LLM: {settings.llm_provider}, Agents: {agent_count})"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
