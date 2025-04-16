"""
Utility functions for handling application icons.
"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import QPoint

from csv2json.core.logging import logger


def create_fallback_icon() -> QIcon:
    """
    Create a simple programmatic fallback icon when the regular icon file cannot be found.

    Returns:
        QIcon: A programmatically created icon
    """
    try:
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(255, 255, 255, 0))
        painter = QPainter(pixmap)

        # Draw CSV rectangle (blue)
        painter.setBrush(QBrush(QColor(41, 128, 185)))
        painter.setPen(QPen(QColor(41, 128, 185)))
        painter.drawRect(5, 5, 25, 54)

        # Draw JSON rectangle (green)
        painter.setBrush(QBrush(QColor(39, 174, 96)))
        painter.setPen(QPen(QColor(39, 174, 96)))
        painter.drawRect(34, 5, 25, 54)

        # Draw arrow (dark gray)
        painter.setBrush(QBrush(QColor(52, 73, 94)))
        painter.setPen(QPen(QColor(52, 73, 94)))
        painter.drawPolygon([QPoint(25, 25), QPoint(39, 15), QPoint(39, 35)])

        painter.end()
        logger.info("Created fallback icon programmatically")
        return QIcon(pixmap)
    except Exception as e:
        logger.error(f"Error creating fallback icon: {e}")
        return QIcon()