"""
Main entry point for the CSV2JSON package.
"""

import sys
import argparse
import importlib.util
import os


def main():
    """
    Main entry point for the CSV2JSON package.
    """
    parser = argparse.ArgumentParser(description="CSV2JSON Converter")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run the command-line interface")

    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Run the graphical user interface")

    args, remaining = parser.parse_known_args()

    # Try to import modules with or without 'src' prefix
    try:
        if args.command == "cli":
            try:
                from src.csv2json.core.cli import main as cli_main
            except ImportError:
                from csv2json.core.cli import main as cli_main
            sys.exit(cli_main())
        elif args.command == "gui":
            try:
                from src.csv2json.gui.app import main as gui_main
            except ImportError:
                from csv2json.gui.app import main as gui_main
            sys.exit(gui_main())
        else:
            # Default to GUI if no command is specified
            try:
                from src.csv2json.gui.app import main as gui_main
            except ImportError:
                from csv2json.gui.app import main as gui_main
            sys.exit(gui_main())
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
