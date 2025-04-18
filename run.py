"""
Simple launcher script for the CSV2JSON application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.csv2json.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
