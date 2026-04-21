"""Logging configuration for kPDF."""

import logging
from pathlib import Path

from kpdf.config import APP_NAME, LOG_DIR


def configure_logging() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "kpdf.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logging.getLogger(APP_NAME).info("Logging initialized")
    return log_file
