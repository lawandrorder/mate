"""Run a pass over saved demo price watches."""

from __future__ import annotations

from mate.agent import MateAgent
from mate.config import Config, load_config


def run_watch(config: Config | None = None, simulate_drop: bool = False) -> list[str]:
    agent = MateAgent(config or load_config())
    watches = agent.prices.list_watches()
    if not watches:
        return ["No saved watches. Text “watch https://example.com/item” first."]
    dropped = agent.prices.tick(simulate_drop=simulate_drop)
    lines = [f"Checked {len(watches)} demo watch(es)."]
    if not dropped:
        lines.append("No demo drops this pass.")
        return lines
    for item in dropped:
        prev = f"{item.currency} {item.previous_price:.2f}" if item.previous_price is not None else "?"
        now = f"{item.currency} {item.last_price:.2f}"
        lines.append(
            f"[demo] Price drop: {item.title} went from {prev} to {now}. {item.url}"
        )
    return lines
