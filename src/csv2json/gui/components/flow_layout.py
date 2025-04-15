"""
FlowLayout implementation for PyQt6.
Based on the Qt6 examples.
"""

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtWidgets import QLayout, QSizePolicy


class FlowLayout(QLayout):
    """
    A layout that arranges widgets in a flow, similar to how text flows in a paragraph.
    """
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins()
        size += QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self._item_list:
            widget = item.widget()
            style = widget.style() if widget else None
            
            # Get the spacing between widgets
            layout_spacing_x = spacing
            layout_spacing_y = spacing
            
            if style:
                layout_spacing_x = style.layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Horizontal
                )
                layout_spacing_y = style.layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Vertical
                )
            
            # Calculate the next position
            next_x = x + item.sizeHint().width() + layout_spacing_x
            
            # If we would exceed the right edge, move to the next line
            if next_x - layout_spacing_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + layout_spacing_y
                next_x = x + item.sizeHint().width() + layout_spacing_x
                line_height = 0
            
            # Place the item if not just testing
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            # Update position and line height
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()
