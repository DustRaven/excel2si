"""
Mapping widget component for the CSV2JSON converter.
"""

import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QTableWidgetItem, QFileDialog, QMessageBox)
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtGui import QIcon
import qtawesome as qta

from src.csv2json.core.logging import logger
from src.csv2json.core.file_service import FileService
from src.csv2json.gui.components.mapping_chips import ChipContainer
from src.csv2json.gui.components.mapping_table import MappingTable
from src.csv2json.gui.services.mapping_service import MappingService


class MappingWidget(QWidget):
    """
    Widget for mapping Excel headers to target fields.
    """
    mapping_changed = pyqtSignal(dict)  # Signal emitted when mapping changes

    # Common button style
    BUTTON_STYLE = """
        QPushButton {
            padding: 6px;
        }
    """

    # Common button size and icon size
    BUTTON_SIZE = 24
    ICON_SIZE = 24

    def setup_button(self, button, icon_name=None):
        """
        Apply common settings to a button.

        Args:
            button (QPushButton): The button to set up
            icon_name (str, optional): Font Awesome icon name. Defaults to None.
        """
        # Set minimum size
        button.setMinimumSize(self.BUTTON_SIZE, self.BUTTON_SIZE)

        # Set icon size
        button.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))

        # Set icon if provided
        if icon_name:
            button.setIcon(qta.icon(icon_name))

        # Apply common style
        button.setStyleSheet(self.BUTTON_STYLE)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the layout
        layout = QVBoxLayout(self)

        # Add a label for the source fields
        source_label = QLabel("Source Fields (Excel Headers)")
        source_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(source_label)

        # Add the chip container for source fields
        self.source_container = ChipContainer()
        layout.addWidget(self.source_container)

        # Add a label for the mapping table
        mapping_label = QLabel("Field Mapping")
        mapping_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(mapping_label)

        # Add the mapping table
        self.mapping_table = MappingTable()
        self.mapping_table.mapping_changed.connect(self.on_mapping_changed)
        self.mapping_table.field_unmapped.connect(self.on_field_unmapped)
        layout.addWidget(self.mapping_table)

        # Store the hidden chips
        self.hidden_chips = {}

        # Add buttons for auto-mapping, clearing, exporting, and importing
        button_layout = QHBoxLayout()

        self.auto_map_button = QPushButton("Auto-Map Fields")
        self.setup_button(self.auto_map_button, 'fa6s.wand-magic-sparkles')
        self.auto_map_button.clicked.connect(self.auto_map_fields)
        button_layout.addWidget(self.auto_map_button)

        self.clear_button = QPushButton("Clear Mapping")
        self.setup_button(self.clear_button, 'fa6s.broom')
        self.clear_button.clicked.connect(self.clear_mapping)
        button_layout.addWidget(self.clear_button)

        self.export_button = QPushButton("Export Mapping")
        self.setup_button(self.export_button, 'fa6s.file-export')
        self.export_button.clicked.connect(self.export_mapping)
        button_layout.addWidget(self.export_button)

        self.import_button = QPushButton("Import Mapping")
        self.setup_button(self.import_button, 'fa6s.file-import')
        self.import_button.clicked.connect(self.import_mapping)
        button_layout.addWidget(self.import_button)

        layout.addLayout(button_layout)

        # Create mapping service
        self.mapping_service = MappingService()

    def update_theme(self):
        """Update the theme for all child widgets."""
        self.source_container.update_style()
        self.mapping_table.update_style()

        # Update all chips
        for chip in self.source_container.chips:
            chip.update_style()

    def load_source_fields(self, fields):
        """
        Load source fields (Excel headers) and display them as chips.

        Args:
            fields (list): List of field names
        """
        logger.info(f"Loading {len(fields)} source fields")
        self.source_container.clear_chips()
        self.hidden_chips = {}
        for field in fields:
            chip = self.source_container.add_chip(field)
            self.hidden_chips[field] = chip
        logger.debug("Source fields loaded as chips")

    def load_datatypes(self, datatypes_str):
        """
        Load target fields and data types from a datatypes string.

        Args:
            datatypes_str (str): String representation of datatypes dictionary
        """
        logger.info("Loading datatypes")
        try:
            # Extract field names and types using regex
            pattern = r'"([^"]+)"\s*:\s*([^,\n\}]+)'  # Matches "field": type
            matches = re.findall(pattern, datatypes_str)

            if matches:
                # Create a dictionary from the matches
                datatypes_dict = {field: type_str.strip() for field, type_str in matches}
                logger.info(f"Found {len(datatypes_dict)} datatypes")

                # Load the datatypes into the mapping table
                self.mapping_table.load_datatypes(datatypes_dict)
            else:
                logger.warning("No datatypes found in the file")
        except Exception as e:
            logger.error(f"Error loading datatypes: {e}", exc_info=True)

    def get_mapping(self):
        """
        Get the current field mapping.

        Returns:
            dict: Dictionary mapping target fields to source fields
        """
        return self.mapping_table.get_mapping()

    def on_mapping_changed(self, mapping):
        """
        Handle changes to the field mapping.

        Args:
            mapping (dict): Updated field mapping
        """
        # Hide chips that are mapped
        for source_field in mapping.values():
            if source_field in self.hidden_chips and self.hidden_chips[source_field] is not None:
                self.hidden_chips[source_field].setVisible(False)
                logger.debug(f"Hidden chip for mapped field: {source_field}")

        self.mapping_changed.emit(mapping)

    def on_field_unmapped(self, source_field):
        """
        Handle when a field is unmapped (removed from the mapping table).

        Args:
            source_field (str): The source field that was unmapped
        """
        # Show the chip again
        if source_field in self.hidden_chips and self.hidden_chips[source_field] is not None:
            self.hidden_chips[source_field].setVisible(True)
            logger.debug(f"Showing chip for unmapped field: {source_field}")

    def auto_map_fields(self):
        """
        Automatically map fields based on name similarity.
        """
        logger.info("Starting auto-mapping of fields")

        # Get the target fields
        target_fields = []
        for row in range(self.mapping_table.rowCount()):
            target_fields.append(self.mapping_table.item(row, 0).text())

        # Get the source fields
        source_fields = [chip.original_text for chip in self.source_container.chips]

        # Use the mapping service to auto-map fields
        mapping = self.mapping_service.auto_map_fields(target_fields, source_fields)

        # Update the mapping table
        logger.info(f"Applying {len(mapping)} field mappings to the table")
        for target, source in mapping.items():
            for row in range(self.mapping_table.rowCount()):
                if self.mapping_table.item(row, 0).text() == target:
                    source_item = QTableWidgetItem(source)
                    # No custom background color - use default
                    self.mapping_table.setItem(row, 2, source_item)
                    break

        # Update the mapping in the table
        self.mapping_table.field_mapping = mapping

        # Emit the mapping changed signal
        self.mapping_changed.emit(mapping)
        logger.info("Mapping changed signal emitted")

        # Hide the mapped chips
        for source_field in mapping.values():
            if source_field in self.hidden_chips and self.hidden_chips[source_field] is not None:
                self.hidden_chips[source_field].setVisible(False)
                logger.debug(f"Hidden chip for mapped field: {source_field}")

        logger.info("Auto-mapping completed successfully")

    def clear_mapping(self):
        """
        Clear the current mapping.
        """
        logger.info("Clearing mapping")
        self.mapping_table.clear_mapping()

    def get_mapping(self):
        """
        Get the current field mapping.

        Returns:
            dict: Dictionary mapping target fields to source fields
        """
        return self.mapping_table.get_mapping()

    def set_mapping(self, mapping):
        """
        Set the field mapping.

        Args:
            mapping (dict): Dictionary mapping target fields to source fields
        """
        logger.info(f"Setting mapping with {len(mapping)} entries")

        # Clear the current mapping
        self.clear_mapping()

        # Update the mapping table
        for target, source in mapping.items():
            for row in range(self.mapping_table.rowCount()):
                if self.mapping_table.item(row, 0).text() == target:
                    source_item = QTableWidgetItem(source)
                    self.mapping_table.setItem(row, 2, source_item)
                    break

        # Update the mapping in the table
        self.mapping_table.field_mapping = mapping

        # Emit the mapping changed signal
        self.mapping_changed.emit(mapping)

        # Hide the mapped chips
        for source_field in mapping.values():
            if source_field in self.hidden_chips and self.hidden_chips[source_field] is not None:
                self.hidden_chips[source_field].setVisible(False)

        logger.info("Mapping set successfully")

    def export_mapping(self):
        """
        Export the current mapping to a file.
        """
        logger.info("Exporting mapping")

        # Get the current mapping
        mapping = self.get_mapping()

        if not mapping:
            QMessageBox.warning(self, "Export Mapping", "No mapping to export.")
            logger.warning("No mapping to export")
            return

        # Ask for a file to save the mapping
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Mapping",
            "",
            "Mapping Files (*.json);;All Files (*)"
        )

        if not file_path:
            logger.info("Export mapping cancelled")
            return

        # Add .json extension if not present
        if not file_path.lower().endswith('.json'):
            file_path += '.json'

        # Save the mapping
        if FileService.save_mapping(mapping, file_path):
            QMessageBox.information(
                self,
                "Export Mapping",
                f"Mapping exported successfully to {file_path}"
            )
            logger.info(f"Mapping exported successfully to {file_path}")
        else:
            QMessageBox.critical(
                self,
                "Export Mapping",
                f"Failed to export mapping to {file_path}"
            )
            logger.error(f"Failed to export mapping to {file_path}")

    def import_mapping(self):
        """
        Import a mapping from a file.
        """
        logger.info("Importing mapping")

        # Ask for a file to load the mapping
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Mapping",
            "",
            "Mapping Files (*.json);;All Files (*)"
        )

        if not file_path:
            logger.info("Import mapping cancelled")
            return

        # Load the mapping
        mapping = FileService.load_mapping(file_path)

        if mapping is None:
            QMessageBox.critical(
                self,
                "Import Mapping",
                f"Failed to import mapping from {file_path}"
            )
            logger.error(f"Failed to import mapping from {file_path}")
            return

        # Set the mapping
        self.set_mapping(mapping)

        QMessageBox.information(
            self,
            "Import Mapping",
            f"Mapping imported successfully from {file_path}"
        )
        logger.info(f"Mapping imported successfully from {file_path}")
