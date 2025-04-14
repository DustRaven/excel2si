"""
Mapping UI components for CSV2JSON converter.
"""

from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
                           QHBoxLayout, QLabel, QFrame, QSizePolicy,
                           QHeaderView, QAbstractItemView, QPushButton, QMenu)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QDrag

from src.csv2json.core.logging import logger


class DraggableChip(QLabel):
    """
    A draggable chip widget representing an Excel header.
    """
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.update_style()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Store the original text
        self.original_text = text

    def update_style(self):
        """Update the style based on the theme mode."""
        # Minimal styling for the chip
        self.setStyleSheet("""
            QLabel {
                background-color: palette(highlight);
                color: palette(highlightedText);
                border-radius: 10px;
                padding: 5px 10px;
                margin: 2px;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        # Check if the mouse has moved far enough to start a drag
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return

        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.original_text)
        drag.setMimeData(mime_data)

        # Create a pixmap of the chip for visual feedback during drag
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        # Start the drag operation
        drag.exec(Qt.DropAction.MoveAction)


class ChipContainer(QFrame):
    """
    A container for draggable chips.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.update_style()

        # Create a flow layout for the chips
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Store the chips
        self.chips = []

    def update_style(self):
        """Update the style based on the theme mode."""
        # Minimal styling for the container
        self.setStyleSheet("""
            ChipContainer {
                min-height: 50px;
            }
        """)

    def add_chip(self, text):
        """Add a new chip to the container."""
        chip = DraggableChip(text, self)
        self.layout.addWidget(chip)
        self.chips.append(chip)
        return chip

    def clear_chips(self):
        """Remove all chips from the container."""
        for chip in self.chips:
            self.layout.removeWidget(chip)
            chip.deleteLater()
        self.chips = []


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


class MappingWidget(QWidget):
    """
    Widget for mapping Excel headers to target fields.
    """
    mapping_changed = pyqtSignal(dict)  # Signal emitted when mapping changes

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

        # Add buttons for auto-mapping and clearing
        button_layout = QHBoxLayout()

        self.auto_map_button = QPushButton("Auto-Map Fields")
        self.auto_map_button.clicked.connect(self.auto_map_fields)
        button_layout.addWidget(self.auto_map_button)

        self.clear_button = QPushButton("Clear Mapping")
        self.clear_button.clicked.connect(self.clear_mapping)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

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
        self.source_container.clear_chips()
        self.hidden_chips = {}
        for field in fields:
            chip = self.source_container.add_chip(field)
            self.hidden_chips[field] = chip

    def load_datatypes(self, datatypes_str):
        """
        Load target fields and data types from a datatypes string.

        Args:
            datatypes_str (str): String representation of datatypes dictionary
        """
        try:
            # Parse the datatypes string into a dictionary
            # We need to handle the Python type literals (str, int, etc.)
            # First, let's extract the field names from the JSON-like structure
            import re

            # Extract field names and types using regex
            pattern = r'"([^"]+)"\s*:\s*([^,\n\}]+)'  # Matches "field": type
            matches = re.findall(pattern, datatypes_str)

            if matches:
                # Create a dictionary from the matches
                datatypes_dict = {field: type_str.strip() for field, type_str in matches}

                # Load the datatypes into the mapping table
                self.mapping_table.load_datatypes(datatypes_dict)
            else:
                print("No datatypes found in the file")
        except Exception as e:
            print(f"Error loading datatypes: {e}")

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

    def auto_map_fields(self):
        """
        Automatically map fields based on name similarity.
        """
        logger.info("Starting auto-mapping of fields")

        # Get the target fields
        target_fields = []
        for row in range(self.mapping_table.rowCount()):
            target_fields.append(self.mapping_table.item(row, 0).text())
        logger.info(f"Target fields: {target_fields}")

        # Get the source fields
        source_fields = [chip.original_text for chip in self.source_container.chips]
        logger.info(f"Source fields: {source_fields}")

        # Common word variations to handle
        variations = {
            'address': ['adresse', 'addr', 'adr'],
            'street': ['strasse', 'straße', 'str'],
            'city': ['stadt', 'ort', 'place'],
            'zip': ['zipcode', 'postal', 'postcode', 'plz', 'postleitzahl', 'zip_code', 'postal_code'],
            'plz': ['zip', 'zipcode', 'postal', 'postcode', 'postleitzahl', 'zip_code', 'postal_code'],
            'name': ['nom', 'namen'],
            'first': ['vorname', 'firstname', 'first_name', 'given'],
            'last': ['nachname', 'lastname', 'last_name', 'surname', 'family'],
            'phone': ['telefon', 'tel', 'telephone', 'mobile', 'cell'],
            'email': ['e-mail', 'mail', 'e_mail'],
            'country': ['land', 'pays', 'nation'],
            'state': ['bundesland', 'province', 'region'],
            'company': ['firma', 'organization', 'organisation', 'business'],
            'date': ['datum', 'day', 'tag'],
            'number': ['nummer', 'no', 'num', 'nr'],
            'price': ['preis', 'cost', 'prix'],
            'amount': ['betrag', 'sum', 'quantity', 'menge']
        }
        logger.debug(f"Loaded {len(variations)} variation groups")

        # Create a reverse lookup for variations (case-insensitive)
        variation_lookup = {}
        for main, variants in variations.items():
            for variant in variants:
                variation_lookup[variant.lower()] = main
            variation_lookup[main.lower()] = main
        logger.debug(f"Created variation lookup with {len(variation_lookup)} entries")

        # Create a mapping based on matches
        mapping = {}
        for target in target_fields:
            # Try to find an exact match
            if target in source_fields:
                mapping[target] = target
                logger.info(f"Exact match: {target}")
                continue

            # Try to find a case-insensitive match
            target_lower = target.lower()
            exact_match_found = False

            for source in source_fields:
                if target_lower == source.lower():
                    mapping[target] = source
                    logger.info(f"Case-insensitive match: {target} -> {source}")
                    exact_match_found = True
                    break

            if exact_match_found:
                continue

            # Try to match based on word variations
            best_match = None
            best_score = 0
            logger.info(f"Trying to fuzzy match: {target}")

            # Extract the base words from target (remove _id, _name suffixes)
            target_base = target_lower
            for suffix in ['_id', '_name', '_nr', '_no', '_num', '_number']:
                if target_base.endswith(suffix):
                    target_base = target_base[:-len(suffix)]
                    logger.debug(f"Removed suffix from {target_lower} -> {target_base}")
                    break

            # Check if any part of the target matches a known variation
            target_parts = target_base.split('_')
            target_variations = set()

            for part in target_parts:
                # Add the original part
                target_variations.add(part)
                # Add any known variations (case-insensitive)
                if part.lower() in variation_lookup:
                    variation = variation_lookup[part.lower()]
                    target_variations.add(variation)
                    logger.debug(f"Found variation for '{part}': '{variation}'")

            logger.debug(f"Target variations for {target}: {target_variations}")

            for source in source_fields:
                source_lower = source.lower()
                source_base = source_lower

                # Extract the base words from source
                for suffix in ['_id', '_name', '_nr', '_no', '_num', '_number']:
                    if source_base.endswith(suffix):
                        source_base = source_base[:-len(suffix)]
                        logger.debug(f"Removed suffix from {source_lower} -> {source_base}")
                        break

                # Split source into parts
                source_parts = source_base.split('_')
                source_variations = set()

                # Special cases for common field names
                special_cases = {
                    'zip_code': ['PLZ', 'ZIP', 'PostalCode'],
                    'address': ['Adresse', 'Anschrift', 'ADRESSE'],
                    'city': ['Stadt', 'Ort', 'CITY'],
                    'country': ['Land', 'COUNTRY'],
                    'phone': ['Telefon', 'Tel', 'PHONE'],
                    'email': ['Email', 'E-Mail', 'EMAIL']
                }

                if target_lower in special_cases and source in special_cases[target_lower]:
                    logger.info(f"Special case match: {target} -> {source}")
                    best_match = source
                    best_score = 1.0
                    break

                # Check for direct match with known variations
                if target_base in variations and source.lower() in [v.lower() for v in variations[target_base]] or \
                   source_base in variations and target.lower() in [v.lower() for v in variations[source_base]]:
                    logger.info(f"Direct variation match: {target} -> {source}")
                    best_match = source
                    best_score = 0.9
                    break

                for part in source_parts:
                    # Add the original part
                    source_variations.add(part)
                    # Add any known variations (case-insensitive)
                    if part.lower() in variation_lookup:
                        variation = variation_lookup[part.lower()]
                        source_variations.add(variation)
                        logger.debug(f"Found source variation for '{part}': '{variation}'")

                # Calculate similarity score based on common variations
                common_variations = target_variations.intersection(source_variations)
                if common_variations:
                    logger.debug(f"Common variations between {target} and {source}: {common_variations}")
                    score = len(common_variations) / max(len(target_variations), len(source_variations))

                    # Boost score for longer matches
                    if len(common_variations) > 1:
                        score *= 1.5

                    logger.debug(f"Score for {target} -> {source}: {score:.2f}")

                    if score > best_score:
                        best_score = score
                        best_match = source

            # If we found a good match (score > 0.3), use it - lowered threshold for more matches
            if best_match and best_score > 0.3:
                mapping[target] = best_match
                logger.info(f"Fuzzy matched: {target} -> {best_match} (score: {best_score:.2f})")

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
        self.mapping_table.clear_mapping()
