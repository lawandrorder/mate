"""Optional OpenRouter fallback for messages the intent parser does not handle.

Requires OPENROUTER_API_KEY in the environment. No key is ever hardcoded.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from mate.config import Config

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are Mate, a text-first shopping assistant.
Stay helpful, brief, and warm — like a text to a friend.

This open-source starter is not connected to Mate's live merchant network.
Do not invent real cashback rates, live discount codes, order statuses, or
user balances and present them as fact. If you sketch an example, label it
clearly as a demo or illustration.

You can explain how Mate works on mate.fm:
- Text Mate before you shop.
- Cashback when you text first: Mate sends a tracked link, cashback lands in the balance.
- Discount codes generated for you.
- Every package tracked, with the option to tell a room-mate.
- Price drop alerts when you send something you're eyeing.

If the shopper is trying to do one of those things, tell them the exact
phrase to text (for example: "cashback at Store", "code for Store",
"track 1Z...", "watch https://...").
"""


class OpenRouterLLM:
    def __init__(self, config: Config) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.openrouter_enabled

    def complete(self, text: str, user_id: str = "web") -> str:
        if not self.enabled:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": 0.4,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.http_referer,
            "X-Title": self.config.app_title,
        }
        request = urllib.request.Request(
            OPENROUTER_URL, data=body, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"OpenRouter HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenRouter request failed: {exc.reason}") from exc
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("OpenRouter returned an unexpected payload") from exc
        return (content or "").strip()
