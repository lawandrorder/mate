#!/usr/bin/env python3
"""Generate Mate brand marks, the original icon set, PNG exports, and social images."""

from __future__ import annotations

import math
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"
BRAND = ASSETS / "brand"
DOCS = ROOT / "docs"

BLUE = "#2E94D6"
BLUE_DARK = "#1C6391"
BLUE_HOVER = "#2578B3"
BLUE_SOFT = "#CDE7FC"
BLUE_WASH = "#EAF5FC"
INK = "#0D0D0D"
INK_SOFT = "#1D1D1D"
SECONDARY = "#656565"
MUTED = "#ADADAD"
GREEN = "#5AA83E"
ORANGE = "#F0813C"
CREAM = "#FAF9F6"
FIELD = "#F3F5F7"
LINE = "#E2E2E2"
WHITE = "#FFFFFF"

GEIST = Path(
    "/usr/share/fonts/truetype/sand-box/google/Geist/Geist-VariableFont_wght.ttf"
)
GEIST_MONO = Path(
    "/usr/share/fonts/truetype/sand-box/google/Geist Mono/GeistMono-VariableFont_wght.ttf"
)


def font(path: Path, size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(path), size)
    if hasattr(f, "set_variation_by_axes"):
        f.set_variation_by_axes([weight])
    return f


def svg_doc(body: str, size: int = 48, bg: str | None = None) -> str:
    bg_el = (
        f'<rect width="{size}" height="{size}" rx="{size/2}" fill="{bg}"/>'
        if bg
        else ""
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'fill="none" role="img">\n{bg_el}{body}\n</svg>\n'
    )


# Official Mate mark path, published at https://mate.fm/icon.svg
MARK_PATH = (
    "M195.199 122.44L128.695 198.971V151.324H73.645V203.681L142.951 203.69"
    "C170.718 203.69 193.941 192.578 210.619 173.39L254.895 122.44H195.199Z"
)


def logo_svg(bg: str = BLUE, fg: str = WHITE, size: int = 320) -> str:
    # Scale official 320 viewBox into size
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" fill="none" role="img" aria-label="Mate">\n'
        f'<circle cx="160" cy="160" r="160" fill="{bg}"/>\n'
        f'<path d="{MARK_PATH}" fill="{fg}"/>\n'
        f"</svg>\n"
    )


def favicon_svg() -> str:
    return logo_svg()


# Shared stroke attributes for the 48x48 icon set
ST = f'stroke="{BLUE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
ST_INK = f'stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
FILL = f'fill="{BLUE}"'
FILL_SOFT = f'fill="{BLUE_SOFT}"'


def icons() -> dict[str, tuple[str, str]]:
    """name -> (title, inner svg). All 48x48, original, monochrome Mate blue."""
    return {
        "chat-bubble": (
            "Chat bubble",
            f'''
            <path {ST} d="M12 14.5c0-3.038 3.806-5.5 8.5-5.5h7c4.694 0 8.5 2.462 8.5 5.5v9c0 3.038-3.806 5.5-8.5 5.5h-3.2L18 38.5l1.4-4.5H20.5c-4.694 0-8.5-2.462-8.5-5.5v-9z"/>
            <circle cx="20.5" cy="19.5" r="1.4" fill="{BLUE}"/>
            <circle cx="24.5" cy="19.5" r="1.4" fill="{BLUE}"/>
            <circle cx="28.5" cy="19.5" r="1.4" fill="{BLUE}"/>
            ''',
        ),
        "cashback": (
            "Cashback",
            f'''
            <circle {ST} cx="24" cy="24" r="13.5"/>
            <path {ST} d="M24 16.5v15M20 19.2c.7-1.3 2-2 4-2 2.6 0 4.2 1.3 4.2 3.2 0 4.6-8.4 2.4-8.4 6.6 0 1.9 1.7 3.4 4.3 3.4 2.1 0 3.5-.8 4.3-2.2"/>
            <path {ST} d="M33.5 11.5c2.4 1.2 4.6 3.2 6 5.6M39.5 11.5v6h-6"/>
            ''',
        ),
        "coupon": (
            "Discount code",
            f'''
            <path {ST} d="M8.5 18.5c0-2.2 1.8-4 4-4h23c2.2 0 4 1.8 4 4v2.2a3.3 3.3 0 0 0 0 6.6v2.2c0 2.2-1.8 4-4 4h-23c-2.2 0-4-1.8-4-4v-2.2a3.3 3.3 0 0 0 0-6.6v-2.2z"/>
            <path {ST} stroke-dasharray="2.2 3.2" d="M24 14.5v19"/>
            <circle cx="17.5" cy="24" r="1.6" fill="{BLUE}"/>
            <path {ST} d="M29 21.5h3.5M29 26.5h3.5"/>
            ''',
        ),
        "barcode": (
            "Barcode",
            f'''
            <path {ST} d="M8 14v20M12.5 14v20M15.5 14v20M21 14v20M24.5 14v20M28 14v20M34 14v20M37.5 14v20M40 14v20"/>
            <path stroke="{BLUE}" stroke-width="2.8" stroke-linecap="round" d="M18 14v20M31 14v20"/>
            ''',
        ),
        "package": (
            "Package",
            f'''
            <path {ST} d="M8.5 18.5 24 11.5l15.5 7v16L24 41.5 8.5 34.5v-16z"/>
            <path {ST} d="M8.5 18.5 24 25.5l15.5-7M24 25.5V41.5"/>
            <path {ST} d="M16 15 24 11.5 29.5 14"/>
            ''',
        ),
        "truck": (
            "Truck",
            f'''
            <path {ST} d="M6.5 17.5h20v14h-20z"/>
            <path {ST} d="M26.5 22.5h8.2L40.5 28v3.5h-14"/>
            <circle {ST} cx="14" cy="33.5" r="3.2"/>
            <circle {ST} cx="33.2" cy="33.5" r="3.2"/>
            <path {ST} d="M6.5 17.5 12 11.5h9.5v6"/>
            ''',
        ),
        "delivered": (
            "Delivered",
            f'''
            <path {ST} d="M8.5 19 24 12l15.5 7v12.5L24 38.5 8.5 31.5V19z"/>
            <path {ST} d="M8.5 19 24 26l15.5-7"/>
            <path {ST} d="M16.5 25.5 21.2 30l8.3-9.5"/>
            ''',
        ),
        "check-circle": (
            "Check circle",
            f'''
            <circle {ST} cx="24" cy="24" r="13.5"/>
            <path {ST} d="M17 24.5 21.5 29l9.5-11"/>
            ''',
        ),
        "price-drop": (
            "Price drop",
            f'''
            <path {ST} d="M10 14.5h16.5c.8 0 1.5.3 2.1.9l9.5 9.5a3 3 0 0 1 0 4.2l-8.3 8.3a3 3 0 0 1-4.2 0L15 27.4a3 3 0 0 1-.9-2.1V14.5z"/>
            <circle cx="18.2" cy="20.2" r="1.8" fill="{BLUE}"/>
            <path {ST} d="M33 14.5v9.5M33 24l-3.4-3.4M33 24l3.4-3.4"/>
            ''',
        ),
        "bell": (
            "Alert bell",
            f'''
            <path {ST} d="M14 20.5a10 10 0 0 1 20 0c0 8 2.5 10 2.5 10H11.5s2.5-2 2.5-10z"/>
            <path {ST} d="M21 34.5a3 3 0 0 0 6 0"/>
            ''',
        ),
        "wallet": (
            "Wallet",
            f'''
            <path {ST} d="M9 16.5h24.5A3.5 3.5 0 0 1 37 20v15.5A3.5 3.5 0 0 1 33.5 39H12.5A3.5 3.5 0 0 1 9 35.5v-19z"/>
            <path {ST} d="M9 16.5 28.5 9.5 37 16.5"/>
            <circle cx="31.5" cy="27.5" r="1.8" fill="{BLUE}"/>
            <path {ST} d="M27 27.5h10.5"/>
            ''',
        ),
        "store": (
            "Store",
            f'''
            <path {ST} d="M8.5 20.5 12 12.5h24l3.5 8"/>
            <path {ST} d="M8.5 20.5h31v16h-31z"/>
            <path {ST} d="M12.5 20.5a3.5 3.5 0 0 0 7 0 3.5 3.5 0 0 0 7 0 3.5 3.5 0 0 0 7 0 3.5 3.5 0 0 0 7 0"/>
            <path {ST} d="M20 36.5v-8h8v8"/>
            ''',
        ),
        "tag": (
            "Tag",
            f'''
            <path {ST} d="M9.5 22.8 22.8 9.5h13.7v13.7L23.2 36.5a3 3 0 0 1-4.2 0L9.5 27a3 3 0 0 1 0-4.2z"/>
            <circle cx="30.2" cy="16.2" r="2.1" fill="{BLUE}"/>
            ''',
        ),
        "cart": (
            "Cart",
            f'''
            <path {ST} d="M8 10.5h4.2l3.2 20.2H35"/>
            <path {ST} d="M14.5 14.5h22.2l-2.4 12.2H16.2z"/>
            <circle {ST} cx="19" cy="37.2" r="2.3"/>
            <circle {ST} cx="31.5" cy="37.2" r="2.3"/>
            ''',
        ),
        "bag": (
            "Shopping bag",
            f'''
            <path {ST} d="M12 16.5h24l-1.6 20.2A3 3 0 0 1 31.4 39.5H16.6a3 3 0 0 1-3-2.8L12 16.5z"/>
            <path {ST} d="M18.5 16.5v-2a5.5 5.5 0 0 1 11 0v2"/>
            ''',
        ),
        "link": (
            "Tracked link",
            f'''
            <path {ST} d="M20 28.5 16.5 32a6 6 0 0 1-8.5-8.5L14 17.5a6 6 0 0 1 8.5 0"/>
            <path {ST} d="M28 19.5 31.5 16a6 6 0 1 1 8.5 8.5L34 30.5a6 6 0 0 1-8.5 0"/>
            <path {ST} d="M20 28.5 28 19.5"/>
            ''',
        ),
        "share": (
            "Share",
            f'''
            <circle {ST} cx="12.5" cy="24" r="4"/>
            <circle {ST} cx="35" cy="13.5" r="4"/>
            <circle {ST} cx="35" cy="34.5" r="4"/>
            <path {ST} d="M16.3 22.2 31.2 15.3M16.3 25.8 31.2 32.7"/>
            ''',
        ),
        "users": (
            "Users",
            f'''
            <circle {ST} cx="18" cy="16.5" r="5"/>
            <path {ST} d="M8.5 34.5c1.2-6 4.8-9 9.5-9s8.3 3 9.5 9"/>
            <circle {ST} cx="31.5" cy="17.5" r="4"/>
            <path {ST} d="M28.2 27.2c3.3-1.2 6.7-.4 9.3 2.6 1.2 1.4 2 3.3 2.5 4.7"/>
            ''',
        ),
        "roommate": (
            "Room-mate",
            f'''
            <path {ST} d="M8.5 22.5 18 15l9.5 7.5V35.5h-19z"/>
            <path {ST} d="M14 35.5v-8h8v8"/>
            <circle {ST} cx="34.5" cy="18" r="4"/>
            <path {ST} d="M27.8 33.5c.9-5 3.8-7.5 6.7-7.5s6 2.6 6.8 7.5"/>
            ''',
        ),
        "phone": (
            "Phone",
            f'''
            <rect {ST} x="14.5" y="7.5" width="19" height="33" rx="4"/>
            <path {ST} d="M21 34.5h6"/>
            <path {ST} d="M22 11.5h4"/>
            ''',
        ),
        "percent": (
            "Percent off",
            f'''
            <circle {ST} cx="16.5" cy="16.5" r="5"/>
            <circle {ST} cx="31.5" cy="31.5" r="5"/>
            <path {ST} d="M14 34 34 14"/>
            ''',
        ),
        "receipt": (
            "Receipt",
            f'''
            <path {ST} d="M15 8.5h18v31l-3-2-3 2-3-2-3 2-3-2-3 2v-31z"/>
            <path {ST} d="M20 16.5h8M20 21.5h8M20 26.5h5"/>
            ''',
        ),
        "card": (
            "Card",
            f'''
            <rect {ST} x="7.5" y="12.5" width="33" height="23" rx="3.5"/>
            <path {ST} d="M7.5 19.5h33"/>
            <path {ST} d="M12.5 27.5h9M28.5 27.5h7"/>
            ''',
        ),
        "search": (
            "Search",
            f'''
            <circle {ST} cx="22" cy="22" r="10.5"/>
            <path {ST} d="M30 30.5 38 38.5"/>
            ''',
        ),
        "shield": (
            "Shield",
            f'''
            <path {ST} d="M24 8.5 38.5 13.5v11c0 8.5-6.2 13.8-14.5 16.2C16 38.3 9.5 33 9.5 24.5v-11L24 8.5z"/>
            <path {ST} d="M19 24.2 22.8 28l7.2-8.5"/>
            ''',
        ),
        "star": (
            "Star",
            f'''
            <path {ST} d="M24 9.5 28.2 18.4l9.8 1.3-7.1 6.8 1.8 9.7L24 31.6l-8.7 4.6 1.8-9.7-7.1-6.8 9.8-1.3L24 9.5z"/>
            ''',
        ),
        "pin": (
            "Map pin",
            f'''
            <path {ST} d="M24 40.5s-11.5-12.2-11.5-19.2a11.5 11.5 0 1 1 23 0c0 7-11.5 19.2-11.5 19.2z"/>
            <circle {ST} cx="24" cy="20.5" r="3.6"/>
            ''',
        ),
        "calendar": (
            "Calendar",
            f'''
            <rect {ST} x="9.5" y="11.5" width="29" height="27" rx="3"/>
            <path {ST} d="M9.5 19.5h29M17 8.5v6M31 8.5v6"/>
            <path {ST} d="M16.5 26.5h3M22.5 26.5h3M28.5 26.5h3M16.5 31.5h3M22.5 31.5h3"/>
            ''',
        ),
        "clock": (
            "Clock",
            f'''
            <circle {ST} cx="24" cy="24" r="13.5"/>
            <path {ST} d="M24 16.5V24l6 3.5"/>
            ''',
        ),
        "user": (
            "User",
            f'''
            <circle {ST} cx="24" cy="16.5" r="6"/>
            <path {ST} d="M10.5 38c1.6-8 6.3-12 13.5-12s11.9 4 13.5 12"/>
            ''',
        ),
        "sparkle": (
            "Sparkle",
            f'''
            <path {ST} d="M24 8.5v6M24 33.5v6M8.5 24h6M33.5 24h6"/>
            <path {ST} d="M24 15.5 27.2 21l6.3 1-5 4.6 1.4 6.4L24 30.2 18.1 33l1.4-6.4-5-4.6 6.3-1L24 15.5z"/>
            <path {ST} d="M13.5 13.5 15 16M34.5 13.5 33 16M13.5 34.5 15 32M34.5 34.5 33 32"/>
            ''',
        ),
        "gift": (
            "Gift",
            f'''
            <rect {ST} x="9.5" y="20.5" width="29" height="18" rx="2"/>
            <path {ST} d="M8.5 20.5h31v-5.5h-31z"/>
            <path {ST} d="M24 15v23.5"/>
            <path {ST} d="M24 15c0-4-3-6.5-6-4.5s-1.5 6 6 6.5c7.5-.5 9-4.5 6-6.5s-6 .5-6 4.5z"/>
            ''',
        ),
        "eye": (
            "Watching",
            f'''
            <path {ST} d="M7.5 24S14 13.5 24 13.5 40.5 24 40.5 24 34 34.5 24 34.5 7.5 24 7.5 24z"/>
            <circle {ST} cx="24" cy="24" r="5"/>
            ''',
        ),
        "globe": (
            "Globe",
            f'''
            <circle {ST} cx="24" cy="24" r="13.5"/>
            <path {ST} d="M10.5 24h27M24 10.5c3.6 3.8 5.5 8.2 5.5 13.5s-1.9 9.7-5.5 13.5c-3.6-3.8-5.5-8.2-5.5-13.5s1.9-9.7 5.5-13.5z"/>
            <path {ST} d="M13.2 16.5h21.6M13.2 31.5h21.6"/>
            ''',
        ),
        "lock": (
            "Lock",
            f'''
            <rect {ST} x="12.5" y="21.5" width="23" height="17" rx="3"/>
            <path {ST} d="M17.5 21.5v-5a6.5 6.5 0 0 1 13 0v5"/>
            <path {ST} d="M24 28.5v4"/>
            ''',
        ),
        "home": (
            "Home",
            f'''
            <path {ST} d="M8.5 22.5 24 9.5l15.5 13V38a2 2 0 0 1-2 2H10.5a2 2 0 0 1-2-2V22.5z"/>
            <path {ST} d="M19 39.5v-10h10v10"/>
            ''',
        ),
        "inbox": (
            "Inbox",
            f'''
            <path {ST} d="M8.5 18.5 14 8.5h20l5.5 10v17a3 3 0 0 1-3 3h-25a3 3 0 0 1-3-3v-17z"/>
            <path {ST} d="M8.5 18.5h9.2l2.3 6h8l2.3-6h9.2"/>
            ''',
        ),
        "send": (
            "Send",
            f'''
            <path {ST} d="M9 24 38.5 10.5 28 38.5 22 25.5 9 24z"/>
            <path {ST} d="M22 25.5 38.5 10.5"/>
            ''',
        ),
        "arrow-up-right": (
            "Arrow up right",
            f'''
            <path {ST} d="M16 32 32 16M18 16h14v14"/>
            ''',
        ),
        "heart": (
            "Heart",
            f'''
            <path {ST} d="M24 38.5s-14.5-8.8-14.5-18A8 8 0 0 1 24 14.5 8 8 0 0 1 38.5 20.5c0 9.2-14.5 18-14.5 18z"/>
            ''',
        ),
        "megaphone": (
            "Megaphone",
            f'''
            <path {ST} d="M8.5 20.5h6l18-8v23l-18-8h-6a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2z"/>
            <path {ST} d="M14.5 27.5v5a4 4 0 0 0 5.6 3.7"/>
            <path {ST} d="M35.5 18.5c1.8 1.6 2.8 3.5 2.8 5.5s-1 3.9-2.8 5.5"/>
            ''',
        ),
        "refresh": (
            "Refresh",
            f'''
            <path {ST} d="M12.5 20.5a11.5 11.5 0 0 1 20.2-5.2M35.5 27.5a11.5 11.5 0 0 1-20.2 5.2"/>
            <path {ST} d="M32.7 8.8v6.7h-6.7M15.3 39.2v-6.7h6.7"/>
            ''',
        ),
        "camera": (
            "Camera",
            f'''
            <rect {ST} x="8.5" y="15.5" width="31" height="21" rx="3"/>
            <circle {ST} cx="24" cy="26" r="6"/>
            <path {ST} d="M17.5 15.5l2.2-4h8.6l2.2 4"/>
            <circle cx="34.5" cy="20.5" r="1.3" fill="{BLUE}"/>
            ''',
        ),
        "headset": (
            "Headset",
            f'''
            <path {ST} d="M10.5 24v-3.5a13.5 13.5 0 0 1 27 0V24"/>
            <rect {ST} x="7.5" y="22.5" width="7" height="11" rx="2.5"/>
            <rect {ST} x="33.5" y="22.5" width="7" height="11" rx="2.5"/>
            <path {ST} d="M40.5 31.5v2A5 5 0 0 1 35.5 38.5H26"/>
            ''',
        ),
        "qr-code": (
            "QR code",
            f'''
            <rect {ST} x="9.5" y="9.5" width="11" height="11" rx="1.5"/>
            <rect {ST} x="27.5" y="9.5" width="11" height="11" rx="1.5"/>
            <rect {ST} x="9.5" y="27.5" width="11" height="11" rx="1.5"/>
            <path {ST} d="M13.5 13.5h3v3h-3zM31.5 13.5h3v3h-3zM13.5 31.5h3v3h-3z"/>
            <path {ST} d="M27.5 27.5h4v4h-4zM34.5 27.5h4v2M27.5 34.5h2v3.5M32.5 33.5h6v5"/>
            ''',
        ),
        "balance": (
            "Balance",
            f'''
            <circle {ST} cx="24" cy="24" r="13.5"/>
            <path {ST} d="M16 24h16"/>
            <path {ST} d="M19.5 19.5c.8-1.6 2.2-2.4 4.5-2.4 2.7 0 4.3 1.3 4.3 3.2 0 4.2-8.6 2.3-8.6 6.6 0 2 1.8 3.5 4.4 3.5 2.3 0 3.8-.9 4.6-2.3"/>
            ''',
        ),
        "list": (
            "List",
            f'''
            <path {ST} d="M18 14.5h19M18 24h19M18 33.5h19"/>
            <circle {ST} cx="11.5" cy="14.5" r="2"/>
            <circle {ST} cx="11.5" cy="24" r="2"/>
            <circle {ST} cx="11.5" cy="33.5" r="2"/>
            ''',
        ),
        "alert": (
            "Alert",
            f'''
            <path {ST} d="M24 8.5 42.5 39.5h-37L24 8.5z"/>
            <path {ST} d="M24 20.5v8"/>
            <circle cx="24" cy="33.2" r="1.4" fill="{BLUE}"/>
            ''',
        ),
        "message": (
            "Text message",
            f'''
            <rect {ST} x="8.5" y="11.5" width="31" height="22" rx="5"/>
            <path {ST} d="M18 33.5 14.5 40.5 25 33.5"/>
            <path {ST} d="M16.5 20.5h15M16.5 25.5h10"/>
            ''',
        ),
        "handshake": (
            "Partnership",
            f'''
            <path {ST} d="M8.5 22.5 16 15.5l5 5 3-3 4.5 4.5"/>
            <path {ST} d="M39.5 22.5 32 15.5l-5 5-1.5-1.5"/>
            <path {ST} d="M13.5 27.5 20 21l4 4 4-3.5 6.5 6"/>
            <path {ST} d="M16 32.5c2.5 3 6 4.5 8 4.5s5.5-1.5 8-4.5"/>
            ''',
        ),
    }


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def export_png(svg_path: Path, png_path: Path, px: int) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=px,
        output_height=px,
        background_color=None,
    )


def make_preview(entries: list[tuple[str, str, Path]]) -> Path:
    """Grid preview sheet of every icon with labels."""
    cols = 8
    rows = math.ceil(len(entries) / cols)
    tile = 128
    pad = 28
    label_h = 36
    header = 160
    footer = 64
    width = pad * 2 + cols * tile + (cols - 1) * 20
    height = header + rows * (tile + label_h + 24) + footer
    img = Image.new("RGB", (width, height), CREAM)
    draw = ImageDraw.Draw(img)

    title = font(GEIST, 42, 700)
    sub = font(GEIST, 18, 400)
    label_font = font(GEIST, 13, 500)
    mono = font(GEIST_MONO, 12, 500)

    # header logo
    logo = Image.open(BRAND / "logo-512.png").convert("RGBA").resize((56, 56), Image.Resampling.LANCZOS)
    img.paste(logo, (pad, 48), logo)
    draw.text((pad + 68, 50), "Mate icons", font=title, fill=INK)
    draw.text(
        (pad + 68, 100),
        f"{len(entries)} original marks  ·  mate.fm palette  ·  stroke set, 48×48",
        font=sub,
        fill=SECONDARY,
    )

    for i, (name, title_, png64) in enumerate(entries):
        r, c = divmod(i, cols)
        x = pad + c * (tile + 20)
        y = header + r * (tile + label_h + 24)
        # tile
        tile_img = Image.new("RGBA", (tile, tile), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(tile_img)
        tdraw.rounded_rectangle((0, 0, tile - 1, tile - 1), radius=28, fill=WHITE, outline=LINE, width=1)
        icon = Image.open(png64).convert("RGBA")
        icon = icon.resize((72, 72), Image.Resampling.LANCZOS)
        ix = (tile - 72) // 2
        iy = (tile - 72) // 2
        tile_img.paste(icon, (ix, iy), icon)
        img.paste(tile_img, (x, y), tile_img)
        # label centered
        bbox = draw.textbbox((0, 0), name, font=label_font)
        tw = bbox[2] - bbox[0]
        draw.text((x + (tile - tw) / 2, y + tile + 8), name, font=label_font, fill=INK_SOFT)

    draw.text((pad, height - 40), "Original set for the Mate starter repo. Not affiliated with any merchant brands.", font=mono, fill=MUTED)
    out = ICONS / "preview.png"
    img.save(out, "PNG", optimize=True)
    return out


def make_social() -> Path:
    """1280x640 GitHub social preview."""
    w, h = 1280, 640
    img = Image.new("RGB", (w, h), WHITE)
    draw = ImageDraw.Draw(img)

    # subtle soft blue wash at the top
    wash = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(wash)
    for i in range(220):
        alpha = int(28 * (1 - i / 220))
        wdraw.rectangle((0, i, w, i + 1), fill=(46, 148, 214, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), wash).convert("RGB")
    draw = ImageDraw.Draw(img)

    logo = Image.open(BRAND / "logo-512.png").convert("RGBA").resize((112, 112), Image.Resampling.LANCZOS)

    word = font(GEIST, 120, 700)
    tag = font(GEIST, 36, 500)
    urlf = font(GEIST, 24, 500)

    word_text = "mate"
    tag_text = "Your mate while you shop."
    url_text = "mate.fm"

    wb = draw.textbbox((0, 0), word_text, font=word)
    ww = wb[2] - wb[0]
    gap = 28
    group = 112 + gap + ww
    x0 = (w - group) // 2
    y0 = 188
    img.paste(logo, (x0, y0 + 8), logo)
    # tight tracking approximation: draw as a whole; Geist Bold already tight-ish
    draw.text((x0 + 112 + gap, y0), word_text, font=word, fill=INK)

    tb = draw.textbbox((0, 0), tag_text, font=tag)
    tw = tb[2] - tb[0]
    draw.text(((w - tw) // 2, y0 + 150), tag_text, font=tag, fill=INK)

    ub = draw.textbbox((0, 0), url_text, font=urlf)
    uw = ub[2] - ub[0]
    draw.text(((w - uw) // 2, y0 + 210), url_text, font=urlf, fill=MUTED)

    out = ASSETS / "social-preview.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    return out


def copy_into_docs():
    dest = DOCS / "assets"
    dest.mkdir(parents=True, exist_ok=True)
    import shutil

    shutil.copy2(BRAND / "logo.svg", dest / "logo.svg")
    shutil.copy2(BRAND / "favicon.svg", dest / "favicon.svg")
    shutil.copy2(BRAND / "favicon-32.png", dest / "favicon-32.png")
    shutil.copy2(BRAND / "apple-touch-icon.png", dest / "apple-touch-icon.png")
    shutil.copy2(ASSETS / "social-preview.png", dest / "social-preview.png")
    icons_dest = dest / "icons"
    icons_dest.mkdir(exist_ok=True)
    for p in (ICONS / "svg").glob("*.svg"):
        shutil.copy2(p, icons_dest / p.name)


def main() -> None:
    # Brand mark
    write(BRAND / "logo.svg", logo_svg())
    write(BRAND / "logo-ink.svg", logo_svg(bg=INK, fg=WHITE))
    write(BRAND / "favicon.svg", favicon_svg())
    export_png(BRAND / "logo.svg", BRAND / "logo-512.png", 512)
    export_png(BRAND / "logo.svg", BRAND / "logo-1024.png", 1024)
    export_png(BRAND / "logo.svg", BRAND / "favicon-32.png", 32)
    write(
        BRAND / "app-icon.svg",
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" fill="none" role="img" aria-label="Mate">
  <rect width="320" height="320" rx="72" fill="{BLUE}"/>
  <path d="{MARK_PATH}" fill="{WHITE}"/>
</svg>
""",
    )
    export_png(BRAND / "app-icon.svg", BRAND / "app-icon-512.png", 512)
    export_png(BRAND / "app-icon.svg", BRAND / "app-icon-1024.png", 1024)
    export_png(BRAND / "app-icon.svg", BRAND / "apple-touch-icon.png", 180)
    export_png(BRAND / "logo.svg", BRAND / "logo-192.png", 192)

    # Wordmark-only SVG (mark + mate text is drawn in raster social; SVG wordmark for docs)
    write(
        BRAND / "wordmark.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 80" role="img" aria-label="mate">
  <circle cx="40" cy="40" r="40" fill="{BLUE}"/>
  <path transform="translate(0,0) scale(0.25)" d="{MARK_PATH}" fill="{WHITE}"/>
  <text x="98" y="57" font-family="Geist, Inter, Helvetica, Arial, sans-serif" font-size="52" font-weight="700" fill="{INK}" letter-spacing="-1.5">mate</text>
</svg>
''',
    )

    catalog = icons()
    entries = []
    readme_rows = []
    for name, (title, body) in catalog.items():
        svg_path = ICONS / "svg" / f"{name}.svg"
        write(svg_path, svg_doc(body))
        for size in (64, 128, 512):
            export_png(svg_path, ICONS / "png" / str(size) / f"{name}.png", size)
        entries.append((name, title, ICONS / "png" / "64" / f"{name}.png"))
        readme_rows.append((name, title))

    preview = make_preview(entries)
    social = make_social()
    copy_into_docs()

    lines = [
        "# Mate icons",
        "",
        "Original stroke icons drawn for this repository in the [mate.fm](https://mate.fm/) palette.",
        "They are not merchant or third-party brand logos.",
        "",
        f"**{len(readme_rows)} icons** · viewBox `48×48` · primary stroke `{BLUE}` · round caps.",
        "",
        "![Icon preview](preview.png)",
        "",
        "## Files",
        "",
        "- `svg/` — source marks",
        "- `png/64`, `png/128`, `png/512` — raster exports",
        "- `preview.png` — contact sheet",
        "",
        "## Palette",
        "",
        f"- Blue `{BLUE}` (primary mark, same as the Mate logo)",
        f"- Ink `{INK}`",
        f"- Soft blue `{BLUE_SOFT}`",
        f"- Green `{GREEN}` and orange `{ORANGE}` appear in the product site and may be used as status accents, not in this monochrome set",
        "",
        "## Catalog",
        "",
        "| File | Meaning |",
        "| --- | --- |",
    ]
    for name, title in readme_rows:
        lines.append(f"| `{name}` | {title} |")
    lines += [
        "",
        "Regenerate with `python tools/generate_assets.py` (needs Pillow and cairosvg).",
        "",
    ]
    write(ICONS / "README.md", "\n".join(lines))
    print(f"wrote {len(readme_rows)} icons")
    print("preview", preview)
    print("social", social)


if __name__ == "__main__":
    main()
