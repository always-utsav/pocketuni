import logging
import time
from typing import List, Optional, AsyncIterator, Dict, Any
from backend.app.core.config import settings

logger = logging.getLogger("pocketuni.gemini")

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.chat_model = settings.GEMINI_CHAT_MODEL
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_output_tokens = settings.GEMINI_MAX_OUTPUT_TOKENS
        self.timeout = settings.GEMINI_TIMEOUT
        self.max_retries = settings.GEMINI_MAX_RETRIES
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not configured in environment.")
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def get_service_status(self) -> Dict[str, Any]:
        """Returns safe operational status without exposing secrets."""
        return {
            "configured": self.is_configured(),
            "chat_model": self.chat_model,
            "embedding_model": self.embedding_model,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens
        }

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ) -> str:
        """Generates content with retries and structured error classification."""
        client = self._get_client()
        temp = temperature if temperature is not None else self.temperature
        tokens = max_output_tokens if max_output_tokens is not None else self.max_output_tokens

        config = {
            "temperature": temp,
            "max_output_tokens": tokens,
        }
        if system_instruction:
            config["system_instruction"] = system_instruction

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=self.chat_model,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text
                return ""
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                logger.warning(f"Gemini generation attempt {attempt} failed: {type(e).__name__}")
                if "rate limit" in err_str or "resource_exhausted" in err_str or "429" in err_str:
                    time.sleep(2 * attempt)
                elif "invalid" in err_str and "key" in err_str:
                    logger.error("Invalid Gemini API key configured.")
                    raise RuntimeError("Gemini API key is invalid or expired.")
                else:
                    time.sleep(1)

        logger.error(f"Gemini generation failed after {self.max_retries} attempts: {last_error}")
        raise RuntimeError(f"Gemini generation service unavailable: {str(last_error)}")

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> AsyncIterator[str]:
        """Streams content tokens asynchronously."""
        client = self._get_client()
        temp = temperature if temperature is not None else self.temperature

        config = {
            "temperature": temp,
            "max_output_tokens": self.max_output_tokens,
        }
        if system_instruction:
            config["system_instruction"] = system_instruction

        try:
            response_stream = client.models.generate_content_stream(
                model=self.chat_model,
                contents=prompt,
                config=config
            )
            for chunk in response_stream:
                if chunk and chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming error: {str(e)}")
            yield f"\n[Generation error: {type(e).__name__}]"

    def embed_text(self, text: str) -> List[float]:
        """Generates embedding for a single text chunk with resilient rate-limit backoff."""
        client = self._get_client()
        for attempt in range(1, 5):
            try:
                res = client.models.embed_content(
                    model=self.embedding_model,
                    contents=text
                )
                if res and res.embeddings:
                    return res.embeddings[0].values
                raise ValueError("No embeddings returned by Gemini.")
            except Exception as e:
                err_str = str(e).lower()
                if "rate limit" in err_str or "429" in err_str or "resource_exhausted" in err_str:
                    sleep_time = 15 * attempt
                    logger.warning(f"Rate limited by Gemini (429). Backing off for {sleep_time}s on attempt {attempt}/4...")
                    time.sleep(sleep_time)
                else:
                    time.sleep(2)
                if attempt == 4:
                    logger.error(f"Gemini embed_text exhausted retries: {str(e)}")
                    raise

        return []

    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """Generates embeddings for multiple texts in safe batches."""
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for t in batch:
                # Individual embed call per text for robust error isolation
                emb = self.embed_text(t)
                results.append(emb)
            time.sleep(0.1)  # brief pause to avoid hitting rate limits
        return results


gemini_service = GeminiService()
