"""
Toolbar component for the CSV2JSON converter.
"""

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (QToolBar, QPushButton, QComboBox, QCheckBox,
                           QLabel, QWidget, QSizePolicy, QSpinBox)
from PyQt6.QtGui import QFontMetrics
import qtawesome as qta

from src.csv2json.core.logging import logger
from src.csv2json.data import get_datatype_files, get_datatype_info


class MainToolbar(QToolBar):
    """
    Main toolbar for the CSV2JSON converter.
    """
    # Signal emitted when skip rows value changes
    skip_rows_changed = pyqtSignal(int)
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

        # Track application state
        self.has_file_selected = False

        # Set icon size to 24x24 pixels for sharper icons
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

        # Add skip rows spinner
        skip_rows_label = QLabel("Skip Rows:")
        self.addWidget(skip_rows_label)

        self.skip_rows_spinner = QSpinBox()
        self.skip_rows_spinner.setMinimum(0)
        self.skip_rows_spinner.setMaximum(100)  # Reasonable maximum
        self.skip_rows_spinner.setValue(0)
        self.skip_rows_spinner.setToolTip("Number of rows to skip from the beginning of the file")
        self.skip_rows_spinner.valueChanged.connect(self.on_skip_rows_changed)
        self.addWidget(self.skip_rows_spinner)

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

    def on_skip_rows_changed(self, value):
        """
        Handle skip rows value change.

        Args:
            value (int): New skip rows value
        """
        logger.debug(f"Skip rows value changed to {value}")
        self.skip_rows_changed.emit(value)

    def load_root_elements(self):
        """
        Load available root elements from datatype files.
        """
        try:
            # Get available datatype files
            datatype_files = get_datatype_files()

            # Create a mapping of display names to root element names
            self.root_element_mapping = {}

            for file_path in datatype_files:
                # Get datatype info from the file
                info = get_datatype_info(file_path)

                # Extract the root element name (filename without extension)
                from pathlib import Path
                file_name = Path(file_path).stem

                # If it's a _schema file, extract the base name
                if file_name.endswith('_schema'):
                    file_name = file_name[:-7]  # Remove '_schema' suffix

                # Use displayName if available, otherwise use the file name
                display_name = info.get('displayName', file_name)

                # Use root if available, otherwise use the file name
                root_name = info.get('root', file_name)

                # Add to mapping
                self.root_element_mapping[display_name] = root_name

                logger.debug(f"Added root element mapping: {display_name} -> {root_name}")

            # Add to combo box
            self.root_combo.clear()
            self.root_combo.addItems(sorted(self.root_element_mapping.keys()))

            logger.info(f"Loaded {len(self.root_element_mapping)} root elements")
        except Exception as e:
            logger.error(f"Error loading root elements: {e}", exc_info=True)
