"""
Theme management for the CSV2JSON converter GUI using Qt's built-in Fusion style.
"""

from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """
    Minimal theme manager that uses Qt's built-in Fusion style.
    The Fusion style automatically adapts to light and dark modes.
    """
    
    @staticmethod
    def set_theme(app):
        """
        Apply the Fusion style to the application.
        
        Args:
            app (QApplication): The application instance
        """
        app.setStyle("Fusion")
    
    # For backward compatibility
    set_light_theme = set_theme
    set_dark_theme = set_theme
    set_fusion_light_theme = set_theme
    set_fusion_dark_theme = set_theme
