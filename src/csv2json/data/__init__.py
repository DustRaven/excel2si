"""
Data handling utilities and resources.
"""

import os
import sys
import glob
import logging
import yaml
from pathlib import Path

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
        list: List of datatype file paths
    """
    dt_files = []

    # Try multiple locations to find schema files
    search_paths = [DATA_DIR]

    # Add project root for development
    if os.path.exists(PROJECT_ROOT):
        search_paths.append(PROJECT_ROOT)

    # Add executable directory for PyInstaller
    if EXE_DIR and os.path.exists(EXE_DIR):
        search_paths.append(EXE_DIR)
        search_paths.append(os.path.join(EXE_DIR, 'csv2json', 'data'))
        search_paths.append(os.path.join(EXE_DIR, 'data'))

    # Search all paths for schema files (.dt, .yaml, .yml)
    for path in search_paths:
        try:
            if os.path.exists(path):
                # Use glob to find all schema files in the directory
                dt_path_files = glob.glob(os.path.join(path, '*.dt'))
                yaml_path_files = glob.glob(os.path.join(path, '*.yaml'))
                yml_path_files = glob.glob(os.path.join(path, '*.yml'))

                # Combine all file types
                all_files = dt_path_files + yaml_path_files + yml_path_files

                logger.info(f"Found {len(all_files)} schema files in {path}: {all_files}")
                # Add full paths to the list
                dt_files.extend(all_files)
        except Exception as e:
            logger.error(f"Error searching for schema files in {path}: {e}", exc_info=True)

    # Remove duplicates while preserving order
    unique_dt_files = []
    seen_names = set()
    for f in dt_files:
        # Get the root name (without path or extension)
        file_path = Path(f)
        name = file_path.stem

        if name not in seen_names:
            seen_names.add(name)
            unique_dt_files.append(f)

    logger.info(f"Found {len(unique_dt_files)} unique schema files")
    return unique_dt_files

def get_datatype_info(file_path):
    """
    Get information from a datatype file.

    Args:
        file_path (str): Path to the datatype file

    Returns:
        dict: Dictionary with datatype information
    """
    try:
        path = Path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Try to parse as YAML first (more secure)
            try:
                data = yaml.safe_load(content)
            except Exception as yaml_error:
                logger.debug(f"Could not parse as YAML: {yaml_error}")
                # Fall back to eval for legacy format (less secure)
                try:
                    data = eval(content)
                except Exception as eval_error:
                    logger.error(f"Could not parse file content: {eval_error}")
                    return {}
            return data
    except Exception as e:
        logger.error(f"Error reading datatype file {file_path}: {e}", exc_info=True)
        return {}

def get_datatype_path(name):
    """
    Get the full path to a datatype file.

    Args:
        name (str): Name of the datatype file without extension

    Returns:
        str: Full path to the datatype file
    """
    # Try multiple locations to find the schema file
    search_paths = [DATA_DIR]

    # Add project root for development
    if os.path.exists(PROJECT_ROOT):
        search_paths.append(PROJECT_ROOT)

    # Add executable directory for PyInstaller
    if EXE_DIR and os.path.exists(EXE_DIR):
        search_paths.append(EXE_DIR)
        search_paths.append(os.path.join(EXE_DIR, 'csv2json', 'data'))
        search_paths.append(os.path.join(EXE_DIR, 'data'))

    # Search all paths for the schema file in different formats
    for path in search_paths:
        try:
            # Check for .dt files first (preferred format)
            dt_path = os.path.join(path, f"{name}.dt")
            if os.path.exists(dt_path):
                return dt_path

            # Then check for YAML files
            yaml_path = os.path.join(path, f"{name}.yaml")
            if os.path.exists(yaml_path):
                return yaml_path

            yml_path = os.path.join(path, f"{name}.yml")
            if os.path.exists(yml_path):
                return yml_path
        except Exception as e:
            logger.error(f"Error checking for {name} schema files in {path}: {e}", exc_info=True)

    # If not found anywhere, return the default path (it will be checked for existence later)
    default_path = os.path.join(DATA_DIR, f"{name}.dt")
    logger.warning(f"Could not find schema file for {name} in any search path. Using default path: {default_path}")
    return default_path
