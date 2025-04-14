# CSV2JSON Converter

A tool for converting Excel/CSV files to JSON with support for nested structures.

## Description

CSV2JSON Converter is a Python application that allows you to convert Excel (.xlsx) and CSV files to JSON format. It supports nested JSON structures using dot notation in column headers.

## Features

- Convert Excel (.xlsx) files to JSON
- Convert CSV files to JSON
- Support for nested JSON structures using dot notation
- Graphical user interface with drag and drop support
- Command-line interface for batch processing
- Customizable data type handling
- Option to remove null values

## Installation

### From Source

1. Clone the repository:
   ```
   git clone https://github.com/example/csv2json.git
   cd csv2json
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```
   pip install -e .
   ```

### Using pip

```
pip install csv2json
```

## Usage

### Graphical User Interface

To start the GUI application:

```
python run.py
```

Or if installed via pip:

```
csv2json
```

The GUI allows you to:
- Select an Excel file using the browse button or drag and drop
- Choose a root element for the JSON structure
- Toggle the option to remove null values
- Convert the file with a single click

### Command Line Interface

To use the command-line interface:

```
python -m csv2json cli <root_element> <input_file> [options]
```

Or if installed via pip:

```
csv2json cli <root_element> <input_file> [options]
```

Options:
- `--output`, `-o`: Specify the output JSON file path
- `--datatypes`, `-d`: Specify a file with data type definitions
- `--debug`, `-v`: Print debug information
- `--remove-nulls`, `-n`: Remove null values from the output

### Building a Standalone Executable

To build a standalone Windows executable:

```
python build_exe.py
```

This will create a single executable file in the `dist` directory.

## Data Type Definitions

You can specify data types for columns in a separate file. The format follows pandas dtype specification:

```python
{'ColumnName': str, 'AnotherColumn': float}
```

The application will automatically look for a `.dt` file with the same name as the root element.

## Nested JSON Structures

Nested JSON structures are created using dot notation in column headers. For example:

### Input:
```
Spalte1.test,Spalte1.test2,Spalte2
Wert, Wert, Wert
```
### Output:
```json
{
  "Spalte1": {
    "test": "Wert",
    "test2": "Wert"
  },
  "Spalte2": "Wert"
}
```
## Project Structure

```
csv2json/
├── src/
│   └── csv2json/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── cli.py
│       │   └── converter.py
│       ├── data/
│       │   ├── __init__.py
│       │   └── *.dt
│       └── gui/
│           ├── __init__.py
│           └── app.py
├── build_exe.py
├── README.md
├── requirements.txt
├── run.py
└── setup.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.