"""
Command-line interface for CSV2JSON converter.
"""

import argparse
import os
import locale
import sys
from pathlib import Path

from src.csv2json.core.converter import excel_to_json, csv_to_json, load_datatypes


def main():
    """
    Main entry point for the command-line interface.
    """
    # Set locale for number formatting
    try:
        locale.setlocale(locale.LC_NUMERIC, 'German_Germany.1252')
    except locale.Error:
        pass  # Use default locale if German is not available

    parser = argparse.ArgumentParser(description="Convert CSV/Excel to JSON")
    parser.add_argument('root', help="The root element to use")
    parser.add_argument('input_file', help="The path to the input CSV or Excel file")
    parser.add_argument('--output', '-o', help="The path to the output JSON file", nargs='?', const=None, type=str)
    parser.add_argument('--datatypes', '-d', help="File with datatypes in python object format", nargs='?', const=None, type=str)
    parser.add_argument('--debug', '-v', action='store_true', help="Print output to stdout")
    parser.add_argument(
        '--remove-nulls', '-n',
        help="Remove null values from output",
        action='store_true',
        default=False,
        dest='remove_nulls'
    )

    args = parser.parse_args()

    # Determine output file path
    output_file = args.output
    if output_file is None:
        filename, ext = os.path.splitext(args.input_file)
        output_file = filename + ".json"

    # Debug output
    if args.debug:
        print(f"Converting "
              f"\033[32m{args.input_file}\033[0m"
              f" to "
              f"\033[32m{output_file}\033[0m"
              f" using root element "
              f"\033[32m{args.root}\033[0m"
              f"{' and deleting empty keys' if args.remove_nulls else ''}.")

    # Determine datatypes file
    datatypes_file = args.datatypes
    if datatypes_file is None:
        default_dt_file = args.root + '.dt'
        if os.path.exists(default_dt_file):
            datatypes_file = default_dt_file
            if args.debug:
                print(f"Using builtin datatypes for {args.root}.")
    elif args.debug:
        print(f"Using datatypes from {datatypes_file}.")

    # Determine file type and convert
    input_path = Path(args.input_file)
    if input_path.suffix.lower() in ['.xlsx', '.xls']:
        # Excel file
        result_path = excel_to_json(
            args.input_file,
            args.root,
            output_file,
            args.remove_nulls,
            datatypes_file
        )
    elif input_path.suffix.lower() in ['.csv']:
        # CSV file
        result_path = csv_to_json(
            args.input_file,
            args.root,
            output_file,
            args.remove_nulls,
            datatypes_file
        )
    else:
        print(f"Error: Unsupported file format: {input_path.suffix}")
        sys.exit(1)

    if args.debug:
        print(f"Successfully converted to {result_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
