from typing import List, Any, Optional
from app.config import settings


def get_embeddings():
    """Return the appropriate embeddings model based on AI_PROVIDER setting."""
    if settings.AI_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small",
        )
    else:
        return GeminiEmbeddings(api_key=settings.GOOGLE_API_KEY)


def get_llm():
    """Return the appropriate LLM based on AI_PROVIDER setting."""
    if settings.AI_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.2,
        )
    else:
        return GeminiLLM(api_key=settings.GOOGLE_API_KEY)


class GeminiEmbeddings:
    """
    LangChain-compatible embeddings wrapper using the Gemini REST API directly.
    Avoids all langchain-google-genai version conflicts.
    """

    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self.api_key = api_key
        self.model = model

    def _embed(self, texts: List[str]) -> List[List[float]]:
        import requests

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:batchEmbedContents"
        params = {"key": self.api_key}

        all_vectors = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            body = {
                "requests": [
                    {
                        "model": f"models/{self.model}",
                        "content": {"parts": [{"text": t}]},
                    }
                    for t in batch
                ]
            }
            resp = requests.post(url, json=body, params=params, timeout=60)
            resp.raise_for_status()
            for item in resp.json()["embeddings"]:
                all_vectors.append(item["values"])

        return all_vectors

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]


class _GeminiResponse:
    """Minimal response object matching LangChain's AIMessage interface."""
    def __init__(self, content: str):
        self.content = content


class GeminiLLM:
    """
    LangChain-compatible chat LLM wrapper using the Gemini REST API directly.
    Avoids the deprecated google-generativeai gRPC path.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", temperature: float = 0.2):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    def _call(self, messages) -> str:
        import requests

        # Convert LangChain messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg.type in ("human", "user") else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        params = {"key": self.api_key}
        body = {
            "contents": contents,
            "generationConfig": {"temperature": self.temperature},
        }
        resp = requests.post(url, json=body, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def invoke(self, messages) -> _GeminiResponse:
        return _GeminiResponse(self._call(messages))

    async def ainvoke(self, messages) -> _GeminiResponse:
        import asyncio
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self._call, messages)
        return _GeminiResponse(text)
