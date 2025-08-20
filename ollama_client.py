import os
import json
import httpx
from typing import AsyncGenerator, Dict, Any, List

_OLLAMA_HOST = os.environ.get("OLLAMA_HOST")
_OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")
OLLAMA_BASE_URL = (_OLLAMA_HOST or _OLLAMA_BASE_URL or "http://127.0.0.1:11434").rstrip("/")
MODEL_FAST = os.environ.get("OLLAMA_MODEL_FAST", "gpt-oss:20b")
MODEL_STRONG = os.environ.get("OLLAMA_MODEL_STRONG", "gpt-oss:120b")


async def stream_generate(prompt: str, use_strong: bool = False, system: str | None = None) -> AsyncGenerator[str, None]:
    model = MODEL_STRONG if use_strong else MODEL_FAST
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": True,
    }
    if system:
        payload["system"] = system

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, read=120.0)) as client:
        async with client.stream("POST", url, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                # Each line is a JSON object with {response: str, done: bool}
                try:
                    data = json.loads(line)
                except Exception:
                    continue
                chunk = data.get("response")
                if chunk:
                    yield chunk
                if data.get("done"):
                    break


async def complete(prompt: str, use_strong: bool = False, system: str | None = None) -> str:
    chunks: List[str] = []
    async for c in stream_generate(prompt, use_strong=use_strong, system=system):
        chunks.append(c)
    return "".join(chunks)
