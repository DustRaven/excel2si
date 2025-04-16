"""
Main entry point for the CSV2JSON converter GUI.
"""

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from csv2json.utils.icon_utils import create_fallback_icon
from csv2json.utils.path_utils import get_resource_path

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

    # Set application icon
    icon_path = get_resource_path('csv2json', 'ico')
    if icon_path:
        try:
            app.setWindowIcon(QIcon(icon_path))
            logger.debug(f"Set application icon: {icon_path}")
        except Exception as e:
            logger.error(f"Error setting application icon from {icon_path}: {e}")
            app.setWindowIcon(create_fallback_icon())
    else:
        logger.warning("Could not find application icon")
        app.setWindowIcon(create_fallback_icon())


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
