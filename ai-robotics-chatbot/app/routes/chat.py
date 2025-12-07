"""Chat routes for RAG chatbot with subagent support."""

from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatWithSelectionRequest, ChatResponse, DocumentChunk
from app.vector_db import vector_db
from app.llm_service import embedding_service, rag_chat_service
from app.agents import get_subagent_registry
from config import settings

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Send a query to the RAG chatbot.
    
    Optionally use a subagent (e.g., 'document_search', 'code_agent', 'citation_agent').
    The chatbot retrieves relevant documents from the textbook and generates
    a response using the configured LLM provider with the retrieved context.
    """
    try:
        agent_used = None
        
        # If subagent requested, try to invoke it
        if request.use_agent:
            try:
                registry = get_subagent_registry()
                agent_response = await registry.invoke(
                    request.use_agent,
                    request.query,
                    context={"documents": []}
                )
                
                if agent_response.status == "success":
                    agent_used = request.use_agent
                    # Return agent response as the main response
                    return ChatResponse(
                        response=f"[{request.use_agent}] {str(agent_response.result)}",
                        retrieved_documents=[],
                        model=f"{settings.chat_model} (agent: {request.use_agent})",
                        agent_used=request.use_agent
                    )
            except Exception as e:
                print(f"Subagent invocation failed: {e}")
                # Fall through to default behavior
        
        # Default: Generate embedding and search
        query_embedding = await embedding_service.embed_text(request.query)
        
        # Try to search for relevant documents
        retrieved_docs = []
        try:
            retrieved_docs = await vector_db.search(
                query_embedding=query_embedding,
                top_k=request.top_k or settings.top_k_results
            )
        except Exception as db_error:
            print(f"Warning: Vector DB search failed: {db_error}")
            print("Proceeding with empty context...")
        
        # Generate response using RAG
        response_text = await rag_chat_service.generate_response(
            query=request.query,
            context_documents=retrieved_docs,
            conversation_history=request.conversation_history
        )
        
        # Format retrieved documents
        doc_chunks = [
            DocumentChunk(
                id=doc["id"],
                text=doc["text"],
                score=doc["score"],
                metadata=doc["metadata"],
                source=doc["source"]
            )
            for doc in retrieved_docs
        ]
        
        # Use the model that was actually used
        model_used = rag_chat_service.last_model_used or settings.chat_model
        
        return ChatResponse(
            response=response_text,
            retrieved_documents=doc_chunks,
            model=model_used,
            agent_used=agent_used
        )
    
    except Exception as e:
        print(f"Error in chat query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-with-selection", response_model=ChatResponse)
async def chat_with_selection(request: ChatWithSelectionRequest):
    """
    Query the chatbot with selected text from the textbook.
    
    This endpoint allows users to select text from the book and ask questions
    specifically about that selection.
    """
    try:
        # Generate response based on selection
        response_text = await rag_chat_service.generate_response_with_selection(
            query=request.query,
            selected_text=request.selected_text
        )
        
        # Create a document chunk from the selection
        selection_doc = DocumentChunk(
            id="user_selection",
            text=request.selected_text,
            score=1.0,
            metadata={"type": "user_selection"},
            source="Selected from textbook"
        )
        
        # Use the model that was actually used
        model_used = rag_chat_service.last_model_used or settings.chat_model
        
        return ChatResponse(
            response=response_text,
            retrieved_documents=[selection_doc],
            model=model_used
        )
    
    except Exception as e:
        print(f"Error in chat with selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-turn")
async def multi_turn_chat(request: ChatRequest):
    """
    Multi-turn conversation endpoint.
    
    Maintains conversation history across multiple turns for coherent dialogues.
    """
    try:
        # Generate embedding for the query
        query_embedding = await embedding_service.embed_text(request.query)
        
        # Try to search for relevant documents
        retrieved_docs = []
        try:
            retrieved_docs = await vector_db.search(
                query_embedding=query_embedding,
                top_k=request.top_k or settings.top_k_results
            )
        except Exception as db_error:
            print(f"Warning: Vector DB search failed: {db_error}")
            print("Proceeding with empty context...")
        
        # Generate response with conversation history
        response_text = await rag_chat_service.generate_response(
            query=request.query,
            context_documents=retrieved_docs,
            conversation_history=request.conversation_history
        )
        
        # Format retrieved documents
        doc_chunks = [
            DocumentChunk(
                id=doc["id"],
                text=doc["text"],
                score=doc["score"],
                metadata=doc["metadata"],
                source=doc["source"]
            )
            for doc in retrieved_docs
        ]
        
        # Use the model that was actually used
        model_used = rag_chat_service.last_model_used or settings.chat_model
        
        return ChatResponse(
            response=response_text,
            retrieved_documents=doc_chunks,
            model=model_used
        )
    
    except Exception as e:
        print(f"Error in multi-turn chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """
    Get list of available subagents.
    
    Returns metadata about each registered subagent that can be used
    with the use_agent parameter in /query endpoint.
    """
    try:
        registry = get_subagent_registry()
        agents = registry.list_all()
        return {
            "agents": agents,
            "total": len(agents),
            "message": "Use the 'use_agent' parameter in /query to invoke a specific agent"
        }
    except Exception as e:
        print(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
