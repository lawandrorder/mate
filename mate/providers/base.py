"""Provider contracts. Swap the demo implementations for live Mate network calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


DEMO_DISCLAIMER = (
    "This is a demo provider in the open-source starter. "
    "It is not connected to Mate's live merchant network, and it does not "
    "pay real cashback or issue real discount codes."
)


@dataclass
class Offer:
    store: str
    summary: str
    link: str | None = None
    code: str | None = None
    demo: bool = True
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class Shipment:
    tracking_number: str | None
    store: str | None
    status: str
    detail: str
    demo: bool = True
    shared_with: list[str] = field(default_factory=list)


@dataclass
class PriceWatch:
    url: str
    title: str
    currency: str
    last_price: float
    previous_price: float | None = None
    dropped: bool = False
    demo: bool = True


class CashbackProvider(Protocol):
    def offer(self, store: str | None, user_id: str) -> Offer: ...
    def credit_demo(self, user_id: str, amount: float, note: str) -> float: ...
    def balance(self, user_id: str) -> float: ...


class CodesProvider(Protocol):
    def code_for(self, store: str | None, user_id: str) -> Offer: ...


class TrackingProvider(Protocol):
    def track(self, number: str | None, store: str | None, user_id: str) -> Shipment: ...
    def share(self, user_id: str, contact: str = "room-mate") -> Shipment | None: ...


class PriceProvider(Protocol):
    def watch(self, url: str, user_id: str) -> PriceWatch: ...
    def list_watches(self, user_id: str | None = None) -> list[PriceWatch]: ...
    def tick(self, simulate_drop: bool = False) -> list[PriceWatch]: ...
