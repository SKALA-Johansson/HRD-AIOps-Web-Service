import logging
import uuid
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from app.config import settings

logger = logging.getLogger(__name__)

_openai_client: OpenAI | None = None
_qdrant_client: QdrantClient | None = None

EMBEDDING_DIM = 1536  # text-embedding-3-small 기본 차원


def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _qdrant_client


def ensure_collection(collection_name: str):
    client = get_qdrant_client()
    collections = {c.name for c in client.get_collections().collections}
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
        logger.info(f"[Qdrant] Collection created: {collection_name} (dim={EMBEDDING_DIM})")


def embed_texts(texts: list[str]) -> list[list[float]]:
    client = get_openai_client()
    response = client.embeddings.create(
        model=settings.OPENAI_EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def upsert_documents(texts: list[str], metadatas: list[dict] | None = None, collection: str | None = None) -> dict:
    if metadatas and len(metadatas) != len(texts):
        raise ValueError("metadatas 길이는 texts 길이와 같아야 합니다.")

    target_collection = collection or settings.QDRANT_COLLECTION
    ensure_collection(target_collection)

    vectors = embed_texts(texts)
    points: list[PointStruct] = []

    for i, text in enumerate(texts):
        meta = metadatas[i] if metadatas else {}
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vectors[i],
                payload={"text": text, "metadata": meta},
            )
        )

    client = get_qdrant_client()
    client.upsert(collection_name=target_collection, points=points, wait=True)

    return {
        "collection": target_collection,
        "uploaded": len(points),
        "vector_size": EMBEDDING_DIM,
        "model": settings.OPENAI_EMBEDDING_MODEL,
    }


def search_similar(query: str, k: int = 5, collection: str | None = None) -> dict:
    target_collection = collection or settings.QDRANT_COLLECTION
    ensure_collection(target_collection)

    query_vector = embed_texts([query])[0]
    client = get_qdrant_client()
    hits = client.search(
        collection_name=target_collection,
        query_vector=query_vector,
        with_payload=True,
        limit=k,
    )

    results = [
        {
            "id": str(hit.id),
            "score": float(hit.score),
            "text": (hit.payload or {}).get("text", ""),
            "metadata": (hit.payload or {}).get("metadata", {}),
        }
        for hit in hits
    ]

    return {"collection": target_collection, "query": query, "hits": results}


def warm_up():
    ensure_collection(settings.QDRANT_COLLECTION)
