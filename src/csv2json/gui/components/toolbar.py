"""
Toolbar component for the CSV2JSON converter.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import (QToolBar, QPushButton, QComboBox, QCheckBox,
                           QLabel, QWidget, QSizePolicy)
import qtawesome as qta
import os

from src.csv2json.core.logging import logger
from src.csv2json.data import get_datatype_files
from src.csv2json.data import get_datatype_path


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
        self.root_element_mapping = None
        self.setMovable(False)
        self.setFloatable(False)

        # Track application state
        self.has_file_selected = False

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
        self.status_label.setMaximumWidth(300)
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        self.status_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
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

        # Initialize button states
        self.update_button_states()

        logger.debug("Toolbar created")

    def update_button_states(self):
        """
        Update button states based on current application state.
        """
        # Convert button is enabled only when a file is selected
        self.convert_button.setEnabled(self.has_file_selected)
        logger.debug(f"Button states updated: file_selected={self.has_file_selected}")

    def set_file_selected(self, selected):
        """
        Set whether a file is selected.

        Args:
            selected (bool): Whether a file is selected
        """
        self.has_file_selected = selected
        self.update_button_states()
        logger.debug(f"File selected state updated: {selected}")

    def set_status_text(self, filename):
        """
        Set the status label text with elided filename if necessary.

        Args:
            filename (str): The filename to display
        """
        metrics = QFontMetrics(self.status_label.font())
        elided_text = metrics.elidedText(
            f"File: {filename}",
            Qt.TextElideMode.ElideMiddle,
            self.status_label.maximumWidth()
        )
        self.status_label.setText(elided_text)
        # Set full filename as tooltip
        self.status_label.setToolTip(f"File: {filename}")

    def load_root_elements(self):
        """
        Load available root elements from datatype files.
        """
        try:
            # Get available datatype files
            datatype_files = get_datatype_files()

            # Store mapping of display names to files
            self.root_element_mapping = {}

            # Extract display names and root elements
            for file_stem in datatype_files:
                dt_path = get_datatype_path(file_stem)
                if not os.path.exists(dt_path):
                    logger.warning(f"Datatype file not found: {dt_path}")
                    continue

                try:
                    with open(dt_path) as f:
                        data = eval(f.read())
                        display_name = data.get("displayName", file_stem)
                        root_element = data.get("root", file_stem)
                        self.root_element_mapping[display_name] = root_element
                except Exception as e:
                    logger.warning(f"Error reading {file_stem}: {e}")
                    display_name = file_stem
                    self.root_element_mapping[display_name] = file_stem

            # Add to combo box
            self.root_combo.clear()
            self.root_combo.addItems(sorted(self.root_element_mapping.keys()))

            logger.info(f"Loaded {len(self.root_element_mapping)} root elements")
        except Exception as e:
            logger.error(f"Error loading root elements: {e}", exc_info=True)
