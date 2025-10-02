"""Local development runner."""
from __future__ import annotations

import uvicorn


def main() -> int:
    """Run backend only (dev)."""

    uvicorn.run("backend.main:create_app", factory=True, host="127.0.0.1", port=8000, reload=True)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
