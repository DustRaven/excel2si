"""
Core conversion functionality for CSV to JSON.
"""

import json
import io
import os
import pandas as pd
import yaml
from pathlib import Path

from src.csv2json.core.logging import logger


def unflatten_dic(dic):
    """
    Convert flat dictionary with dot notation keys to nested dictionary.

    Args:
        dic (dict): Dictionary to unflatten
    """
    for k, v in list(dic.items()):
        subkeys = k.split('.')
        if len(subkeys) > 1:
            dic.setdefault(subkeys[0], dict())
            dic[subkeys[0]].update({"".join(subkeys[1:]): v})
            unflatten_dic(dic[subkeys[0]])
            del (dic[k])


def merge_lists(dic, remove_nulls):
    """
    Process dictionary to handle lists and null values.

    Args:
        dic (dict): Dictionary to process
        remove_nulls (bool): Whether to remove null values
    """
    for k, v in list(dic.items()):
        if pd.isnull(v):
            if remove_nulls:
                del dic[k]
            else:
                dic[k] = None
        if isinstance(v, dict):
            keys = list(v.keys())
            values = list(v.values())
            if all(isinstance(l, list) and len(l) == len(values[0]) for l in values):
                dic[k] = []
                val_tuple = set(zip(*values))  # removing duplicates with set()
                for t in val_tuple:
                    dic[k].append({subkey: t[i] for i, subkey in enumerate(keys)})
            else:
                merge_lists(v, remove_nulls)
        elif isinstance(v, list):
            dic[k] = list(set(v))  # removing list duplicates


def load_datatypes(file):
    """
    Load datatypes from a file.

    Args:
        file (str): Path to the datatypes file

    Returns:
        dict: Dictionary of datatypes
    """
    logger.info(f"Loading datatypes from: {file}")
    try:
        file_path = Path(file)
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

            # Try to parse as YAML first (more secure)
            try:
                data = yaml.safe_load(content)
            except Exception as yaml_error:
                logger.debug(f"Could not parse as YAML: {yaml_error}")
                # Fall back to eval for legacy format (less secure)
                try:
                    data = eval(content)

                    # Convert Python types to strings for consistent handling
                    if isinstance(data, dict) and 'fields' in data and isinstance(data['fields'], dict):
                        for key, value in data['fields'].items():
                            if isinstance(value, type):
                                data['fields'][key] = value.__name__
                except Exception as eval_error:
                    logger.error(f"Could not parse file content: {eval_error}")
                    raise

            # Extract fields from the data structure
            if isinstance(data, dict) and 'fields' in data:
                datatypes = data['fields']
            else:
                datatypes = data

            # Safely log a preview of the datatypes
            if isinstance(datatypes, dict):
                preview = str(list(datatypes.keys())[:10])
                logger.debug(f"Loaded datatypes with keys: {preview}...")
            elif isinstance(datatypes, list):
                preview = str(datatypes[:10])
                logger.debug(f"Loaded datatypes (list): {preview}...")
            else:
                logger.debug(f"Loaded datatypes of type: {type(datatypes)}")

            return datatypes
    except Exception as e:
        logger.error(f"Error loading datatypes: {e}")
        raise


def excel_to_json(excel_path, root_element, output_path=None, remove_nulls=False, datatypes_file=None, field_mapping=None, skiprows=0):
    """
    Convert Excel file to JSON.

    Args:
        excel_path (str): Path to the Excel file
        root_element (str): Root element name for the JSON
        output_path (str, optional): Path to save the JSON file. If None, uses the same path as excel_path with .json extension.
        remove_nulls (bool, optional): Whether to remove null values. Defaults to False.
        datatypes_file (str, optional): Path to datatypes file. Defaults to None.
        field_mapping (dict, optional): Mapping from target fields to source fields. Defaults to None.
        skiprows (int, optional): Number of rows to skip from the beginning of the file. Defaults to 0.

    Returns:
        str: Path to the output JSON file
    """
    logger.info(f"Converting Excel file: {excel_path}")
    logger.info(f"Root element: {root_element}")
    logger.info(f"Remove nulls: {remove_nulls}")

    # Generate output JSON path if not provided
    if output_path is None:
        output_path = str(Path(excel_path).with_suffix('.json'))
    logger.info(f"Output path: {output_path}")

    try:
        # Read Excel file
        logger.info(f"Reading Excel file (skipping {skiprows} rows)...")
        df = pd.read_excel(excel_path, skiprows=skiprows)
        logger.info(f"Excel file read successfully. Shape: {df.shape}")

        # Apply field mapping if provided
        if field_mapping:
            logger.info(f"Applying field mapping: {field_mapping}")
            # Create a new DataFrame with mapped columns
            mapped_df = pd.DataFrame()

            for target_field, source_field in field_mapping.items():
                if source_field in df.columns:
                    mapped_df[target_field] = df[source_field]
                    logger.debug(f"Mapped {source_field} to {target_field}")
                else:
                    logger.warning(f"Source field {source_field} not found in Excel file")

            # Use the mapped DataFrame if it has columns
            if not mapped_df.empty:
                logger.info(f"Using mapped DataFrame. Shape: {mapped_df.shape}")
                df = mapped_df
            else:
                logger.warning("No fields were mapped. Using original DataFrame.")

        # Try to load datatypes if available
        datatypes = None
        if datatypes_file:
            logger.info(f"Using datatypes file: {datatypes_file}")
            try:
                if os.path.exists(datatypes_file):
                    datatypes = load_datatypes(datatypes_file)
                    logger.debug(f"Datatypes loaded: {list(datatypes.keys())[:5]}...")
                else:
                    logger.warning(f"Datatypes file not found: {datatypes_file}")
            except Exception as dt_error:
                logger.error(f"Could not load datatypes: {dt_error}")

        # Apply datatypes directly to the DataFrame if available
        if datatypes:
            logger.info("Applying datatypes directly to the DataFrame...")
            for col, dtype in datatypes.items():
                if col in df.columns:
                    try:
                        # Attempt to convert columns with potential comma decimals to numeric first
                        if pd.api.types.is_string_dtype(df[col]) and (dtype == 'float' or dtype == 'int'):
                             # Replace comma with period for decimal conversion
                            df[col] = pd.to_numeric(df[col].str.replace(',', '.', regex=False), errors='coerce')
                        df[col] = df[col].astype(dtype)
                        logger.debug(f"Applied dtype '{dtype}' to column '{col}'.")
                    except Exception as e:
                        logger.warning(f"Could not apply dtype '{dtype}' to column '{col}': {e}")
                else:
                    logger.warning(f"Datatype specified for column '{col}' but column not found in DataFrame.")
        else:
            logger.info("No datatypes provided or loaded, skipping direct datatype application.")

        # Convert to JSON with nested structure
        logger.info("Converting to JSON with nested structure...")
        raw_json = df.to_dict(orient="records")
        logger.info(f"Number of records: {len(raw_json)}")

        for element in raw_json:
            unflatten_dic(element)
            merge_lists(element, remove_nulls)

        json_data = {root_element: raw_json}

        # Write JSON file
        logger.info(f"Writing JSON to: {output_path}")
        with io.open(output_path, "w", encoding='utf8') as file:
            file.write(json.dumps(json_data, indent=4, skipkeys=True))

        logger.info("Conversion completed successfully")
        return output_path
    except Exception as e:
        logger.error(f"Error converting Excel to JSON: {e}", exc_info=True)
        raise


def get_excel_headers(excel_path, skiprows=0):
    """
    Get the column headers from an Excel file.

    Args:
        excel_path (str): Path to the Excel file
        skiprows (int, optional): Number of rows to skip from the beginning of the file. Defaults to 0.

    Returns:
        list: List of column headers as strings
    """
    logger.info(f"Getting headers from Excel file: {excel_path} (skipping {skiprows} rows)")
    try:
        df = pd.read_excel(excel_path, skiprows=skiprows)
        # Convert all headers to strings to avoid type issues when creating QLabel widgets
        headers = [str(col) for col in df.columns]
        logger.info(f"Found {len(headers)} headers: {headers[:10]}...")
        return headers
    except Exception as e:
        logger.error(f"Error reading Excel headers: {e}")
        return []


def csv_to_json(csv_path, root_element, output_path=None, remove_nulls=False, datatypes_file=None, skiprows=0):
    """
    Convert CSV file to JSON.

    Args:
        csv_path (str): Path to the CSV file
        root_element (str): Root element name for the JSON
        output_path (str, optional): Path to save the JSON file. If None, uses the same path as csv_path with .json extension.
        remove_nulls (bool, optional): Whether to remove null values. Defaults to False.
        datatypes_file (str, optional): Path to datatypes file. Defaults to None.
        skiprows (int, optional): Number of rows to skip from the beginning of the file. Defaults to 0.

    Returns:
        str: Path to the output JSON file
    """
    logger.info(f"Converting CSV file: {csv_path}")
    logger.info(f"Root element: {root_element}")
    logger.info(f"Remove nulls: {remove_nulls}")

    # Generate output JSON path if not provided
    if output_path is None:
        output_path = str(Path(csv_path).with_suffix('.json'))
    logger.info(f"Output path: {output_path}")

    try:
        # Try to load datatypes if available
        datatypes = None
        if datatypes_file:
            logger.info(f"Using datatypes file: {datatypes_file}")
            try:
                if os.path.exists(datatypes_file):
                    datatypes = load_datatypes(datatypes_file)
                    logger.debug(f"Datatypes loaded: {list(datatypes.keys())[:5]}...")
                else:
                    logger.warning(f"Datatypes file not found: {datatypes_file}")
            except Exception as dt_error:
                logger.error(f"Could not load datatypes: {dt_error}")

        # Read CSV file
        logger.info(f"Reading CSV file (skipping {skiprows} rows)...")
        if datatypes:
            logger.debug("Reading CSV with datatypes...")
            df = pd.read_csv(csv_path, sep=";", engine="c", dtype=datatypes, decimal=',', skiprows=skiprows)
        else:
            logger.debug("Reading CSV without datatypes...")
            df = pd.read_csv(csv_path, sep=";", engine="c", decimal=',', skiprows=skiprows)
        logger.info(f"CSV file read successfully. Shape: {df.shape}")

        # Convert to JSON with nested structure
        logger.info("Converting to JSON with nested structure...")
        raw_json = df.to_dict(orient="records")
        logger.info(f"Number of records: {len(raw_json)}")

        for element in raw_json:
            unflatten_dic(element)
            merge_lists(element, remove_nulls)

        json_data = {root_element: raw_json}

        # Write JSON file
        logger.info(f"Writing JSON to: {output_path}")
        with io.open(output_path, "w", encoding='utf8') as file:
            file.write(json.dumps(json_data, indent=4, skipkeys=True))

        logger.info("Conversion completed successfully")
        return output_path
    except Exception as e:
        logger.error(f"Error converting CSV to JSON: {e}", exc_info=True)
        raise
