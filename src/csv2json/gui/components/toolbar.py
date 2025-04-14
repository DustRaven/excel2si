"""
Toolbar component for the CSV2JSON converter.
"""

from PyQt6.QtWidgets import (QToolBar, QPushButton, QComboBox, QCheckBox,
                           QLabel, QWidget, QSizePolicy)
from PyQt6.QtGui import QIcon
# Use qtawesome instead of pytablericons
import qtawesome as qta

from src.csv2json.core.logging import logger
from src.csv2json.data import get_datatype_files


class MainToolbar(QToolBar):
    """
    Main toolbar for the CSV2JSON converter.
    """
    # Common button style
    BUTTON_STYLE = """
        QPushButton {
            padding: 6px;
        }
    """

    # Common button size and icon size
    BUTTON_SIZE = 24
    ICON_SIZE = 24

    def setup_button(self, button, icon_name=None, tooltip=None):
        """
        Apply common settings to a button.

        Args:
            button (QPushButton): The button to set up
            icon_name (str, optional): Font Awesome icon name. Defaults to None.
            tooltip (str, optional): Tooltip text. Defaults to None.
        """
        # Set minimum size
        button.setMinimumSize(self.BUTTON_SIZE, self.BUTTON_SIZE)

        # Set icon if provided
        if icon_name:
            button.setIcon(qta.icon(icon_name))

        # Set tooltip if provided
        if tooltip:
            button.setToolTip(tooltip)

        # Apply common style
        button.setStyleSheet(self.BUTTON_STYLE)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)

        # Set icon size to 24x24 pixels for sharper icons
        from PyQt6.QtCore import QSize
        self.setIconSize(QSize(24, 24))

        # Create the root element selector
        root_label = QLabel("Root Element:")
        self.addWidget(root_label)

        self.root_combo = QComboBox()
        self.root_combo.setMinimumWidth(150)
        self.load_root_elements()
        self.addWidget(self.root_combo)

        # Add remove nulls checkbox
        self.remove_nulls = QCheckBox("Remove Nulls")
        self.addWidget(self.remove_nulls)

        # Add browse button with icon
        browse_btn = QPushButton()
        self.setup_button(browse_btn, 'fa6s.folder-open', "Browse for Excel File")
        self.browse_button = browse_btn
        self.addWidget(browse_btn)

        # Add convert button with icon
        convert_btn = QPushButton()
        self.setup_button(convert_btn, 'fa6s.file-export', "Convert to JSON")
        self.convert_button = convert_btn
        self.addWidget(convert_btn)

        # Add status label
        self.status_label = QLabel("No file selected")
        self.addWidget(self.status_label)

        # Add spacer to push items to the left and log button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        # Add log viewer button with icon (on the far right)
        log_btn = QPushButton()
        self.setup_button(log_btn, 'fa6s.file-lines', "View Logs")
        self.log_button = log_btn
        self.addWidget(log_btn)

        logger.debug("Toolbar created")

    def load_root_elements(self):
        """
        Load available root elements from datatype files.
        """
        try:
            # Get available datatype files
            datatype_files = get_datatype_files()

            # Extract root element names (file names without extension)
            root_elements = []
            for file in datatype_files:
                # Handle both Path objects and strings
                if hasattr(file, 'stem'):
                    root_elements.append(file.stem)
                else:
                    # If it's a string, extract the filename without extension
                    import os
                    root_elements.append(os.path.splitext(os.path.basename(file))[0])

            # Add to combo box
            self.root_combo.clear()
            self.root_combo.addItems(root_elements)

            logger.info(f"Loaded {len(root_elements)} root elements")
        except Exception as e:
            logger.error(f"Error loading root elements: {e}", exc_info=True)
