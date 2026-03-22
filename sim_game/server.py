from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from sim_game.config import FIELD_SCHEMA, WorldConfig
from sim_game.engine import SimulationEngine
from sim_game.presets import DEFAULT_PRESET, PRESETS, serialize_presets


ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"


class SimulationHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int]) -> None:
        super().__init__(server_address, SimulationRequestHandler)
        self.engine = SimulationEngine(PRESETS[DEFAULT_PRESET])


class SimulationRequestHandler(BaseHTTPRequestHandler):
    server: SimulationHTTPServer

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/bootstrap":
            self._send_json(
                {
                    "defaultPreset": DEFAULT_PRESET,
                    "presets": serialize_presets(),
                    "fieldSchema": FIELD_SCHEMA,
                    "policies": self.server.engine.available_policies(),
                    "operations": self.server.engine.available_operations(),
                    "state": self.server.engine.serialize_state(),
                }
            )
            return
        if path == "/api/state":
            self._send_json(self.server.engine.serialize_state())
            return
        self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        payload = self._read_json()
        if path == "/api/reset":
            self._send_json(self.server.engine.reset(self._parse_config(payload.get("config"))))
            return
        if path == "/api/step":
            operations = payload.get("operations") or []
            if not isinstance(operations, list):
                operations = []
            self._send_json(
                self.server.engine.step(
                    str(payload.get("policy", "balanced")),
                    [str(item) for item in operations],
                )
            )
            return
        if path == "/api/run":
            turns = max(1, min(int(payload.get("turns", 1)), 100))
            policy = str(payload.get("policy", "balanced"))
            schedule = payload.get("schedule") or []
            if not isinstance(schedule, list):
                schedule = []
            operations = payload.get("operations") or []
            if not isinstance(operations, list):
                operations = []
            self._send_json(
                self.server.engine.run(
                    turns,
                    policy,
                    [str(item) for item in schedule],
                    [str(item) for item in operations],
                )
            )
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def log_message(self, format: str, *args: object) -> None:
        return

    def _parse_config(self, payload: object) -> WorldConfig:
        if isinstance(payload, dict):
            return WorldConfig.from_dict(payload)
        return PRESETS[DEFAULT_PRESET]

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, path: str) -> None:
        target = WEB_DIR / "index.html" if path in {"", "/"} else (WEB_DIR / path.lstrip("/")).resolve()
        if target != WEB_DIR and WEB_DIR not in target.parents:
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return
        if not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the settlement simulation game server.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind.")
    args = parser.parse_args()

    server = SimulationHTTPServer((args.host, args.port))
    print(f"Settlement simulation available at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
