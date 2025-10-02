"""Entrypoint to serve the SimpleSpecs application."""
from __future__ import annotations

import uvicorn


def main() -> int:
    """Start the backend with uvicorn."""

    uvicorn.run("backend.main:create_app", factory=True, host="0.0.0.0", port=8000)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
