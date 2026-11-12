"""Twilio SMS webhook adapter.

This is a stub you can point a Twilio number at. It parses the standard
`Body` / `From` form post and returns TwiML. Signature validation is
optional and only runs when TWILIO_VALIDATE_SIGNATURE=1 and
TWILIO_AUTH_TOKEN is set — the token is never hardcoded.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Mapping
from urllib.parse import parse_qs

from mate.agent import MateAgent
from mate.config import Config


def parse_form(body: bytes, charset: str = "utf-8") -> dict[str, str]:
    parsed = parse_qs(body.decode(charset, errors="replace"), keep_blank_values=True)
    return {key: values[0] if values else "" for key, values in parsed.items()}


def twiml_message(text: str) -> str:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<Response><Message>"
        f"{escaped}"
        "</Message></Response>\n"
    )


def validate_signature(
    token: str,
    url: str,
    params: Mapping[str, str],
    signature: str,
) -> bool:
    """Twilio signed-request check. See Twilio's request-validation docs."""
    if not token or not signature:
        return False
    pieces = [url]
    for key in sorted(params):
        pieces.append(key)
        pieces.append(params[key])
    digest = hmac.new(token.encode("utf-8"), "".join(pieces).encode("utf-8"), hashlib.sha1)
    expected = base64.b64encode(digest.digest()).decode("ascii")
    return hmac.compare_digest(expected, signature)


class TwilioAdapter:
    def __init__(self, agent: MateAgent, config: Config) -> None:
        self.agent = agent
        self.config = config

    def handle_webhook(
        self,
        body: bytes,
        *,
        url: str = "",
        signature: str | None = None,
        content_type: str = "application/x-www-form-urlencoded",
    ) -> tuple[int, str, str]:
        """Return (status, content_type, body)."""
        params = parse_form(body)
        if self.config.twilio_validate_signature:
            token = self.config.twilio_auth_token or ""
            if not validate_signature(token, url, params, signature or ""):
                return 403, "text/plain; charset=utf-8", "invalid signature\n"
        text = (params.get("Body") or "").strip()
        sender = (params.get("From") or "sms").strip() or "sms"
        if not text:
            reply = "I didn't get a message body. Text me cashback, a code, a tracking number, or a link."
        else:
            reply = self.agent.handle(text, user_id=f"sms:{sender}").text
        return 200, "application/xml; charset=utf-8", twiml_message(reply)
