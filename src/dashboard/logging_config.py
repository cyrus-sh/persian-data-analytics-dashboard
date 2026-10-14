"""Structured JSON logging configuration."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from pythonjsonlogger import jsonlogger

from dashboard.config import LOG_DIR


def configure_logging() -> logging.Logger:
    """Configure a compact structured logger for app events.

    Returns:
        A module-level logger ready for application use.
    """

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("persian_data_dashboard")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(module)s %(funcName)s"
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        Path(LOG_DIR / "app.log"),
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
