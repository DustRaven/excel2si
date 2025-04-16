"""
Main window for the CSV2JSON converter.
"""

import os
import locale
from pathlib import Path
from sys import version_info

from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QFileDialog,
                           QMessageBox, QApplication)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QAction

from csv2json.core.version_checker import VersionChecker
from csv2json.gui.windows.update_dialog import UpdateDialog
from csv2json.utils.icon_utils import create_fallback_icon
from csv2json.utils.path_utils import get_resource_path

# Try to import with or without 'src' prefix
try:
    from src.csv2json.core.logging import logger
    from src.csv2json.core.converter import excel_to_json
    from src.csv2json.core.file_service import FileService
    from src.csv2json.data import get_datatype_path
    from src.csv2json.gui.components.toolbar import MainToolbar
    from src.csv2json.gui.components.mapping_widget import MappingWidget
    from src.csv2json.gui.components.log_viewer import LogViewer
except ImportError:
    from csv2json.core.logging import logger
    from csv2json.core.converter import excel_to_json
    from csv2json.core.file_service import FileService
    from csv2json.data import get_datatype_path
    from csv2json.gui.components.toolbar import MainToolbar
    from csv2json.gui.components.mapping_widget import MappingWidget
    from csv2json.gui.components.log_viewer import LogViewer


class MainWindow(QMainWindow):
    """
    Main window for the CSV2JSON converter.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV2JSON Converter")
        self.setMinimumSize(800, 600)
        self.setAcceptDrops(True)  # Enable drops for the main window

        # Set application icon
        icon_path = get_resource_path('csv2json','ico')
        if icon_path:
            try:
                self.setWindowIcon(QIcon(icon_path))
                logger.debug(f"Set application icon: {icon_path}")
            except Exception as e:
                logger.error(f"Error setting icon from {icon_path}: {e}")
                self.setWindowIcon(create_fallback_icon())
        else:
            logger.warning("Could not find application icon")
            self.setWindowIcon(create_fallback_icon())

        logger.info("Initializing main window")

        # Set locale for number formatting
        try:
            locale.setlocale(locale.LC_NUMERIC, 'German_Germany.1252')
            logger.info("Set locale to German_Germany.1252")
        except locale.Error:
            logger.warning("Could not set German locale, using default")
            pass  # Use default locale if German is not available

        # Create toolbar with controls
        self.toolbar = MainToolbar(self)
        self.addToolBar(self.toolbar)

        # Connect toolbar buttons
        self.toolbar.browse_button.clicked.connect(self.browse_file)
        self.toolbar.convert_button.clicked.connect(self.convert_file)
        self.toolbar.log_button.clicked.connect(self.show_log_viewer)
        self.toolbar.root_combo.currentIndexChanged.connect(self.load_datatypes_for_mapping)
        self.toolbar.skip_rows_changed.connect(self.on_skip_rows_changed)
        logger.debug("Toolbar buttons connected")

        # Create status bar
        self.statusBar().showMessage("Ready. Drop an Excel file or use the Browse button.")

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        logger.debug("Central widget and layout created")

        # Create mapping widget
        self.mapping_widget = MappingWidget()
        self.mapping_widget.mapping_changed.connect(self.on_mapping_changed)
        main_layout.addWidget(self.mapping_widget)
        logger.debug("Mapping widget created and added to layout")

        # Store the last selected file and mapping
        self.selected_file = None
        self.field_mapping = {}

        # Initialize button states
        self.toolbar.set_file_selected(False)

        # Load datatypes for the initial root element
        self.load_datatypes_for_mapping()
        logger.info("Main window initialization complete")

        # Check for Updates in help menu
        help_menu = self.menuBar().addMenu("Help")
        check_updates_action = QAction("Check for updates", self)
        check_updates_action.triggered.connect(self.check_for_updates) # type: ignore
        help_menu.addAction(check_updates_action)

        # Check for updates on startup
        QTimer.singleShot(1000, self.check_for_updates_silent)

    def check_for_updates(self):
        """Check for updates and show dialog in any case."""
        update_status = VersionChecker.check_for_updates()
        self.show_update_dialog(update_status)

    def check_for_updates_silent(self):
        """Check for updates silently and notify only if update available."""
        update_status = VersionChecker.check_for_updates()
        if update_status.get('update_available', False):
            self.show_update_dialog(update_status)

    def show_update_dialog(self, update_status):
        """Show the update dialog."""
        dialog = UpdateDialog(update_status, self)
        dialog.exec()

    def browse_file(self):
        """
        Open a file dialog to select an Excel file.
        """
        logger.info("Opening file dialog to browse for Excel file")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "", "Excel Files (*.xlsx *.xls);;All Files (*)"
        )

        if file_path:
            logger.info(f"Selected file: {file_path}")
            self.selected_file = file_path
            self.statusBar().showMessage(f"Selected file: {Path(file_path).name}")

            # Update toolbar status label and button states
            self.toolbar.set_file_selected(True)

            # Load Excel headers for mapping
            self.load_excel_headers(file_path, self.toolbar.skip_rows_spinner.value())
        else:
            logger.info("No file selected")

    def on_skip_rows_changed(self, value):
        """
        Handle skip rows value change.

        Args:
            value (int): New skip rows value
        """
        logger.info(f"Skip rows value changed to {value}")

        # Reload headers if a file is selected
        if self.selected_file:
            self.load_excel_headers(self.selected_file, value)

    def load_excel_headers(self, excel_path, skiprows=0):
        """
        Load Excel headers for mapping.

        Args:
            excel_path (str): Path to the Excel file
            skiprows (int, optional): Number of rows to skip from the beginning of the file. Defaults to 0.
        """
        logger.info(f"Loading Excel headers from: {excel_path} (skipping {skiprows} rows)")
        try:
            # Get Excel headers
            headers = FileService.get_excel_headers(excel_path, skiprows)
            logger.info(f"Got {len(headers)} headers from Excel file")

            # Load headers into the mapping widget
            self.mapping_widget.load_source_fields(headers)
            logger.debug("Loaded source fields into mapping widget")

            # Update the field mapping
            self.field_mapping = self.mapping_widget.get_mapping()
            logger.debug(f"Updated field mapping: {self.field_mapping}")
        except Exception as e:
            logger.error(f"Error loading Excel headers: {e}", exc_info=True)
            self.statusBar().showMessage(f"Error loading Excel headers: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error loading Excel headers: {str(e)}")

    def on_mapping_changed(self, mapping):
        """
        Handle changes to the field mapping.

        Args:
            mapping (dict): Updated field mapping
        """
        self.field_mapping = mapping
        logger.debug(f"Field mapping updated: {len(mapping)} mappings")

    def convert_file(self):
        """
        Convert the selected Excel file to JSON.
        """
        if not self.selected_file:
            logger.warning("No file selected for conversion")
            QMessageBox.warning(self, "Warning", "Please select an Excel file first.")
            return

        self.process_excel(self.selected_file)

    def process_excel(self, excel_path):
        """
        Process an Excel file and convert it to JSON.

        Args:
            excel_path (str): Path to the Excel file
        """
        logger.info(f"Processing Excel file: {excel_path}")
        try:
            self.statusBar().showMessage(f"Processing {Path(excel_path).name}...")
            QApplication.processEvents()  # Update UI

            # Get selected root element display name
            display_name = self.toolbar.root_combo.currentText()

            # Get the actual root element name from the mapping
            root = self.toolbar.root_element_mapping.get(display_name, display_name)
            remove_nulls = self.toolbar.remove_nulls.isChecked()
            logger.info(f"Using root element: {root} (display: {display_name}), remove_nulls: {remove_nulls}")

            # Get datatypes file path
            datatypes_file = get_datatype_path(root)
            if not os.path.exists(datatypes_file):
                logger.warning(f"Datatypes file not found: {datatypes_file}")
                datatypes_file = None
            else:
                logger.info(f"Using datatypes file: {datatypes_file}")

            # Generate output JSON path
            json_path = FileService.get_output_path(excel_path)
            logger.info(f"Output JSON path: {json_path}")

            # Get current field mapping
            self.field_mapping = self.mapping_widget.get_mapping()
            logger.info(f"Using field mapping with {len(self.field_mapping)} entries")

            # Get skip rows value
            skiprows = self.toolbar.skip_rows_spinner.value()
            logger.info(f"Skipping {skiprows} rows")

            # Convert Excel to JSON with field mapping
            json_path = excel_to_json(
                excel_path,
                root,
                json_path,
                remove_nulls,
                datatypes_file,
                self.field_mapping,
                skiprows
            )

            logger.info(f"Conversion successful. Output file: {json_path}")
            self.statusBar().showMessage(f"Successfully converted: {Path(excel_path).name} to {Path(json_path).name}")

            # Ask if user wants to open the output file
            reply = QMessageBox.question(self, "Conversion Complete",
                                        f"File saved to {json_path}\n\nDo you want to open the output folder?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                logger.info(f"Opening output folder: {os.path.dirname(json_path)}")
                FileService.open_folder(json_path)

        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            self.statusBar().showMessage(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error processing file: {str(e)}")

    def load_datatypes_for_mapping(self):
        """
        Load datatypes for the selected root element and update the mapping widget.
        """
        # Get the selected root element display name
        display_name = self.toolbar.root_combo.currentText()

        # Get the actual root element name from the mapping
        root = self.toolbar.root_element_mapping.get(display_name, display_name)
        if not root:
            logger.warning("No root element selected")
            return

        logger.info(f"Loading datatypes for root element: {root} (display: {display_name})")

        # Get datatypes file path
        datatypes_file = get_datatype_path(root)
        if not os.path.exists(datatypes_file):
            logger.warning(f"Datatypes file not found: {datatypes_file}")
            return

        # Load datatypes
        try:
            from src.csv2json.core.converter import load_datatypes
            datatypes_str = load_datatypes(datatypes_file)
            logger.debug(f"Loaded datatypes from: {datatypes_file}")

            # Pass the raw string to the mapping widget
            self.mapping_widget.load_datatypes(datatypes_str)
            logger.info(f"Datatypes loaded for root element: {root} (display: {display_name})")
        except Exception as e:
            logger.error(f"Error loading datatypes: {e}", exc_info=True)

    def show_log_viewer(self):
        """
        Show the log viewer dialog.
        """
        logger.info("Opening log viewer")
        log_viewer = LogViewer(self)
        log_viewer.exec()
        logger.info("Log viewer closed")

    def dragEnterEvent(self, event):
        """
        Handle drag enter events.
        """
        if event.mimeData().hasUrls():
            # Check if the dragged file is an Excel file
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(('.xlsx', '.xls')):
                event.acceptProposedAction()
                logger.debug("Drag enter event accepted for Excel file")
            else:
                logger.debug("Drag enter event rejected (not an Excel file)")
        else:
            logger.debug("Drag enter event rejected (no URLs)")

    def dropEvent(self, event):
        """
        Handle drop events.
        """
        if event.mimeData().hasUrls():
            # Get the first URL (we only support one file at a time)
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()

            if file_path.lower().endswith(('.xlsx', '.xls')):
                logger.info(f"File dropped: {file_path}")
                self.selected_file = file_path
                self.statusBar().showMessage(f"Selected file: {Path(file_path).name}")

                # Update button states
                self.toolbar.set_file_selected(True)

                # Load Excel headers for mapping
                self.load_excel_headers(file_path, self.toolbar.skip_rows_spinner.value())

                event.acceptProposedAction()
            else:
                logger.warning(f"Dropped file is not an Excel file: {file_path}")
        else:
            logger.debug("Drop event rejected (no URLs)")
