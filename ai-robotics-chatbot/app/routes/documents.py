"""Document management routes."""

from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
from app.models import UploadDocumentRequest
from app.vector_db import vector_db
from app.llm_service import embedding_service

router = APIRouter()


@router.post("/upload")
async def upload_document(request: UploadDocumentRequest):
    """
    Upload a document to the vector database.
    
    The document is split into chunks, embedded, and stored in Qdrant.
    """
    try:
        # Initialize collection if needed
        await vector_db.initialize_collection()
        
        # Split content into chunks (simple approach)
        # In production, use more sophisticated chunking
        chunk_size = 500
        chunks = [
            request.content[i:i + chunk_size]
            for i in range(0, len(request.content), chunk_size)
        ]
        
        document_ids = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 0:
                # Generate embedding
                embedding = await embedding_service.embed_text(chunk)
                
                # Add to vector database
                doc_id = await vector_db.add_document(
                    text=chunk,
                    embedding=embedding,
                    metadata={
                        "title": request.title,
                        "chunk_index": i,
                        "source": request.source or request.title
                    }
                )
                document_ids.append(doc_id)
        
        return {
            "status": "success",
            "message": f"Document '{request.title}' uploaded successfully",
            "chunks_processed": len(document_ids),
            "document_ids": document_ids
        }
    
    except Exception as e:
        print(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a text file (markdown or txt) to the vector database.
    """
    try:
        # Initialize collection if needed
        await vector_db.initialize_collection()
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Split into chunks
        chunk_size = 500
        chunks = [
            content_str[i:i + chunk_size]
            for i in range(0, len(content_str), chunk_size)
        ]
        
        document_ids = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 0:
                # Generate embedding
                embedding = await embedding_service.embed_text(chunk)
                
                # Add to vector database
                doc_id = await vector_db.add_document(
                    text=chunk,
                    embedding=embedding,
                    metadata={
                        "title": file.filename,
                        "chunk_index": i,
                        "source": file.filename
                    }
                )
                document_ids.append(doc_id)
        
        return {
            "status": "success",
            "message": f"File '{file.filename}' uploaded successfully",
            "chunks_processed": len(document_ids),
            "document_ids": document_ids
        }
    
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def document_status():
    """Get status of the document collection."""
    try:
        collection_info = vector_db.client.get_collection(vector_db.collection_name)
        
        return {
            "status": "success",
            "collection_name": vector_db.collection_name,
            "point_count": collection_info.points_count,
            "vector_size": collection_info.config.params.vectors.size if hasattr(collection_info.config.params, 'vectors') else "unknown"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete("/clear")
async def clear_collection():
    """
    Clear all documents from the collection.
    
    WARNING: This is destructive and cannot be undone.
    """
    try:
        success = await vector_db.delete_collection()
        
        if success:
            # Reinitialize empty collection
            await vector_db.initialize_collection()
            return {
                "status": "success",
                "message": "Collection cleared and reinitialized"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear collection")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
