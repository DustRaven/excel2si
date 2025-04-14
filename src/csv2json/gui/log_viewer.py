"""
Log viewer window for CSV2JSON converter.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QPushButton, QFileDialog, QLabel, QComboBox,
                           QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor

from src.csv2json.core.logging import get_logs, clear_logs, export_logs


class LogViewer(QDialog):
    """
    Dialog window for viewing application logs.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSV2JSON Log Viewer")
        self.setMinimumSize(800, 600)

        # Create layout
        layout = QVBoxLayout(self)

        # Create controls layout
        controls_layout = QHBoxLayout()

        # Add log level filter
        level_label = QLabel("Log Level:")
        controls_layout.addWidget(level_label)

        self.level_combo = QComboBox()
        self.level_combo.addItems(["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.setCurrentIndex(0)  # Default to All
        self.level_combo.currentIndexChanged.connect(self.filter_logs)
        controls_layout.addWidget(self.level_combo)

        # Add newest first checkbox
        self.newest_first_check = QCheckBox("Newest First")
        self.newest_first_check.setChecked(False)
        self.newest_first_check.stateChanged.connect(self.refresh_logs)
        controls_layout.addWidget(self.newest_first_check)

        # Add auto-refresh checkbox
        self.auto_refresh_check = QCheckBox("Auto Refresh")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_check)

        # Add spacer
        controls_layout.addStretch()

        # Add buttons
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_logs)
        controls_layout.addWidget(self.refresh_button)

        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        controls_layout.addWidget(self.clear_button)

        self.export_button = QPushButton("Export Logs")
        self.export_button.clicked.connect(self.export_logs)
        controls_layout.addWidget(self.export_button)

        layout.addLayout(controls_layout)

        # Create log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Use monospace font for better log readability
        font = QFont("Courier New")
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.log_text.setFont(font)

        layout.addWidget(self.log_text)

        # Set up auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_logs)
        self.refresh_timer.start(1000)  # Refresh every second

        # Track scroll position
        self.was_at_bottom = True

        # Initial log load
        self.refresh_logs()

    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh on/off."""
        if state == Qt.CheckState.Checked.value:
            self.refresh_timer.start(1000)
        else:
            self.refresh_timer.stop()

    def refresh_logs(self):
        """Refresh the log display."""
        logs = get_logs()

        # Apply filter if needed
        level_filter = self.level_combo.currentText()
        if level_filter != "All":
            logs = [log for log in logs if f" - {level_filter} - " in log]

        # Check if we should reverse the order (newest first)
        if self.newest_first_check.isChecked():
            logs = list(reversed(logs))

        # Update text while preserving scroll position
        scroll_bar = self.log_text.verticalScrollBar()

        # Remember if we were at the bottom before refresh
        self.was_at_bottom = scroll_bar.value() >= (scroll_bar.maximum() - 10)  # Allow some margin

        # Update the text
        self.log_text.setText("\n".join(logs))

        # Scroll to appropriate position
        if self.newest_first_check.isChecked():
            # If newest first, scroll to top
            self.log_text.moveCursor(QTextCursor.MoveOperation.Start)
        elif self.was_at_bottom or self.auto_refresh_check.isChecked():
            # If we were at the bottom or auto-refresh is on, scroll to bottom
            self.log_text.moveCursor(QTextCursor.MoveOperation.End)

    def filter_logs(self):
        """Filter logs based on selected level."""
        self.refresh_logs()

    def clear_logs(self):
        """Clear all logs."""
        clear_logs()
        self.refresh_logs()

    def export_logs(self):
        """Export logs to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "", "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            success = export_logs(file_path)
            if success:
                self.parent().statusBar().showMessage(f"Logs exported to: {file_path}")
            else:
                self.parent().statusBar().showMessage("Error exporting logs")

    def closeEvent(self, event):
        """Handle dialog close event."""
        self.refresh_timer.stop()
        event.accept()
