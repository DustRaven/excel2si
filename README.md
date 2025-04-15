# CSV2JSON Converter

A modern tool for converting Excel files to JSON format compatible with d.velop Smart Invoice, with support for nested structures, field mapping, and data type handling.

## Description

CSV2JSON Converter is a Python application with a Qt6-based GUI that allows you to convert Excel (.xlsx) files to JSON format specifically designed for [d.velop Smart Invoice](https://help.d-velop.de/docs/de/pub/smart-invoice-developer/cloud/verwenden-der-api-funktionen/ubertragen-von-stammdaten-dvelop-smart-invoice). It features an intuitive drag-and-drop interface for mapping Excel headers to target fields defined in schema files.

This tool simplifies the process of transferring master data to d.velop Smart Invoice by converting your Excel data into the required JSON format for the Smart Invoice API.

## Features

- Convert Excel (.xlsx) files to JSON with customizable field mapping
- Support for nested JSON structures using dot notation
- Modern Qt6-based graphical interface with drag-and-drop functionality
- Automatic field mapping based on name similarity
- Skip header rows as needed
- Customizable data type handling via schema files
- Export and import field mappings for reuse
- Option to remove null values
- Detailed logging with exportable log files

## Installation

### From Source

1. Clone the repository:
   ```
   git clone https://github.com/DustRaven/excel2si.git
   cd excel2si
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python run.py
   ```

### Using the Standalone Executable

Download the latest release from the [Releases](https://github.com/DustRaven/excel2si/releases) page.

## Usage

### Graphical User Interface

To start the GUI application:

```
python run.py
```

The GUI allows you to:
- Select an Excel file using the browse button or drag and drop
- Choose a root element for the JSON structure
- Skip header rows as needed
- Map Excel headers to target fields via drag and drop
- Auto-map fields based on name similarity
- Toggle the option to remove null values
- Convert the file with a single click
- Export and import field mappings
- View detailed logs

### Command Line Interface

To use the command-line interface:

```
python -m src.csv2json cli <root_element> <input_file> [options]
```

Options:
- `--output`, `-o`: Specify the output JSON file path
- `--datatypes`, `-d`: Specify a file with data type definitions
- `--mapping`, `-m`: Specify a mapping file
- `--skiprows`, `-s`: Number of rows to skip from the beginning
- `--debug`, `-v`: Print debug information
- `--remove-nulls`, `-n`: Remove null values from the output

### Building a Standalone Executable

To build a standalone Windows executable:

```
python build_exe.py
```

This will create a single executable file in the `dist` directory.

## Data Type Definitions

You can specify data types for fields in schema files with the `.dt` extension. The application supports two formats:

### YAML Format (Preferred)

```yaml
displayName: Products
root: products
fields:
  id: str
  name: str
  price: float
  is_active: bool
```

### Legacy Python Dictionary Format

```python
{
  "displayName": "Products",
  "root": "products",
  "fields": {
    "id": str,
    "name": str,
    "price": float,
    "is_active": bool
  }
}
```

The application automatically looks for schema files in the `src/csv2json/data` directory. Each file contains:

- `displayName`: The human-readable name shown in the UI dropdown
- `root`: The root element name used in the JSON output
- `fields`: Dictionary mapping field names to their Python types

## Field Mapping

The application provides an intuitive interface for mapping Excel headers to target fields:

1. Excel headers appear as draggable chips at the top of the window
2. Target fields from the schema file are displayed in a table
3. Drag headers and drop them onto the corresponding target fields
4. Use the Auto-Map feature to automatically match similar field names
5. Export your mapping for future use

## Smart Invoice Compatibility

This tool is specifically designed to work with [d.velop Smart Invoice](https://help.d-velop.de/docs/de/pub/smart-invoice-developer/cloud/verwenden-der-api-funktionen/ubertragen-von-stammdaten-dvelop-smart-invoice), a cloud-based invoice processing solution. The included schema files (`.dt` files) match the data structures required by the Smart Invoice API for master data transfer, including:

- Companies (Mandanten)
- Vendors (Lieferanten)
- Cost Centers (Kostenstellen)
- Cost Units (Kostenträger)
- GL Accounts (Sachkonten)
- Document Types (Belegarten)
- Payment Terms (Zahlungsbedingungen)
- Tax Codes (Steuerschlüssel)
- Currencies (Währungen)
- Vendor Bank Accounts (Lieferantenbankkonten)

The tool ensures that your Excel data is properly formatted and structured according to the requirements of the Smart Invoice API, making it easy to transfer master data to the system.

## Nested JSON Structures

Nested JSON structures are created using dot notation in target field names. For example:

### Input Excel:
```
ID | Name  | Address
---+-------+--------
1  | Test  | Berlin
```

### Mapping:
- ID → id
- Name → company.name
- Address → company.address

### Output JSON:
```json
{
  "products": [
    {
      "id": 1,
      "company": {
        "name": "Test",
        "address": "Berlin"
      }
    }
  ]
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
│       │   ├── converter.py
│       │   ├── file_service.py
│       │   └── logging.py
│       ├── data/
│       │   ├── __init__.py
│       │   └── *.dt
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   ├── mapping.py
│       │   ├── theme_minimal.py
│       │   ├── components/
│       │   ├── services/
│       │   └── windows/
│       └── resources/
├── build_exe.py
├── README.md
├── requirements.txt
├── run.py
└── setup.py
```

## Release Process

This project uses GitHub's Release Drafter to automate the creation of release notes:

1. Pull requests are automatically labeled based on their title and description
2. When PRs are merged to the main branch, a draft release is created or updated
3. Release notes are categorized based on PR labels (features, bug fixes, etc.)
4. When ready to release, a maintainer publishes the draft release with a new version tag
5. The tag triggers the build workflow which creates the executable

To contribute effectively:
- Make sure your PR title clearly describes the change
- Use conventional prefixes like "Fix:", "Feature:", or "Docs:" in PR titles when possible
- Review the automatically applied labels and adjust if needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.