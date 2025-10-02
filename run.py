"""Helper script to launch the SimpleSpecs backend."""
from __future__ import annotations

import argparse

import uvicorn


def main() -> int:
    """Start backend & static frontend servers."""

    parser = argparse.ArgumentParser(description="Run the SimpleSpecs API server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind")
    args = parser.parse_args()

    uvicorn.run("backend.main:create_app", factory=True, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    raise SystemExit(main())
