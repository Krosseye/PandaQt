import argparse
import logging
import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def _setup_logging():
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def _get_fps_cap(screen):
    """Determines the FPS cap based on the screen's refresh rate."""
    if hasattr(screen, "refreshRate"):
        refresh_rate = screen.refreshRate()
        logger.info("Refresh Rate: %i Hz", refresh_rate)
        return int(refresh_rate)
    else:
        logger.info("Couldn't determine refresh rate, defaulting to 45 Hz.")
        return 45


def _create_main_window(fps_cap, enable_hd_renderer):
    """Creates and configures the main window."""
    window = MainWindow(fps_cap, enable_hd_renderer=enable_hd_renderer)

    app_icon = QIcon(os.path.join(os.path.dirname(__file__), "resources", "icon.png"))
    window.setWindowIcon(app_icon)

    available_geometry = window.screen().availableGeometry()
    window.resize(
        (available_geometry.width() * 2) / 3, (available_geometry.height() * 2) / 3
    )
    window.move(
        (available_geometry.width() - window.width()) / 2,
        (available_geometry.height() - window.height()) / 2,
    )

    return window


def _main():
    parser = argparse.ArgumentParser(description="PandaQt Application")
    parser.add_argument(
        "--hd-renderer",
        action="store_true",
        help="Enable experimental HD renderer",
    )
    args = parser.parse_args()

    _setup_logging()

    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    fps_cap = _get_fps_cap(screen)

    window = _create_main_window(fps_cap, enable_hd_renderer=args.hd_renderer)
    window.show()

    # Start engine after creating main window
    window.viewport_widget.engine.run()

    sys.exit(app.exec())


if __name__ == "__main__":
    _main()
