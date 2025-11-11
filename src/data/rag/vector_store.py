from typing import Optional

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.config.settings import settings


class VectorStoreInitializer:
    def __init__(self):
        self.client = None
        self.vector_store = None
        self.embeddings = None

    def initialize(self) -> QdrantVectorStore:
        """Initialize Qdrant vector store with configuration"""
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)

        # Initialize Qdrant client
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )

        # Get vector size
        vector_size = len(self.embeddings.embed_query("sample text"))

        # Create collection if not exists
        if not self.client.collection_exists(settings.QDRANT_COLLECTION_NAME):
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

        # Initialize vector store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            embedding=self.embeddings,
        )

        return self.vector_store

    def get_vector_store(self) -> Optional[QdrantVectorStore]:
        """Get initialized vector store"""
        if self.vector_store is None:
            return self.initialize()
        return self.vector_store

    def get_embeddings(self) -> OpenAIEmbeddings:
        """Get embeddings instance"""
        if self.embeddings is None:
            self.initialize()
        return self.embeddings


# Global instance
vector_store_initializer = VectorStoreInitializer()


def get_vector_store() -> QdrantVectorStore:
    """Get vector store instance (singleton)"""
    return vector_store_initializer.get_vector_store()


def get_embeddings() -> OpenAIEmbeddings:
    """Get embeddings instance (singleton)"""
    return vector_store_initializer.get_embeddings()
