"""
Main window for the CSV2JSON converter.
"""

import os
import sys
import locale
from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QFileDialog,
                           QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

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
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "csv2json.ico"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources", "csv2json.ico"),
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
                    self.setWindowIcon(QIcon(icon_path))
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
                self.setWindowIcon(QIcon(pixmap))
                logger.info("Created fallback icon programmatically")
            except Exception as e:
                logger.error(f"Error creating fallback icon: {e}")

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
            self.toolbar.status_label.setText(f"File: {Path(file_path).name}")
            self.toolbar.set_file_selected(True)

            # Load Excel headers for mapping
            self.load_excel_headers(file_path)
        else:
            logger.info("No file selected")

    def load_excel_headers(self, excel_path):
        """
        Load Excel headers for mapping.

        Args:
            excel_path (str): Path to the Excel file
        """
        logger.info(f"Loading Excel headers from: {excel_path}")
        try:
            # Get Excel headers
            headers = FileService.get_excel_headers(excel_path)
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

            # Get selected root element
            root = self.toolbar.root_combo.currentText()
            remove_nulls = self.toolbar.remove_nulls.isChecked()
            logger.info(f"Using root element: {root}, remove_nulls: {remove_nulls}")

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

            # Convert Excel to JSON with field mapping
            json_path = excel_to_json(
                excel_path,
                root,
                json_path,
                remove_nulls,
                datatypes_file,
                self.field_mapping
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

    def load_datatypes_for_mapping(self, index=None):
        """
        Load datatypes for the selected root element and update the mapping widget.

        Args:
            index (int, optional): Index of the selected root element. Defaults to None.
        """
        # Get the selected root element
        root = self.toolbar.root_combo.currentText()
        if not root:
            logger.warning("No root element selected")
            return

        logger.info(f"Loading datatypes for root element: {root}")

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
            logger.info(f"Datatypes loaded for root element: {root}")
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

                # Update toolbar status label and button states
                self.toolbar.status_label.setText(f"File: {Path(file_path).name}")
                self.toolbar.set_file_selected(True)

                # Load Excel headers for mapping
                self.load_excel_headers(file_path)

                event.acceptProposedAction()
            else:
                logger.warning(f"Dropped file is not an Excel file: {file_path}")
        else:
            logger.debug("Drop event rejected (no URLs)")
