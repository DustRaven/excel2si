"""
Theme service for the CSV2JSON converter GUI.
"""

from PyQt6.QtWidgets import QApplication

from src.csv2json.core.logging import logger


class ThemeService:
    """
    Service for managing application themes.
    """
    
    @staticmethod
    def set_theme(app):
        """
        Apply the Fusion style to the application.
        
        Args:
            app (QApplication): The application instance
        """
        app.setStyle("Fusion")
        logger.info("Applied Fusion style to application")
    
    # For backward compatibility
    set_light_theme = set_theme
    set_dark_theme = set_theme
    set_fusion_light_theme = set_theme
    set_fusion_dark_theme = set_theme
