"""
Data handling utilities and resources.
"""

import os
import sys
import glob
import logging

# Get logger
logger = logging.getLogger('csv2json')

# Determine if we're running in a PyInstaller bundle
def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Path to data files - handle both development and PyInstaller environments
if is_bundled():
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
    logger.info(f"Running in PyInstaller bundle. Base path: {base_path}")

    DATA_DIR = os.path.join(base_path, 'csv2json', 'data')
    if not os.path.exists(DATA_DIR):
        logger.info(f"Path not found: {DATA_DIR}")
        # Try alternative paths
        DATA_DIR = os.path.join(base_path, 'data')
        if not os.path.exists(DATA_DIR):
            logger.info(f"Path not found: {DATA_DIR}")
            DATA_DIR = base_path
            logger.info(f"Using base path: {DATA_DIR}")
        else:
            logger.info(f"Using path: {DATA_DIR}")
    else:
        logger.info(f"Using path: {DATA_DIR}")
else:
    # Normal development environment
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Running in development mode. Data directory: {DATA_DIR}")

# Also check the project root for .dt files (for development)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
logger.info(f"Project root directory: {PROJECT_ROOT}")

# Also check the executable directory for .dt files (for PyInstaller)
EXE_DIR = os.path.dirname(sys.executable) if is_bundled() else None
if EXE_DIR:
    logger.info(f"Executable directory: {EXE_DIR}")

def get_datatype_files():
    """
    Get a list of all available datatype files.

    Returns:
        list: List of datatype file names without extension
    """
    dt_files = []

    # Try multiple locations to find .dt files
    search_paths = [DATA_DIR]

    # Add project root for development
    if os.path.exists(PROJECT_ROOT):
        search_paths.append(PROJECT_ROOT)

    # Add executable directory for PyInstaller
    if EXE_DIR and os.path.exists(EXE_DIR):
        search_paths.append(EXE_DIR)
        search_paths.append(os.path.join(EXE_DIR, 'csv2json', 'data'))
        search_paths.append(os.path.join(EXE_DIR, 'data'))

    # Search all paths for .dt files
    for path in search_paths:
        try:
            if os.path.exists(path):
                # Use glob to find all .dt files in the directory
                dt_path_files = glob.glob(os.path.join(path, '*.dt'))
                logger.info(f"Found {len(dt_path_files)} .dt files in {path}: {dt_path_files}")
                # Extract filenames without extension
                dt_files.extend([os.path.basename(f)[:-3] for f in dt_path_files])
        except Exception as e:
            logger.error(f"Error searching for .dt files in {path}: {e}", exc_info=True)

    # Remove duplicates while preserving order
    unique_dt_files = []
    for f in dt_files:
        if f not in unique_dt_files:
            unique_dt_files.append(f)

    logger.info(f"Found unique .dt files: {unique_dt_files}")
    return unique_dt_files

def get_datatype_path(name):
    """
    Get the full path to a datatype file.

    Args:
        name (str): Name of the datatype file without extension

    Returns:
        str: Full path to the datatype file
    """
    # Try multiple locations to find the specific .dt file
    search_paths = [DATA_DIR]

    # Add project root for development
    if os.path.exists(PROJECT_ROOT):
        search_paths.append(PROJECT_ROOT)

    # Add executable directory for PyInstaller
    if EXE_DIR and os.path.exists(EXE_DIR):
        search_paths.append(EXE_DIR)
        search_paths.append(os.path.join(EXE_DIR, 'csv2json', 'data'))
        search_paths.append(os.path.join(EXE_DIR, 'data'))

    # Search all paths for the specific .dt file
    for path in search_paths:
        try:
            file_path = os.path.join(path, f"{name}.dt")
            if os.path.exists(file_path):
                return file_path
        except Exception as e:
            logger.error(f"Error checking for {name}.dt in {path}: {e}", exc_info=True)

    # If not found anywhere, return the default path (it will be checked for existence later)
    default_path = os.path.join(DATA_DIR, f"{name}.dt")
    logger.warning(f"Could not find {name}.dt in any search path. Using default path: {default_path}")
    return default_path
