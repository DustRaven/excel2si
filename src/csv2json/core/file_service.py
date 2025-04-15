"""
File service for the CSV2JSON converter.
"""

import os
import json
from pathlib import Path
import pandas as pd

from src.csv2json.core.logging import logger


class FileService:
    """
    Service for handling file operations.
    """

    @staticmethod
    def get_excel_headers(excel_path, skiprows=0):
        """
        Get the column headers from an Excel file.

        Args:
            excel_path (str): Path to the Excel file
            skiprows (int, optional): Number of rows to skip from the beginning of the file. Defaults to 0.

        Returns:
            list: List of column headers
        """
        logger.info(f"Getting headers from Excel file: {excel_path} (skipping {skiprows} rows)")
        try:
            df = pd.read_excel(excel_path, skiprows=skiprows)
            headers = list(df.columns)
            logger.info(f"Found {len(headers)} headers: {headers[:10]}...")
            return headers
        except Exception as e:
            logger.error(f"Error reading Excel headers: {e}")
            return []

    @staticmethod
    def get_output_path(input_path, extension='.json'):
        """
        Generate an output path based on an input path.

        Args:
            input_path (str): Path to the input file
            extension (str, optional): Extension for the output file. Defaults to '.json'.

        Returns:
            str: Path to the output file
        """
        return str(Path(input_path).with_suffix(extension))

    @staticmethod
    def open_folder(folder_path):
        """
        Open a folder in the file explorer.

        Args:
            folder_path (str): Path to the folder
        """
        logger.info(f"Opening folder: {folder_path}")
        try:
            os.startfile(os.path.dirname(folder_path))
        except Exception as e:
            logger.error(f"Error opening folder: {e}")

    @staticmethod
    def save_mapping(mapping, file_path):
        """
        Save a field mapping to a JSON file.

        Args:
            mapping (dict): Dictionary mapping target fields to source fields
            file_path (str): Path to save the mapping file

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Saving mapping to file: {file_path}")
        try:
            # Create a dictionary with metadata and the mapping
            data = {
                "version": "1.0",
                "type": "csv2json_mapping",
                "mapping": mapping
            }

            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

            # Write the mapping to a JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

            logger.info(f"Mapping saved successfully with {len(mapping)} entries")
            return True
        except Exception as e:
            logger.error(f"Error saving mapping: {e}", exc_info=True)
            return False

    @staticmethod
    def load_mapping(file_path):
        """
        Load a field mapping from a JSON file.

        Args:
            file_path (str): Path to the mapping file

        Returns:
            dict: Dictionary mapping target fields to source fields, or None if error
        """
        logger.info(f"Loading mapping from file: {file_path}")
        try:
            # Read the mapping from a JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate the file format
            if not isinstance(data, dict) or "mapping" not in data:
                logger.error(f"Invalid mapping file format: {file_path}")
                return None

            # Extract the mapping
            mapping = data["mapping"]
            logger.info(f"Mapping loaded successfully with {len(mapping)} entries")
            return mapping
        except Exception as e:
            logger.error(f"Error loading mapping: {e}", exc_info=True)
            return None
