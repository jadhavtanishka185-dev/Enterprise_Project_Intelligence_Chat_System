import chromadb
from langchain_chroma import Chroma
from langchain.schema import Document
from typing import List, Tuple
from app.config import settings
from app.rag.embeddings import get_embeddings


def get_collection_name(project_id: int) -> str:
    """Each project gets its own isolated ChromaDB collection."""
    return f"collection_project_{project_id}"


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)


def get_vector_store(project_id: int) -> Chroma:
    """Get or create a Chroma vector store for a specific project."""
    collection_name = get_collection_name(project_id)
    embeddings = get_embeddings()
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )


def add_documents_to_store(project_id: int, documents: List[Document]) -> int:
    """Add documents to the project's isolated vector store. Returns chunk count."""
    vector_store = get_vector_store(project_id)
    vector_store.add_documents(documents)
    return len(documents)


def similarity_search(
    project_id: int,
    query: str,
    k: int = 5,
) -> List[Tuple[Document, float]]:
    """
    Search ONLY within the specified project's collection.
    This enforces project isolation at the vector store level.
    """
    vector_store = get_vector_store(project_id)
    results = vector_store.similarity_search_with_relevance_scores(query, k=k)
    return results


def delete_project_collection(project_id: int) -> None:
    """Delete all vectors for a project when the project is deleted."""
    try:
        client = get_chroma_client()
        collection_name = get_collection_name(project_id)
        client.delete_collection(collection_name)
    except Exception:
        pass  # Collection may not exist yet
