"""Qdrant vector database client."""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Optional
import uuid

from config import settings


class QdrantVectorDB:
    """Qdrant vector database interface for RAG."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            api_key=settings.qdrant_api_key,
            url=settings.qdrant_url
        )
        self.collection_name = settings.qdrant_collection_name
        self.embedding_dim = 1536  # text-embedding-3-small dimension
    
    async def initialize_collection(self) -> bool:
        """Initialize Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            try:
                self.client.get_collection(self.collection_name)
                print(f"Collection '{self.collection_name}' already exists")
                return True
            except Exception:
                # Collection doesn't exist, create it
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    ),
                )
                print(f"Created collection '{self.collection_name}'")
                return True
        except Exception as e:
            print(f"Error initializing collection: {e}")
            return False
    
    async def add_document(
        self,
        text: str,
        embedding: List[float],
        metadata: Optional[dict] = None
    ) -> str:
        """Add a document to the vector database."""
        try:
            doc_id = str(uuid.uuid4())
            point = PointStruct(
                id=hash(doc_id) & 0x7FFFFFFF,  # Positive integer ID
                vector=embedding,
                payload={
                    "text": text,
                    "metadata": metadata or {},
                    "source": metadata.get("source", "unknown") if metadata else "unknown"
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return doc_id
        except Exception as e:
            print(f"Error adding document: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[dict]:
        """Search for similar documents."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=0.5
            )
            
            documents = []
            for result in results:
                documents.append({
                    "id": str(result.id),
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": result.payload.get("metadata", {}),
                    "source": result.payload.get("source", "unknown")
                })
            return documents
        except Exception as e:
            print(f"Error searching documents: {e}")
            raise
    
    async def delete_collection(self) -> bool:
        """Delete the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False


# Global instance
try:
    vector_db = QdrantVectorDB()
except Exception as e:
    print(f"Warning: Could not initialize Qdrant client: {e}")
    # Create a mock/dummy instance that won't crash the app
    class DummyVectorDB:
        def __init__(self):
            self.client = None
            self.collection_name = "dummy"
            self.embedding_dim = 1536
        async def search(self, *args, **kwargs):
            return []
        async def add_document(self, *args, **kwargs):
            return None
    vector_db = DummyVectorDB()

