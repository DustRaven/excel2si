"""
Version checker service for CSV2JSON
"""

import requests
import packaging.version as version
from functools import lru_cache
import sys
import subprocess
from pathlib import Path

from csv2json import __version__

class VersionChecker:
    GITHUB_API_URL = "https://api.github.com/repos/DustRaven/excel2si/releases/latest"

    @staticmethod
    @lru_cache(maxsize=1)
    def check_for_updates():
        """Check if a newer version is available"""
        try:
            response = requests.get(VersionChecker.GITHUB_API_URL, timeout=5)
            response.raise_for_status()
            latest = response.json()
            latest_version = latest["tag_name"].lstrip("v")
            current_version = __version__

            return {
                'update_available': version.parse(latest_version) > version.parse(current_version),
                'latest_version': latest_version,
                'current_version': current_version,
                'download_url': latest["assets"][0]["browser_download_url"] if latest["assets"] else None,
                'release_notes': latest["body"]
            }
        except Exception as e:
            return {
                'error': str(e),
                'current_version': __version__,
            }

    @staticmethod
    def is_bundled():
        """Check if running as PyInstaller bundle."""
        return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

    @staticmethod
    def perform_update(download_url):
        """
        Download and install the update.
        Returns (success, message)
        """
        if not VersionChecker.is_bundled():
            return False, "Auto-Update only supported in bundled version"

        try:
            # Download new version
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Get the executable path
            if getattr(sys, "frozen", False):
                current_exe = sys.executable
            else:
                return False, "Auto-Update only supported in bundled version"

            # Save as temporary file
            temp_path = current_exe + ".new"
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Create update batch script:
            update_script = Path(current_exe).parent / "update.bat"
            with open(update_script, "w", encoding='utf-8') as f:
                f.write('@echo off\n')
                f.write('timeout /t 1 /nobreak >nul\n')
                f.write(f'move /y "{temp_path}" "{current_exe}"\n')
                f.write(f'start "" "{current_exe}"\n')
                f.write('del "%~f0"\n')

            # Launch update script and exit
            subprocess.Popen(['cmd', '/c', str(update_script)],
                             creationflags=subprocess.DETACHED_PROCESS)
            return True, "Update downloaded, restarting application..."

        except Exception as e:
            return False, f"Update failed, {str(e)}"