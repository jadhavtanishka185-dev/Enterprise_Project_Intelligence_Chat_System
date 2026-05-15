from typing import List
import time
import logging
import asyncio

from app.config import settings

logger = logging.getLogger(__name__)


# =========================================================
# EMBEDDINGS
# =========================================================

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


# =========================================================
# LLM
# =========================================================

def get_llm():
    """Return appropriate LLM based on provider setting."""
    if settings.AI_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.2,
        )
    else:
        return GeminiLLM(api_key=settings.GOOGLE_API_KEY)


# =========================================================
# GEMINI EMBEDDINGS
# =========================================================

class GeminiEmbeddings:
    """
    LangChain-compatible embeddings wrapper using the Gemini REST API directly.
    Includes exponential backoff retry logic for rate limits.
    """

    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self.api_key = api_key
        self.model = model
        self.url = (
            f"https://generativelanguage.googleapis.com"
            f"/v1beta/models/{self.model}:batchEmbedContents"
        )

    def _embed_batch(self, texts: List[str], attempt: int = 0) -> List[List[float]]:
        """Embed a single batch with exponential backoff on rate limits."""
        import requests

        body = {
            "requests": [
                {
                    "model": f"models/{self.model}",
                    "content": {"parts": [{"text": t}]},
                }
                for t in texts
            ]
        }

        try:
            resp = requests.post(
                self.url,
                json=body,
                params={"key": self.api_key},
                timeout=60,
            )

            if resp.status_code == 429:
                if attempt >= 4:
                    raise Exception(
                        "Gemini API rate limit exceeded after 4 retries. "
                        "Please wait a minute and try uploading again."
                    )
                wait_time = 10 * (2 ** attempt)
                logger.warning(
                    f"Rate limit hit. Waiting {wait_time}s "
                    f"before retry {attempt + 1}/4..."
                )
                time.sleep(wait_time)
                return self._embed_batch(texts, attempt + 1)

            resp.raise_for_status()
            return [item["values"] for item in resp.json()["embeddings"]]

        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                raise
            logger.error(f"Gemini embedding error: {e}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Embed all texts in small batches to avoid rate limits."""
        all_vectors = []
        batch_size = 5

        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            vectors = self._embed_batch(batch)
            all_vectors.extend(vectors)

            # Small delay between batches to avoid rate limits
            if i + batch_size < len(texts):
                time.sleep(0.5)

        return all_vectors

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]


# =========================================================
# GEMINI LLM
# =========================================================

class _GeminiResponse:
    """Minimal response object matching LangChain's AIMessage interface."""
    def __init__(self, content: str):
        self.content = content


class GeminiLLM:
    """
    LangChain-compatible chat LLM wrapper using the Gemini REST API directly.
    Includes exponential backoff retry logic for rate limits.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.2,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    def _call(self, messages, attempt: int = 0) -> str:
        import requests

        contents = []
        for msg in messages:
            role = "user" if msg.type in ("human", "user") else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})

        url = (
            f"https://generativelanguage.googleapis.com"
            f"/v1beta/models/{self.model}:generateContent"
        )
        body = {
            "contents": contents,
            "generationConfig": {"temperature": self.temperature},
        }

        try:
            resp = requests.post(
                url,
                json=body,
                params={"key": self.api_key},
                timeout=60,
            )

            if resp.status_code == 429:
                if attempt >= 4:
                    raise Exception(
                        "Gemini API rate limit exceeded after 4 retries. "
                        "Please try again later."
                    )
                wait_time = 10 * (2 ** attempt)
                logger.warning(
                    f"Rate limit hit. Waiting {wait_time}s "
                    f"before retry {attempt + 1}/4..."
                )
                time.sleep(wait_time)
                return self._call(messages, attempt + 1)

            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            logger.error(f"Gemini LLM error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")

    def invoke(self, messages) -> _GeminiResponse:
        return _GeminiResponse(self._call(messages))

    async def ainvoke(self, messages) -> _GeminiResponse:
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self._call, messages)
        return _GeminiResponse(text)
