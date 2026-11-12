"""Mate agent: parse a text, call a provider, return a reply."""

from __future__ import annotations

from dataclasses import dataclass

from mate.config import Config, load_config
from mate.intents import (
    INTENT_BALANCE,
    INTENT_CASHBACK,
    INTENT_CODE,
    INTENT_GREET,
    INTENT_HELP,
    INTENT_SHARE,
    INTENT_TRACK,
    INTENT_UNKNOWN,
    INTENT_WATCH,
    Intent,
    parse_intent,
)
from mate.providers.cashback import DemoCashbackProvider
from mate.providers.codes import DemoCodesProvider
from mate.providers.llm import OpenRouterLLM
from mate.providers.prices import DemoPriceProvider
from mate.providers.tracking import DemoTrackingProvider
from mate.store import JsonStore

HELP_TEXT = """I'm Mate — your mate while you shop.

This is the open-source starter. It understands the same kinds of texts
the live product is built around, and answers with clearly labeled demos.

Try:
• cashback at <store>
• code for <store>
• track <number>   or   where's my <store> order
• watch <url>
• tell my room-mate
• balance

Live Mate on mate.fm texts you a tracked link, a code, a delivery update,
or a price-drop alert. This starter does not pay real cashback or issue
live merchant codes."""

GREET_TEXT = (
    "Hey — I'm Mate. Text me before you shop. "
    "Ask for cashback at a store, a code, a tracking update, or a price watch. "
    "Say help to see the list. Replies in this starter are demos."
)

UNKNOWN_TEXT = (
    "I didn't catch that as cashback, a code, tracking, or a price watch. "
    "Try: cashback at <store>, code for <store>, track <number>, or watch <url>. "
    "Say help for the short list."
)


@dataclass
class Reply:
    text: str
    intent: Intent
    demo: bool = True
    used_llm: bool = False


class MateAgent:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or load_config()
        data = JsonStore(self.config.data_dir / "mate.json")
        self.cashback = DemoCashbackProvider(data)
        self.codes = DemoCodesProvider()
        self.tracking = DemoTrackingProvider(data)
        self.prices = DemoPriceProvider(data)
        self.llm = OpenRouterLLM(self.config)

    def handle(self, text: str, user_id: str = "web") -> Reply:
        intent = parse_intent(text)
        if intent.name == INTENT_HELP:
            return Reply(HELP_TEXT, intent, demo=False)
        if intent.name == INTENT_GREET:
            return Reply(GREET_TEXT, intent, demo=False)
        if intent.name == INTENT_CASHBACK:
            return Reply(self._cashback(intent, user_id), intent)
        if intent.name == INTENT_CODE:
            return Reply(self._code(intent, user_id), intent)
        if intent.name == INTENT_TRACK:
            return Reply(self._track(intent, user_id), intent)
        if intent.name == INTENT_WATCH:
            return Reply(self._watch(intent, user_id), intent)
        if intent.name == INTENT_BALANCE:
            return Reply(self._balance(user_id), intent)
        if intent.name == INTENT_SHARE:
            return Reply(self._share(user_id), intent)
        return self._unknown(intent, text, user_id)

    def _cashback(self, intent: Intent, user_id: str) -> str:
        offer = self.cashback.offer(intent.store, user_id)
        store = offer.store
        return (
            f"[demo] {offer.summary}\n\n"
            f"Tracked demo link for {store}:\n{offer.link}\n\n"
            "In the live product, buying through the link Mate sends is how "
            "cashback lands in your balance. This demo link does not track a "
            "real order or pay cashback."
        )

    def _code(self, intent: Intent, user_id: str) -> str:
        offer = self.codes.code_for(intent.store, user_id)
        return (
            f"[demo] {offer.summary}\n\n"
            f"{offer.code}\n\n"
            "That's a placeholder, not a working checkout code. "
            "Example codes on mate.fm are also marked as fictional."
        )

    def _track(self, intent: Intent, user_id: str) -> str:
        shipment = self.tracking.track(intent.tracking_number, intent.store, user_id)
        number = shipment.tracking_number or "demo"
        return (
            f"[demo] No live carrier lookup in this starter.\n\n"
            f"{shipment.detail}\n"
            f"Status: {shipment.status.replace('_', ' ')}\n"
            f"Tracking: {number}\n\n"
            "Say “tell my room-mate” to share demo delivery alerts."
        )

    def _watch(self, intent: Intent, user_id: str) -> str:
        if not intent.url:
            return (
                "Send the link you're eyeing and I'll watch the price in this "
                "demo. Example: watch https://shop.example/item"
            )
        watch = self.prices.watch(intent.url, user_id)
        price = f"{watch.currency} {watch.last_price:.2f}"
        return (
            f"[demo] I'll watch that URL in the local demo job.\n\n"
            f"{watch.title}\n"
            f"{intent.url}\n"
            f"Current demo price: {price}\n\n"
            "This is not a live scrape of the product page. Run "
            "`python -m mate watch --simulate-drop` to see a demo drop alert."
        )

    def _balance(self, user_id: str) -> str:
        amount = self.cashback.balance(user_id)
        return (
            f"[demo] Your starter balance is ${amount:.2f}. "
            "It only changes if a demo credit is recorded in this environment. "
            "It is not your live Mate balance."
        )

    def _share(self, user_id: str) -> str:
        shipment = self.tracking.share(user_id, "room-mate")
        if not shipment:
            return (
                "I don't have a demo package on file for you yet. "
                "Text “track DEMO-123456” or “where's my order” first, "
                "then ask me to tell your room-mate."
            )
        return (
            f"[demo] I'll text delivery updates to your room-mate in this stub.\n\n"
            f"Still watching: {shipment.tracking_number} ({shipment.status.replace('_', ' ')}).\n"
            "No real message is sent from this starter."
        )

    def _unknown(self, intent: Intent, text: str, user_id: str) -> Reply:
        if self.llm.enabled:
            try:
                content = self.llm.complete(text, user_id=user_id)
                if content:
                    return Reply(content, intent, demo=False, used_llm=True)
            except Exception as exc:  # noqa: BLE001 — surface a soft fallback
                return Reply(
                    f"{UNKNOWN_TEXT}\n\n(LLM fallback failed: {exc})",
                    intent,
                    demo=False,
                    used_llm=False,
                )
        return Reply(UNKNOWN_TEXT, intent, demo=False)
