"""Helper script to launch the SimpleSpecs backend and static frontend server."""
from __future__ import annotations

import argparse
import contextlib
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn

import uvicorn


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server serving static files."""

    allow_reuse_address = True
    daemon_threads = True


def _start_static_server(host: str, port: int) -> tuple[threading.Thread, ThreadedHTTPServer] | tuple[None, None]:
    """Launch a background static file server for the frontend directory."""

    if not FRONTEND_DIR.exists():
        return None, None

    handler_factory = partial(SimpleHTTPRequestHandler, directory=str(FRONTEND_DIR))
    server: ThreadedHTTPServer = ThreadedHTTPServer((host, port), handler_factory)  # type: ignore[arg-type]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread, server


def main() -> int:
    """Start backend & static frontend servers."""

    parser = argparse.ArgumentParser(description="Run the SimpleSpecs API server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind")
    parser.add_argument("--static-port", default=8001, type=int, help="Port to serve static frontend files")
    args = parser.parse_args()

    static_thread, static_server = _start_static_server(args.host, args.static_port)

    try:
        uvicorn.run("backend.main:create_app", factory=True, host=args.host, port=args.port)
    finally:
        if static_server is not None:
            with contextlib.suppress(Exception):
                static_server.shutdown()
        if static_thread is not None:
            static_thread.join(timeout=1)
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    raise SystemExit(main())
