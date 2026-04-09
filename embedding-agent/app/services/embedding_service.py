import logging
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from app.config import settings

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None
_qdrant_client: QdrantClient | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"[Embedding] Loading model: {settings.BGE_M3_MODEL_NAME} ({settings.BGE_M3_DEVICE})")
        _model = SentenceTransformer(settings.BGE_M3_MODEL_NAME, device=settings.BGE_M3_DEVICE)
    return _model


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _qdrant_client


def get_embedding_size() -> int:
    size = get_model().get_sentence_embedding_dimension()
    if size is None:
        raise RuntimeError("임베딩 벡터 차원 수를 확인할 수 없습니다.")
    return int(size)


def ensure_collection(collection_name: str):
    client = get_qdrant_client()
    collections = {c.name for c in client.get_collections().collections}
    if collection_name in collections:
        return

    vector_size = get_embedding_size()
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    logger.info(f"[Qdrant] Collection created: {collection_name} (dim={vector_size})")


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=settings.BGE_BATCH_SIZE,
    )
    return vectors.tolist()


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
                payload={
                    "text": text,
                    "metadata": meta,
                },
            )
        )

    client = get_qdrant_client()
    client.upsert(collection_name=target_collection, points=points, wait=True)

    return {
        "collection": target_collection,
        "uploaded": len(points),
        "vector_size": len(vectors[0]) if vectors else 0,
        "model": settings.BGE_M3_MODEL_NAME,
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

    results = []
    for hit in hits:
        payload = hit.payload or {}
        results.append(
            {
                "id": str(hit.id),
                "score": float(hit.score),
                "text": payload.get("text", ""),
                "metadata": payload.get("metadata", {}),
            }
        )

    return {
        "collection": target_collection,
        "query": query,
        "hits": results,
    }


def warm_up():
    ensure_collection(settings.QDRANT_COLLECTION)
