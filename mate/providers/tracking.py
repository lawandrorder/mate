"""Demo package-tracking stub. No live carrier lookups."""

from __future__ import annotations

from mate.providers.base import Shipment
from mate.store import JsonStore

# Stable demo statuses so tests and the web chat stay predictable.
DEMO_STATUSES = (
    ("shipped", "Your demo package has shipped. I'll text again when it's out for delivery."),
    ("out_for_delivery", "Out for delivery (demo). A live Mate thread would also offer to tell your room-mate."),
    ("delivered", "Delivered (demo). Left at the front door in this stub story."),
)


class DemoTrackingProvider:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def track(self, number: str | None, store: str | None, user_id: str) -> Shipment:
        key = f"shipment:{user_id}"
        existing = self.store.get(key) or {}
        tracking = number or existing.get("tracking_number") or "DEMO-000000"
        shop = store or existing.get("store")
        # Advance one step each time the same user asks, starting at shipped.
        step = int(existing.get("step", -1)) + 1
        if step >= len(DEMO_STATUSES):
            step = len(DEMO_STATUSES) - 1
        status, detail = DEMO_STATUSES[step]
        if shop and "order" not in detail.lower() and step == 0:
            detail = f"{shop}: {detail}"
        shipment = {
            "tracking_number": tracking,
            "store": shop,
            "status": status,
            "detail": detail,
            "step": step,
            "shared_with": list(existing.get("shared_with") or []),
            "demo": True,
        }
        self.store.set(key, shipment)
        return self._as_shipment(shipment)

    def share(self, user_id: str, contact: str = "room-mate") -> Shipment | None:
        key = f"shipment:{user_id}"
        existing = self.store.get(key)
        if not existing:
            return None
        shared = list(existing.get("shared_with") or [])
        if contact not in shared:
            shared.append(contact)
        existing["shared_with"] = shared
        existing["detail"] = (
            f"{existing.get('detail', '')} Shared demo alerts with your {contact}."
        ).strip()
        self.store.set(key, existing)
        return self._as_shipment(existing)

    def _as_shipment(self, data: dict) -> Shipment:
        return Shipment(
            tracking_number=data.get("tracking_number"),
            store=data.get("store"),
            status=data.get("status", "unknown"),
            detail=data.get("detail", ""),
            demo=True,
            shared_with=list(data.get("shared_with") or []),
        )
