"""Shared LLM client using OpenRouter (OpenAI-compatible) → Claude claude-sonnet-4-6."""

from __future__ import annotations
import os
from pathlib import Path
from openai import OpenAI

_ENV_FILE = Path(__file__).parent.parent / ".env"

def _load_env() -> None:
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

MODEL = "anthropic/claude-sonnet-4-6"

def get_client() -> OpenAI:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not found. "
            "Set it in the environment or in /home/user/File-System/Bots/.env"
        )
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)


def chat(
    client: OpenAI,
    system: str,
    user: str | list,
    max_tokens: int = 4096,
) -> str:
    """Send a chat request; user may be a string or a list of content parts (for vision)."""
    user_content = user if isinstance(user, list) else [{"type": "text", "text": user}]
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
    )
    return response.choices[0].message.content or ""
