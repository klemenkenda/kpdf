"""Application entry point for kPDF."""

import logging
import sys

from PySide6.QtWidgets import QApplication

from kpdf.ui.main_window import MainWindow
from kpdf.utils.logging_config import configure_logging


def main() -> int:
    configure_logging()
    logging.getLogger("kPDF").info("Starting application")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
