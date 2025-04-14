"""
Draggable chips component for the CSV2JSON converter.
"""

from PyQt6.QtWidgets import QLabel, QFrame, QHBoxLayout, QSizePolicy
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
