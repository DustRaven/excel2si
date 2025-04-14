"""
Mapping table component for the CSV2JSON converter.
"""

from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                           QAbstractItemView, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal

from src.csv2json.core.logging import logger


class MappingTable(QTableWidget):
    """
    A table widget for mapping Excel headers to target fields.
    """
    mapping_changed = pyqtSignal(dict)  # Signal emitted when mapping changes
    field_unmapped = pyqtSignal(str)  # Signal emitted when a field is unmapped

    def __init__(self, parent=None):
        super().__init__(0, 3, parent)  # 3 columns: Target Field, Data Type, Source Field
        self.setAcceptDrops(True)
        self.update_style()

        # Set up the table
        self.setHorizontalHeaderLabels(["Target Field", "Data Type", "Source Field"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Hide the vertical header (row numbers)
        self.verticalHeader().setVisible(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Store the mapping
        self.field_mapping = {}

    def update_style(self):
        """Update the style based on the theme mode."""
        # Remove all custom styling and let Fusion handle it
        self.setStyleSheet("")

        # Clear any custom background colors from cells
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    item.setData(Qt.ItemDataRole.BackgroundRole, None)
                    item.setData(Qt.ItemDataRole.ForegroundRole, None)

    def load_datatypes(self, datatypes_dict):
        """
        Load target fields and data types from a datatypes dictionary.

        Args:
            datatypes_dict (dict): Dictionary mapping field names to data types
        """
        self.clear()
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["Target Field", "Data Type", "Source Field"])

        # Reset the mapping
        self.field_mapping = {}

        # Add rows for each field
        for i, (field, dtype) in enumerate(datatypes_dict.items()):
            self.insertRow(i)

            # Target field
            field_item = QTableWidgetItem(field)
            self.setItem(i, 0, field_item)

            # Data type
            dtype_item = QTableWidgetItem(str(dtype))
            self.setItem(i, 1, dtype_item)

            # Source field (empty initially)
            source_item = QTableWidgetItem("")
            # Let the Fusion style handle the background color
            self.setItem(i, 2, source_item)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def show_context_menu(self, position):
        """
        Show context menu for the table.

        Args:
            position (QPoint): Position where the context menu was requested
        """
        row = self.rowAt(position.y())
        if row >= 0:
            source_item = self.item(row, 2)
            if source_item and source_item.text():
                # Only show context menu for mapped fields
                target_field = self.item(row, 0).text()

                menu = QMenu(self)
                remove_action = menu.addAction("Remove Mapping")
                action = menu.exec(self.mapToGlobal(position))

                if action == remove_action:
                    # Clear the source field cell
                    source_field = source_item.text()
                    empty_item = QTableWidgetItem("")
                    # No custom background color - use default
                    self.setItem(row, 2, empty_item)

                    # Remove from mapping
                    if target_field in self.field_mapping:
                        del self.field_mapping[target_field]

                    # Emit signals
                    self.mapping_changed.emit(self.field_mapping)
                    self.field_unmapped.emit(source_field)

    def dropEvent(self, event):
        if event.mimeData().hasText():
            # Get the source field from the drag event
            source_field = event.mimeData().text()

            # Get the row where the drop occurred
            # Convert float to int for rowAt
            y_pos = int(event.position().y())
            row = self.rowAt(y_pos)
            if row >= 0:
                # Get the target field
                target_field = self.item(row, 0).text()

                # Check if this cell already has a mapping
                old_source_field = None
                old_item = self.item(row, 2)
                if old_item and old_item.text():
                    old_source_field = old_item.text()

                # Update the source field cell
                source_item = QTableWidgetItem(source_field)
                # No custom styling - let Fusion handle it
                self.setItem(row, 2, source_item)

                # Update the mapping
                self.field_mapping[target_field] = source_field

                # Emit the mapping changed signal with the old source field
                # so it can be restored if needed
                self.mapping_changed.emit(self.field_mapping)

                # If there was a previous mapping, emit the unmapped signal for it
                if old_source_field:
                    self.field_unmapped.emit(old_source_field)

            event.accept()
        else:
            event.ignore()

    def get_mapping(self):
        """
        Get the current field mapping.

        Returns:
            dict: Dictionary mapping target fields to source fields
        """
        return self.field_mapping

    def clear_mapping(self):
        """Clear the current mapping."""
        # Get all source fields before clearing
        old_source_fields = list(self.field_mapping.values())

        # Clear the source field cells
        for row in range(self.rowCount()):
            source_item = QTableWidgetItem("")
            # Let the Fusion style handle the background color
            self.setItem(row, 2, source_item)

        # Reset the mapping
        self.field_mapping = {}

        # Emit the mapping changed signal
        self.mapping_changed.emit(self.field_mapping)

        # Emit unmapped signals for all old source fields
        for source_field in old_source_fields:
            self.field_unmapped.emit(source_field)
