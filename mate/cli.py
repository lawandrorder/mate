"""Command line for the Mate starter: chat, serve, watch."""

from __future__ import annotations

import argparse
import sys

from mate import __version__
from mate.agent import MateAgent
from mate.config import load_config
from mate.jobs.watch import run_watch
from mate.server import serve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mate",
        description="Mate starter — a text-first shopping agent you can run locally.",
    )
    parser.add_argument("--version", action="version", version=f"mate-starter {__version__}")
    sub = parser.add_subparsers(dest="command")

    chat = sub.add_parser("chat", help="Handle one message and print the reply")
    chat.add_argument("text", nargs="+", help="The shopper message")
    chat.add_argument("--user", default="cli", help="User id for demo state")

    serve_p = sub.add_parser("serve", help="Run the web chat demo and Twilio webhook")
    serve_p.add_argument("--host", default=None)
    serve_p.add_argument("--port", type=int, default=None)

    watch = sub.add_parser("watch", help="Run one pass of the demo price watcher")
    watch.add_argument(
        "--simulate-drop",
        action="store_true",
        help="Drop every unsaved demo watch by 15% and print alerts",
    )
    watch.add_argument("--once", action="store_true", help=argparse.SUPPRESS)

    # Bare `python -m mate "cashback at demo"` convenience.
    if argv is None:
        argv = sys.argv[1:]
    if argv and not argv[0].startswith("-") and argv[0] not in {"chat", "serve", "watch"}:
        argv = ["chat", *argv]

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    if args.command == "chat":
        text = " ".join(args.text)
        reply = MateAgent().handle(text, user_id=args.user)
        print(reply.text)
        return 0

    if args.command == "serve":
        overrides = {}
        if args.host:
            overrides["host"] = args.host
        if args.port:
            overrides["port"] = args.port
        config = load_config(overrides or None)
        serve(config)
        return 0

    if args.command == "watch":
        lines = run_watch(simulate_drop=args.simulate_drop)
        print("\n".join(lines))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
