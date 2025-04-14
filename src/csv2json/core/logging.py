"""
Logging module for CSV2JSON converter.
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Create a custom logger
logger = logging.getLogger('csv2json')
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(log_format)

# Add handlers to the logger
logger.addHandler(console_handler)

# In-memory log storage for GUI display
log_records = []

class MemoryHandler(logging.Handler):
    """Custom handler that stores log records in memory for GUI display."""
    
    def emit(self, record):
        log_records.append(self.format(record))
        # Keep only the last 1000 records to avoid memory issues
        if len(log_records) > 1000:
            log_records.pop(0)

# Create and add memory handler
memory_handler = MemoryHandler()
memory_handler.setFormatter(log_format)
logger.addHandler(memory_handler)

def setup_file_logging(log_dir=None):
    """
    Set up file logging.
    
    Args:
        log_dir (str, optional): Directory to store log files. Defaults to None.
    """
    if log_dir is None:
        # Use user's documents folder by default
        log_dir = os.path.join(Path.home(), 'Documents', 'CSV2JSON', 'logs')
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a file handler
    log_file = os.path.join(log_dir, f'csv2json_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    
    # Add file handler to the logger
    logger.addHandler(file_handler)
    
    logger.info(f"Log file created at: {log_file}")
    return log_file

def get_logs():
    """
    Get all log records.
    
    Returns:
        list: List of log records.
    """
    return log_records

def clear_logs():
    """Clear all log records."""
    log_records.clear()
    logger.info("Logs cleared")

def export_logs(file_path):
    """
    Export logs to a file.
    
    Args:
        file_path (str): Path to export logs to.
    """
    try:
        with open(file_path, 'w') as f:
            for record in log_records:
                f.write(f"{record}\n")
        logger.info(f"Logs exported to: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting logs: {e}")
        return False
