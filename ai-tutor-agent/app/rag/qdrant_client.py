"""
Qdrant Vector Store - AI Tutor RAG
커리큘럼 콘텐츠 및 교육 자료를 벡터화하여 튜터링에 활용합니다.
"""
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.config import settings

logger = logging.getLogger(__name__)

_qdrant_client: QdrantClient | None = None
_vector_store: QdrantVectorStore | None = None


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _qdrant_client


def get_vector_store() -> QdrantVectorStore:
    global _vector_store
    if _vector_store is None:
        client = get_qdrant_client()
        embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
        collections = [c.name for c in client.get_collections().collections]
        if settings.QDRANT_COLLECTION not in collections:
            client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            logger.info(f"[Qdrant] 컬렉션 생성: {settings.QDRANT_COLLECTION}")

        _vector_store = QdrantVectorStore(
            client=client,
            collection_name=settings.QDRANT_COLLECTION,
            embedding=embeddings,
        )
    return _vector_store


async def add_documents(texts: list[str], metadatas: list[dict] | None = None):
    store = get_vector_store()
    docs = [
        Document(page_content=text, metadata=metadatas[i] if metadatas else {})
        for i, text in enumerate(texts)
    ]
    store.add_documents(docs)
    logger.info(f"[Qdrant] {len(docs)}건 저장 완료")


async def search_relevant_content(query: str, k: int = 5) -> list[str]:
    store = get_vector_store()
    results = store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]
