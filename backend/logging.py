"""Logging configuration helpers."""
from __future__ import annotations

import logging
from logging import Logger


def setup_logging(level: int = logging.INFO) -> Logger:
    """Configure the root logger for the application."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logger = logging.getLogger("simplespecs")
    logger.debug("Logging configured", extra={"level": level})
    return logger
