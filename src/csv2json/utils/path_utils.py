import os
import sys
from pathlib import Path
from typing import Optional


def is_bundled() -> bool:
    """Check if running as PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def get_bundle_path() -> Optional[str]:
    """
    Get the PyInstaller bundle base path.
    Returns None if not running in a bundle.
    """
    # pylint: disable=protected-access
    return sys._MEIPASS if is_bundled() else None

def get_executable_dir() -> str:
    """Get the executable directory."""
    if is_bundled():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(resource_name: str, resource_type: str) -> Optional[str]:
    """
    Get the path to a resource file, checking multiple possible locations.

    Args:
        resource_name: The name of the resource file (e.g. 'icon')
        resource_type: The type of the resource file (e.g. 'ico', 'png' etc.)

    Returns:
        Full path to the resource file if found, None otherwise.
    """
    paths_to_check = []

    if is_bundled():
        base_path = get_bundle_path()
        if base_path:
            paths_to_check.extend([
                os.path.join(base_path, "csv2json", "resources", f"{resource_name}.{resource_type}"),
                os.path.join(base_path, "resources", f"{resource_name}.{resource_type}"),
                os.path.join(base_path, f"{resource_name}.{resource_type}"),
                os.path.join(get_executable_dir(), f"{resource_name}.{resource_type}"),
                os.path.join(get_executable_dir(), "csv2json", "resources", f"{resource_name}.{resource_type}"),
            ])
    else:
        # Development paths
        project_root = Path(__file__).parent.parent.parent
        paths_to_check.extend([
            project_root / "resources" / f"{resource_name}.{resource_type}",
            project_root / "csv2json" / "resources" / f"{resource_name}.{resource_type}",
        ])

    # Common paths
    paths_to_check.extend([
        os.path.join(os.getcwd(), f"{resource_name}.{resource_type}"),
        os.path.join(os.getcwd(), "resources", f"{resource_name}.{resource_type}"),
        os.path.join(os.getcwd(), "csv2json", "resources", f"{resource_name}.{resource_type}"),
    ])

    for path in paths_to_check:
        if os.path.exists(path):
            return path

    return None