from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from app.rag.vector_store import similarity_search
from app.rag.embeddings import get_llm

RAG_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful AI assistant for an enterprise knowledge base.
Answer the user's question based ONLY on the provided context documents.
If the answer is not found in the context, say "I couldn't find relevant information in the project documents."
Do NOT use any external knowledge beyond what is provided.

Context:
{context}

Question: {question}

Answer:
""")


async def run_rag_query(project_id: int, question: str) -> Dict[str, Any]:
    """
    Run the full RAG pipeline for a specific project.
    ISOLATION: Only retrieves from collection_project_{project_id}.
    """
    # Step 1: Retrieve relevant chunks from THIS project only
    results = similarity_search(project_id=project_id, query=question, k=5)

    if not results:
        return {
            "answer": "I couldn't find any relevant documents in this project. Please upload documents first.",
            "sources": [],
        }

    # Step 2: Build context from retrieved chunks
    context_parts = []
    sources = []
    seen_sources = set()

    for doc, score in results:
        if score < 0.1:  # Filter very low relevance results
            continue
        context_parts.append(doc.page_content)
        source_name = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page")
        source_key = f"{source_name}_{page}"
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({
                "document": source_name,
                "page": page,
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "relevance_score": round(score, 3),
            })

    if not context_parts:
        return {
            "answer": "The retrieved documents don't seem relevant enough to answer your question. Try rephrasing.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(context_parts)

    # Step 3: Generate answer using LLM
    llm = get_llm()
    prompt = RAG_PROMPT.format_messages(context=context, question=question)
    response = await llm.ainvoke(prompt)

    return {
        "answer": response.content,
        "sources": sources,
    }
