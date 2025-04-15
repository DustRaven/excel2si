"""
Draggable chips component for the CSV2JSON converter.
"""

from PyQt6.QtWidgets import QLabel, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag

from src.csv2json.core.logging import logger
from src.csv2json.gui.components.flow_layout import FlowLayout


class DraggableChip(QLabel):
    """
    A draggable chip widget representing an Excel header.
    """
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.update_style()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Enable word wrap for long text
        self.setWordWrap(True)

        # Set maximum width to prevent overly wide chips
        self.setMaximumWidth(200)

        # Ensure text is properly displayed with ellipsis if needed
        self.setTextFormat(Qt.TextFormat.PlainText)

        # Store the original text
        self.original_text = text

        # Set tooltip to show full text on hover
        self.setToolTip(text)

        # Adjust height based on content
        self.adjustSize()

        # Log the chip creation
        logger.debug(f"Created chip for field: {text}")

    def update_style(self):
        """Update the style based on the theme mode."""
        # Enhanced styling for the chip with better text handling
        self.setStyleSheet("""
            QLabel {
                background-color: palette(highlight);
                color: palette(highlightedText);
                border-radius: 10px;
                padding: 6px 10px;
                margin: 3px;
                min-height: 20px;
                max-height: 60px;
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
    A container for draggable chips that arranges them in a flowing layout.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.update_style()

        # Create a flow layout for the chips that wraps to the next line
        self.layout = FlowLayout(self, margin=10, spacing=5)

        # Store the chips
        self.chips = []

        # Set minimum height to ensure there's always space for chips
        self.setMinimumHeight(100)

        # Log container creation
        logger.debug("Created chip container with flow layout")

    def update_style(self):
        """Update the style based on the theme mode."""
        # Enhanced styling for the container
        self.setStyleSheet("""
            ChipContainer {
                min-height: 100px;
                border: 1px solid palette(mid);
                border-radius: 5px;
                background-color: palette(base);
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
