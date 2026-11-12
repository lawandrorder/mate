"""Demo price watcher. Does not crawl live product pages unless you replace it."""

from __future__ import annotations

import hashlib
from urllib.parse import urlparse

from mate.providers.base import PriceWatch
from mate.store import JsonStore


def _demo_price(url: str) -> float:
    """Stable fictional price derived from the URL, not a live scrape."""
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    cents = int(digest[:4], 16) % 15000 + 2000  # $20.00 – $169.99
    return round(cents / 100.0, 2)


def _title(url: str) -> str:
    host = urlparse(url).netloc or "item"
    path = urlparse(url).path.rstrip("/") or "/"
    slug = path.rsplit("/", 1)[-1] or host
    label = slug.replace("-", " ").replace("_", " ")
    return f"Demo listing: {label} ({host})"


class DemoPriceProvider:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def watch(self, url: str, user_id: str) -> PriceWatch:
        price = _demo_price(url)
        record = {
            "url": url,
            "user_id": user_id,
            "title": _title(url),
            "currency": "USD",
            "last_price": price,
            "previous_price": None,
            "dropped": False,
            "demo": True,
        }

        def mutator(current):
            items = list(current or [])
            for item in items:
                if item.get("url") == url and item.get("user_id") == user_id:
                    item.update({k: v for k, v in record.items() if k != "last_price"})
                    # Keep the already stored price so later ticks can drop it.
                    if "last_price" not in item:
                        item["last_price"] = price
                    return items
            items.append(record)
            return items

        items = self.store.update("watches", mutator)
        saved = next(i for i in items if i["url"] == url and i["user_id"] == user_id)
        return self._as_watch(saved)

    def list_watches(self, user_id: str | None = None) -> list[PriceWatch]:
        items = list(self.store.get("watches") or [])
        if user_id is not None:
            items = [i for i in items if i.get("user_id") == user_id]
        return [self._as_watch(i) for i in items]

    def tick(self, simulate_drop: bool = False) -> list[PriceWatch]:
        """Advance demo prices. With simulate_drop, every watch falls 15% once."""

        dropped: list[PriceWatch] = []

        def mutator(current):
            items = list(current or [])
            for item in items:
                last = float(item.get("last_price") or _demo_price(item["url"]))
                if simulate_drop and not item.get("dropped"):
                    new_price = round(last * 0.85, 2)
                    item["previous_price"] = last
                    item["last_price"] = new_price
                    item["dropped"] = True
                    dropped.append(self._as_watch(item))
                else:
                    item.setdefault("last_price", last)
            return items

        self.store.update("watches", mutator)
        return dropped

    def _as_watch(self, item: dict) -> PriceWatch:
        return PriceWatch(
            url=item["url"],
            title=item.get("title") or _title(item["url"]),
            currency=item.get("currency") or "USD",
            last_price=float(item["last_price"]),
            previous_price=(
                float(item["previous_price"]) if item.get("previous_price") is not None else None
            ),
            dropped=bool(item.get("dropped")),
            demo=True,
        )
