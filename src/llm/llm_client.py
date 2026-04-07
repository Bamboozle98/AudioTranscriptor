import os
import json
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class LLMConfig:
    client: OpenAI
    model: str


def llm_summon() -> LLMConfig:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL", "gpt-4.1-mini")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)
    return LLMConfig(client=client, model=model)


def llm_chat_json(
    cfg: LLMConfig,
    system: str,
    user: str,
    temperature: float = 0.0,
):
    response = cfg.client.responses.create(
        model=cfg.model,
        temperature=temperature,
        input=[
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": user.strip()},
        ],
    )

    content = getattr(response, "output_text", "") or ""
    if not content:
        raise ValueError("Model returned empty content.")

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON.\nRaw:\n{content}") from e