"""
Update dialog for CSV2JSON
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QTextEdit, QProgressBar)

class UpdateDialog(QDialog):
    def __init__(self, update_status, parent=None):
        super().__init__(parent)
        self.version_info = update_status
        self.setWindowTitle("Software Update")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Version information
        if 'error' in update_status:
            layout.addWidget(QLabel(f"Error checking for updates:\n{update_status['error']}"))
            layout.addWidget(QLabel(f"Current version: {update_status['current_version']}"))
        else:
            if update_status['update_available']:
                layout.addWidget(QLabel(
                    f"Update available!\n\n"
                    f"Current version: {update_status['current_version']}\n"
                    f"Latest version: {update_status['latest_version']}"
                ))

                # Release notes
                if update_status['release_notes']:
                    layout.addWidget(QLabel("Release notes:"))
                    notes = QTextEdit()
                    notes.setReadOnly(True)
                    notes.setMarkdown(update_status['release_notes'])
                    notes.setMaximumHeight(200)
                    layout.addWidget(notes)

                # Update button
                self.update_button = QPushButton("Update")
                self.update_button.clicked.connect(self.start_update) # type: ignore
                layout.addWidget(self.update_button)

                # Progress bar (hidden initially)
                self.progress_bar = QProgressBar()
                self.progress_bar.hide()
                layout.addWidget(self.progress_bar)
            else:
                layout.addWidget(QLabel("You have the latest version!"))
                layout.addWidget(QLabel(f"Current version: {update_status['current_version']}"))

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept) # type: ignore
        layout.addWidget(close_button)

    def start_update(self):
        """Start the update process."""
        from csv2json.core.version_checker import VersionChecker

        self.update_button.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)

        success, message = VersionChecker.perform_update(self.version_info['download_url'])

        if success:
            QLabel(message).show()
            self.accept()
        else:
            self.update_button.setEnabled(True)
            self.progress_bar.hide()
            QLabel(f"Update failed: {message}").show()