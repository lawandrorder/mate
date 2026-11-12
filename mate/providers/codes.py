"""Demo discount-code provider. Codes are placeholders, not live offers."""

from __future__ import annotations

import re

from mate.providers.base import DEMO_DISCLAIMER, Offer


def demo_code(store: str | None, user_id: str = "you") -> str:
    store_part = re.sub(r"[^A-Za-z0-9]+", "", (store or "STORE")).upper()[:16] or "STORE"
    name_part = re.sub(r"[^A-Za-z0-9]+", "", user_id).upper()[:10] or "YOU"
    return f"DEMO-{name_part}-{store_part}"


class DemoCodesProvider:
    def code_for(self, store: str | None, user_id: str) -> Offer:
        name = store or "that store"
        code = demo_code(name, user_id)
        summary = (
            f"If this starter were hooked up to Mate's live network, I'd generate "
            f"a discount code for {name} made for you. Here's the placeholder "
            f"shape a demo reply uses — it will not work at checkout."
        )
        return Offer(
            store=name,
            summary=summary,
            code=code,
            extras={"disclaimer": DEMO_DISCLAIMER, "kind": "code"},
        )
