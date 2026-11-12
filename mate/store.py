"""Tiny JSON document store for demo balances, watches, and packages."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        if not self.path.exists():
            self._write({})

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        text = self.path.read_text(encoding="utf-8") or "{}"
        data = json.loads(text)
        if not isinstance(data, dict):
            return {}
        return data

    def _write(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._read().get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            data = self._read()
            data[key] = value
            self._write(data)

    def update(self, key: str, mutator) -> Any:
        with self._lock:
            data = self._read()
            current = data.get(key)
            updated = mutator(current)
            data[key] = updated
            self._write(data)
            return updated

    def all(self) -> dict[str, Any]:
        with self._lock:
            return self._read()
