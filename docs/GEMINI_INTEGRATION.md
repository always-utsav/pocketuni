# PocketUni — Google Gemini Integration Specification

## 1. SDK & Client Details
- **SDK:** Official Google GenAI SDK (`google-genai` v2.34.0, `from google import genai`)
- **API Version:** v1beta via official SDK endpoints
- **Authentication:** `Client(api_key=settings.GEMINI_API_KEY)` initialized server-side.

## 2. Configured Models & Settings
The models are configurable via environment variables in `backend/.env` with production defaults:

| Setting | Default Value | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | *(Configured in `.env`)* | Secret API authorization key |
| `GEMINI_CHAT_MODEL` | `gemini-2.5-flash` | Primary low-latency grounded reasoning & chat synthesis |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | Semantic text embedding (3072 dimensions) |
| `GEMINI_TEMPERATURE` | `0.2` | Low temperature to enforce strict grounding |
| `GEMINI_MAX_OUTPUT_TOKENS` | `2048` | Maximum output response length |
| `GEMINI_TIMEOUT` | `30` | Request timeout in seconds |
| `GEMINI_MAX_RETRIES` | `3` | Exponential backoff attempts on rate limits |

## 3. Secret Protection & Diagnostics
- The API key is loaded into FastAPI settings server-side and never exposed to the frontend, never returned in API payloads, and never logged.
- The diagnostics endpoint (`GET /api/v1/admin/ai-status`) exposes only operational indicators:
  ```json
  {
    "configured": true,
    "chat_model": "gemini-2.5-flash",
    "embedding_model": "gemini-embedding-001",
    "temperature": 0.2,
    "max_output_tokens": 2048
  }
  ```
