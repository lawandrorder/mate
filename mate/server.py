"""Stdlib HTTP server for the web chat demo and the Twilio webhook stub."""

from __future__ import annotations

import json
import mimetypes
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from mate.agent import MateAgent
from mate.adapters.twilio import TwilioAdapter
from mate.config import Config, load_config

WEB_DIR = Path(__file__).resolve().parent / "web"


class MateHandler(BaseHTTPRequestHandler):
    server_version = "MateStarter/0.1"
    agent: MateAgent
    config: Config
    twilio: TwilioAdapter

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _send(self, status: int, body: bytes, content_type: str, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if extra:
            for key, value in extra.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8") + b"\n"
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/", "/index.html"}:
            return self._static("index.html")
        if path == "/health":
            return self._json(
                200,
                {
                    "ok": True,
                    "service": "mate-starter",
                    "openrouter": self.config.openrouter_enabled,
                },
            )
        if path.startswith("/assets/"):
            rel = path[len("/assets/") :]
            # Serve brand and icon previews from the repo when present.
            root = Path(__file__).resolve().parent.parent
            candidate = (root / "assets" / rel).resolve()
            if str(candidate).startswith(str((root / "assets").resolve())) and candidate.is_file():
                return self._file(candidate)
        if path.startswith("/"):
            name = path.lstrip("/")
            if ".." not in name:
                return self._static(name)
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        if parsed.path in {"/api/message", "/api/chat"}:
            return self._chat(body)
        if parsed.path in {"/webhooks/twilio", "/webhook/twilio"}:
            url = self._public_url()
            signature = self.headers.get("X-Twilio-Signature")
            status, content_type, text = self.twilio.handle_webhook(
                body,
                url=url,
                signature=signature,
                content_type=self.headers.get("Content-Type", ""),
            )
            return self._send(status, text.encode("utf-8"), content_type)
        self._json(404, {"error": "not found"})

    def _chat(self, body: bytes) -> None:
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return self._json(400, {"error": "invalid json"})
        text = (payload.get("text") or payload.get("message") or "").strip()
        user_id = (payload.get("user_id") or payload.get("user") or "web").strip() or "web"
        if not text:
            return self._json(400, {"error": "text is required"})
        reply = self.agent.handle(text, user_id=user_id)
        self._json(
            200,
            {
                "reply": reply.text,
                "intent": reply.intent.as_dict(),
                "demo": reply.demo,
                "used_llm": reply.used_llm,
            },
        )

    def _public_url(self) -> str:
        host = self.headers.get("Host") or f"{self.config.host}:{self.config.port}"
        scheme = "https" if self.headers.get("X-Forwarded-Proto") == "https" else "http"
        return f"{scheme}://{host}{self.path}"

    def _static(self, name: str) -> None:
        candidate = (WEB_DIR / name).resolve()
        if not str(candidate).startswith(str(WEB_DIR.resolve())) or not candidate.is_file():
            return self._json(404, {"error": "not found"})
        self._file(candidate)

    def _file(self, candidate: Path) -> None:
        content_type = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
        data = candidate.read_bytes()
        cache = "public, max-age=3600" if candidate.suffix in {".png", ".svg", ".jpg", ".woff2"} else "no-store"
        self._send(200, data, content_type, {"Cache-Control": cache})


def make_server(config: Config | None = None, agent: MateAgent | None = None) -> ThreadingHTTPServer:
    config = config or load_config()
    agent = agent or MateAgent(config)
    handler = type(
        "BoundMateHandler",
        (MateHandler,),
        {
            "agent": agent,
            "config": config,
            "twilio": TwilioAdapter(agent, config),
        },
    )
    server = ThreadingHTTPServer((config.host, config.port), handler)
    return server


def serve(config: Config | None = None) -> None:
    config = config or load_config()
    server = make_server(config)
    print(
        f"Mate starter listening on http://{config.host}:{config.port}",
        file=sys.stderr,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.", file=sys.stderr)
    finally:
        server.server_close()


def serve_in_thread(config: Config | None = None) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = make_server(config)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread
