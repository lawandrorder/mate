"""Demo cashback provider. Clearly labeled — no live rates, no real payouts."""

from __future__ import annotations

from mate.providers.base import DEMO_DISCLAIMER, Offer
from mate.store import JsonStore


def _slug(store: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in store)
    return "-".join(part for part in cleaned.split("-") if part) or "store"


class DemoCashbackProvider:
    """In-memory / JSON demo of 'text first, get a tracked link, cashback lands'."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def offer(self, store: str | None, user_id: str) -> Offer:
        name = store or "that store"
        slug = _slug(name)
        link = f"https://demo.mate.local/r/{slug}?uid={_slug(user_id)}"
        summary = (
            f"If this starter were hooked up to Mate's live network, I'd send you "
            f"a tracked checkout link for {name} and any cashback would land in "
            f"your balance after the order."
        )
        return Offer(
            store=name,
            summary=summary,
            link=link,
            extras={"disclaimer": DEMO_DISCLAIMER, "kind": "cashback"},
        )

    def credit_demo(self, user_id: str, amount: float, note: str) -> float:
        def mutator(current):
            wallet = dict(current or {"balance": 0.0, "ledger": []})
            wallet["balance"] = round(float(wallet.get("balance", 0)) + amount, 2)
            ledger = list(wallet.get("ledger") or [])
            ledger.append({"amount": amount, "note": note, "demo": True})
            wallet["ledger"] = ledger[-50:]
            return wallet

        wallet = self.store.update(f"wallet:{user_id}", mutator)
        return float(wallet["balance"])

    def balance(self, user_id: str) -> float:
        wallet = self.store.get(f"wallet:{user_id}") or {}
        return float(wallet.get("balance", 0.0))
