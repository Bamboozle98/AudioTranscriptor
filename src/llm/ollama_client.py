import os
import json
import requests
from dataclasses import dataclass


@dataclass
class OllamaConfig:
    host: str
    model: str
    chat_url: str
    tags_url: str


def ollama_summon() -> OllamaConfig:
    """
    Returns Ollama connection/config info.
    Environment variables:
      OLLAMA_HOST (default http://127.0.0.1:11434)
      OLLAMA_MODEL (default qwen2.5:3b-instruct)
    """
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")

    return OllamaConfig(
        host=host,
        model=model,
        chat_url=f"{host}/api/chat",
        tags_url=f"{host}/api/tags",
    )


def ollama_chat_json(
    cfg: OllamaConfig,
    system: str,
    user: str,
    temperature: float = 0.0,
    timeout: int = 120,
) -> dict:
    """
    Calls Ollama /api/chat and returns parsed JSON from the assistant response.
    Assumes the model is instructed to return *JSON only*.
    """
    payload = {
        "model": cfg.model,
        "stream": False,
        "options": {"temperature": temperature},
        "messages": [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": user.strip()},
        ],
    }

    r = requests.post(cfg.chat_url, json=payload, timeout=timeout)
    r.raise_for_status()

    content = (r.json().get("message", {}) or {}).get("content", "")
    if not content:
        raise ValueError("Ollama returned empty content.")

    # Strict JSON parsing (fail loudly if model outputs anything else)
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON.\nRaw:\n{content}") from e
