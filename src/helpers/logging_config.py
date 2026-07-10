"""Reusable logging helpers for the classification engine."""

from __future__ import annotations

import logging
from typing import Optional


def configure_logging(name: str = "classification_engine") -> logging.Logger:
    """Configure and return a logger with a simple, reusable format.

    Args:
        name: Logger name.

    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
