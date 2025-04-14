"""
Main entry point for the CSV2JSON converter GUI.
"""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Try to import with or without 'src' prefix
try:
    from src.csv2json.core.logging import logger, setup_file_logging
    from src.csv2json.gui.services.theme_service import ThemeService
    from src.csv2json.gui.windows.main_window import MainWindow
except ImportError:
    from csv2json.core.logging import logger, setup_file_logging
    from csv2json.gui.services.theme_service import ThemeService
    from csv2json.gui.windows.main_window import MainWindow


def main():
    """
    Main entry point for the GUI application.
    """
    # Set up logging
    setup_file_logging()
    logger.info("CSV2JSON Converter started")

    app = QApplication(sys.argv)

    # Determine if we're running in a PyInstaller bundle
    def is_bundled():
        return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

    # Set application icon - try multiple possible paths
    icon_paths = []

    if is_bundled():
        # PyInstaller paths
        base_path = sys._MEIPASS
        icon_paths.extend([
            os.path.join(base_path, "csv2json", "resources", "csv2json.ico"),
            os.path.join(base_path, "resources", "csv2json.ico"),
            os.path.join(base_path, "csv2json.ico"),
            # Also check executable directory
            os.path.join(os.path.dirname(sys.executable), "csv2json.ico"),
        ])
    else:
        # Development paths
        icon_paths.extend([
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "csv2json.ico"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "csv2json.ico"),
        ])

    # Common paths to try in both modes
    icon_paths.extend([
        os.path.join("csv2json", "resources", "csv2json.ico"),
        os.path.join(os.path.dirname(sys.executable), "csv2json", "resources", "csv2json.ico"),
        # Try the current directory
        os.path.join(os.getcwd(), "csv2json.ico"),
        os.path.join(os.getcwd(), "resources", "csv2json.ico"),
        os.path.join(os.getcwd(), "csv2json", "resources", "csv2json.ico"),
    ])

    # Log all paths we're checking
    logger.debug(f"Checking icon paths: {icon_paths}")

    icon_set = False
    for icon_path in icon_paths:
        try:
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
                logger.info(f"Set application icon: {icon_path}")
                icon_set = True
                break
        except Exception as e:
            logger.error(f"Error setting icon from {icon_path}: {e}")

    if not icon_set:
        logger.warning("Could not find application icon")
        # Try to create a simple icon programmatically
        try:
            from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen
            from PyQt6.QtCore import QPoint
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(255, 255, 255, 0))
            painter = QPainter(pixmap)
            painter.setBrush(QBrush(QColor(41, 128, 185)))
            painter.setPen(QPen(QColor(41, 128, 185)))
            painter.drawRect(5, 5, 25, 54)
            painter.setBrush(QBrush(QColor(39, 174, 96)))
            painter.setPen(QPen(QColor(39, 174, 96)))
            painter.drawRect(34, 5, 25, 54)
            painter.setBrush(QBrush(QColor(52, 73, 94)))
            painter.setPen(QPen(QColor(52, 73, 94)))
            painter.drawPolygon([QPoint(25, 25), QPoint(39, 15), QPoint(39, 35)])
            painter.end()
            app.setWindowIcon(QIcon(pixmap))
            logger.info("Created fallback icon programmatically")
        except Exception as e:
            logger.error(f"Error creating fallback icon: {e}")

    # Set Fusion style which automatically adapts to light/dark mode
    ThemeService.set_theme(app)
    logger.info("Theme set to Fusion style")

    window = MainWindow()
    logger.info("Main window created")

    window.show()
    logger.info("Application window displayed")

    exit_code = app.exec()
    logger.info(f"Application exiting with code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
