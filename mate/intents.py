"""Parse a shopper's text into a structured intent.

The patterns follow how people text Mate on mate.fm: cashback at a store,
a code for a store, tracking a package, or watching a price.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


INTENT_CASHBACK = "cashback"
INTENT_CODE = "code"
INTENT_TRACK = "track"
INTENT_WATCH = "watch"
INTENT_BALANCE = "balance"
INTENT_SHARE = "share"
INTENT_HELP = "help"
INTENT_GREET = "greet"
INTENT_UNKNOWN = "unknown"

# A tracking-number-like token: UPS 1Z, USPS, FedEx-ish, or a long alphanumeric.
TRACKING_TOKEN = re.compile(
    r"\b("
    r"1Z[0-9A-Z]{16}"
    r"|[A-Z]{2}\d{9}[A-Z]{2}"
    r"|\d{12,22}"
    r"|[A-Z0-9]{10,30}"
    r")\b",
    re.I,
)

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)

STORE_TAIL = r"(?P<store>.+?)\s*[.!?]*$"

_CASHBACK = [
    re.compile(
        rf"\b(?:cash\s*back|cashback|deals?|rewards?)\s+(?:at|for|from|with|on)\s+{STORE_TAIL}",
        re.I,
    ),
    re.compile(
        rf"\b(?:any|got|get|need|want|looking for)\s+(?:cash\s*back|cashback|deals?)\s+(?:at|for|from|with)?\s*{STORE_TAIL}",
        re.I,
    ),
    re.compile(
        rf"\b(?:about to buy|buying|checkout|checking out)(?:\s+these|\s+this)?(?:\s+.+?)?\s+(?:at|from)\s+{STORE_TAIL}",
        re.I,
    ),
    re.compile(r"^\s*cashback(?:\s+at)?\s*$", re.I),
]

_CODE = [
    re.compile(
        rf"\b(?:discount\s+)?(?:codes?|coupon(?:s)?|promo(?:\s+codes?)?|vouchers?)\s+(?:at|for|from|with|on)\s+{STORE_TAIL}",
        re.I,
    ),
    re.compile(
        rf"\b(?:any|got|get|need|want)\s+(?:a\s+)?(?:discount\s+)?(?:codes?|coupon(?:s)?|promo)\s+(?:at|for|from|with)?\s*{STORE_TAIL}",
        re.I,
    ),
    re.compile(
        rf"\b(?:generate|make|find)\s+(?:me\s+)?(?:a\s+)?(?:discount\s+)?codes?\s+(?:at|for|from|with)\s+{STORE_TAIL}",
        re.I,
    ),
]

_TRACK = [
    re.compile(
        r"\b(?:track|tracking|status(?:\s+of)?|where(?:'s| is))\s+(?:my\s+)?(?:order\s+|package\s+|pkg\s+)?(?P<number>[A-Za-z0-9\-]{6,})\s*\??\s*$",
        re.I,
    ),
    re.compile(
        r"\b(?:where(?:'s| is)\s+my)\s+(?P<store>.+?)\s+(?:order|package|parcel)\b",
        re.I,
    ),
    re.compile(r"\btrack(?:ing)?\s+(?P<number>[A-Za-z0-9\-]{6,})\b", re.I),
]

_WATCH = re.compile(
    r"\b(?:watch|track(?:\s+the)?\s+price|price(?:\s+drop)?\s+alert|alert(?:s)?(?:\s+me)?)\b",
    re.I,
)

_BALANCE = re.compile(
    r"\b(?:my\s+)?(?:balance|wallet|how much(?:\s+cashback)?(?:\s+do I have)?)\b",
    re.I,
)
_SHARE = re.compile(
    r"\b(?:tell|text|share(?:\s+(?:it|this|tracking))?(?:\s+with)?)\s+(?:my\s+)?(?:room[-\s]?mate|roommate|friend|family)\b",
    re.I,
)
_HELP = re.compile(r"^\s*(?:help|menu|commands?|\?)\s*$", re.I)
_GREET = re.compile(
    r"^\s*(?:hi|hey|hello|yo|what(?:'s| is)\s+up|good\s+(?:morning|afternoon|evening))\b",
    re.I,
)


@dataclass(frozen=True)
class Intent:
    name: str
    raw: str
    store: str | None = None
    tracking_number: str | None = None
    url: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "raw": self.raw,
            "store": self.store,
            "tracking_number": self.tracking_number,
            "url": self.url,
        }


def _clean_store(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    text = re.sub(r"^(the\s+)", "", text, flags=re.I)
    text = re.sub(r"[.!?]+$", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def parse_intent(text: str) -> Intent:
    """Return the best intent for a free-text shopper message."""
    raw = (text or "").strip()
    if not raw:
        return Intent(INTENT_UNKNOWN, raw)

    if _HELP.match(raw):
        return Intent(INTENT_HELP, raw)
    if _GREET.match(raw) and len(raw.split()) <= 6:
        return Intent(INTENT_GREET, raw)

    url = None
    url_match = URL_RE.search(raw)
    if url_match:
        url = url_match.group(0).rstrip(").,]")

    if _SHARE.search(raw):
        store = None
        for pat in _TRACK:
            m = pat.search(raw)
            if m and m.groupdict().get("store"):
                store = _clean_store(m.group("store"))
        number = None
        tm = TRACKING_TOKEN.search(raw)
        if tm:
            number = tm.group(1)
        return Intent(INTENT_SHARE, raw, store=store, tracking_number=number, url=url)

    if url and _WATCH.search(raw):
        return Intent(INTENT_WATCH, raw, url=url)
    if url and re.search(r"\b(?:watch|eyeing|price|drop|track)\b", raw, re.I):
        return Intent(INTENT_WATCH, raw, url=url)
    # A bare URL is treated as a price watch — that's the site's "send something you're eyeing".
    if url and len(raw) <= len(url) + 8:
        return Intent(INTENT_WATCH, raw, url=url)

    for pat in _CASHBACK:
        m = pat.search(raw)
        if m:
            store = _clean_store(m.groupdict().get("store"))
            return Intent(INTENT_CASHBACK, raw, store=store)

    for pat in _CODE:
        m = pat.search(raw)
        if m:
            store = _clean_store(m.groupdict().get("store"))
            return Intent(INTENT_CODE, raw, store=store)

    for pat in _TRACK:
        m = pat.search(raw)
        if m:
            groups = m.groupdict()
            number = groups.get("number")
            store = _clean_store(groups.get("store"))
            if number and not re.search(r"[0-9]", number) and not store:
                # "where's my LANEIGE" captured as a number — treat as store name.
                store = _clean_store(number)
                number = None
            return Intent(INTENT_TRACK, raw, store=store, tracking_number=number)

    if _BALANCE.search(raw):
        return Intent(INTENT_BALANCE, raw)

    if re.search(r"\b(?:cash\s*back|cashback)\b", raw, re.I):
        store = _guess_store(raw)
        return Intent(INTENT_CASHBACK, raw, store=store)
    if re.search(r"\b(?:discount\s+)?(?:codes?|coupon|promo)\b", raw, re.I):
        store = _guess_store(raw)
        return Intent(INTENT_CODE, raw, store=store)

    return Intent(INTENT_UNKNOWN, raw, url=url)


def _guess_store(raw: str) -> str | None:
    m = re.search(r"\b(?:at|for|from|with)\s+(.+)$", raw, re.I)
    if m:
        return _clean_store(m.group(1))
    return None
