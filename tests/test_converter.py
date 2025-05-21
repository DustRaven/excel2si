import unittest
import os
import json
import yaml
import pandas as pd
from pathlib import Path
from unittest.mock import patch, mock_open

# Attempt to import functions from the src directory
try:
    from src.csv2json.core.converter import load_datatypes, excel_to_json, csv_to_json
    from src.csv2json.core.logging import logger # For mocking
except ImportError:
    # This is a fallback for environments where src is not directly in PYTHONPATH
    # You might need to adjust this based on your testing setup or run tests as a module
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.csv2json.core.converter import load_datatypes, excel_to_json, csv_to_json
    from src.csv2json.core.logging import logger


class TestLoadDatatypes(unittest.TestCase):
    test_dir = Path("tests")
    valid_yaml_path = test_dir / "datatypes_valid.yaml"
    invalid_yaml_path = test_dir / "datatypes_invalid.yaml"
    malformed_yaml_path = test_dir / "datatypes_malformed.yaml"


    @classmethod
    def setUpClass(cls):
        cls.test_dir.mkdir(exist_ok=True)
        # Valid YAML content
        valid_content = {
            "fields": {
                "column_a": "str",
                "column_b": "int",
                "column_c": "float"
            }
        }
        with open(cls.valid_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(valid_content, f)

        # Invalid YAML (parsable but not the structure load_datatypes expects for direct use)
        # This will be loaded as is, not extracting 'fields'
        invalid_content_direct = {
            "column_x": "str",
            "column_y": "int"
        }
        with open(cls.invalid_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(invalid_content_direct, f)

        # Malformed YAML content (syntax error)
        malformed_content = "fields: [column_a: str, column_b: int" # Missing closing bracket
        with open(cls.malformed_yaml_path, 'w', encoding='utf-8') as f:
            f.write(malformed_content)

    @classmethod
    def tearDownClass(cls):
        if cls.valid_yaml_path.exists():
            cls.valid_yaml_path.unlink()
        if cls.invalid_yaml_path.exists():
            cls.invalid_yaml_path.unlink()
        if cls.malformed_yaml_path.exists():
            cls.malformed_yaml_path.unlink()
        # Attempt to remove the tests directory if it's empty
        try:
            cls.test_dir.rmdir()
        except OSError:
            pass # Directory not empty, or other error

    def test_load_valid_yaml_with_fields_key(self):
        expected_datatypes = {
            "column_a": "str",
            "column_b": "int",
            "column_c": "float"
        }
        datatypes = load_datatypes(str(self.valid_yaml_path))
        self.assertEqual(datatypes, expected_datatypes)

    def test_load_valid_yaml_direct_structure(self):
        expected_datatypes = {
            "column_x": "str",
            "column_y": "int"
        }
        datatypes = load_datatypes(str(self.invalid_yaml_path)) # Using the "invalid" one for this test
        self.assertEqual(datatypes, expected_datatypes)


    def test_load_non_existent_file(self):
        with self.assertRaises((FileNotFoundError, Exception)) as cm: # More general for CI
            load_datatypes("non_existent_file.yaml")
        self.assertTrue(isinstance(cm.exception, (FileNotFoundError, Exception)))


    def test_load_malformed_yaml(self):
        with self.assertRaises(yaml.YAMLError):
            load_datatypes(str(self.malformed_yaml_path))

class BaseConverterTest(unittest.TestCase):
    test_dir = Path("tests")
    output_json_path = test_dir / "output.json"
    datatypes_yaml_path = test_dir / "datatypes_test.yaml" # Already created by user
    test_excel_path = test_dir / "test_excel.xlsx" # Already created by user
    test_csv_path = test_dir / "test_csv.csv" # Already created by user

    def tearDown(self):
        if self.output_json_path.exists():
            self.output_json_path.unlink()
        # The main datatypes_test.yaml, test_excel.xlsx, test_csv.csv
        # should be managed outside individual test methods if they are pre-generated.
        # If tests create their own versions, they should clean them up.

class TestExcelToJson(BaseConverterTest):

    def test_excel_to_json_no_datatypes(self):
        output_file = excel_to_json(
            excel_path=str(self.test_excel_path),
            root_element="data",
            output_path=str(self.output_json_path)
        )
        self.assertTrue(Path(output_file).exists())
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 3)
        # Check a few values, expecting them as strings or default pandas types
        self.assertEqual(data["data"][0]["column_a"], "text1")
        self.assertEqual(data["data"][0]["column_b"], "10") # Was stored as string in excel
        self.assertEqual(data["data"][1]["column_c"], "2.2") # Was stored as string in excel

    def test_excel_to_json_with_datatypes(self):
        output_file = excel_to_json(
            excel_path=str(self.test_excel_path),
            root_element="data",
            datatypes_file=str(self.datatypes_yaml_path),
            output_path=str(self.output_json_path)
        )
        self.assertTrue(Path(output_file).exists())
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn("data", data)
        records = data["data"]
        self.assertEqual(len(records), 3)

        # Check types based on datatypes_test.yaml
        # fields:
        #   column_a: str
        #   column_b: int
        #   column_c: float
        #   column_d: str
        #   column_e: bool
        #   numeric_with_comma: float
        self.assertIsInstance(records[0]["column_a"], str)
        self.assertEqual(records[0]["column_a"], "text1")

        self.assertIsInstance(records[0]["column_b"], int)
        self.assertEqual(records[0]["column_b"], 10)
        self.assertIsInstance(records[1]["column_b"], int)
        self.assertEqual(records[1]["column_b"], 20)

        self.assertIsInstance(records[0]["column_c"], float)
        self.assertEqual(records[0]["column_c"], 1.1)
        self.assertIsInstance(records[1]["column_c"], float)
        self.assertEqual(records[1]["column_c"], 2.2)

        # column_d: 'not_an_int', '200', 'another_text' -> specified as str
        self.assertIsInstance(records[0]["column_d"], str)
        self.assertEqual(records[0]["column_d"], "not_an_int")
        self.assertIsInstance(records[1]["column_d"], str) # '200' should remain str as per datatype
        self.assertEqual(records[1]["column_d"], "200")
        self.assertIsInstance(records[2]["column_d"], str)
        self.assertEqual(records[2]["column_d"], "another_text")

        # column_e: 'True', 'false', 'TRUE' -> specified as bool
        self.assertIsInstance(records[0]["column_e"], bool)
        self.assertEqual(records[0]["column_e"], True)
        self.assertIsInstance(records[1]["column_e"], bool)
        self.assertEqual(records[1]["column_e"], False)
        self.assertIsInstance(records[2]["column_e"], bool)
        self.assertEqual(records[2]["column_e"], True)
        
        # numeric_with_comma: ['10,5', '20,0', '30,33'] -> specified as float
        self.assertIsInstance(records[0]["numeric_with_comma"], float)
        self.assertEqual(records[0]["numeric_with_comma"], 10.5)
        self.assertIsInstance(records[1]["numeric_with_comma"], float)
        self.assertEqual(records[1]["numeric_with_comma"], 20.0)
        self.assertIsInstance(records[2]["numeric_with_comma"], float)
        self.assertEqual(records[2]["numeric_with_comma"], 30.33)

    @patch('src.csv2json.core.converter.logger.warning')
    def test_excel_to_json_type_conversion_warning(self, mock_logger_warning):
        # Create a temporary datatypes file that will cause a warning
        warning_datatypes_content = {
            "fields": {
                "column_a": "int" # Trying to convert "text1" to int
            }
        }
        warning_dt_path = self.test_dir / "warning_dt.yaml"
        with open(warning_dt_path, 'w', encoding='utf-8') as f:
            yaml.dump(warning_datatypes_content, f)

        excel_to_json(
            excel_path=str(self.test_excel_path),
            root_element="data",
            datatypes_file=str(warning_dt_path),
            output_path=str(self.output_json_path)
        )
        
        mock_logger_warning.assert_called()
        # Check that a warning for column_a was logged
        found_warning = False
        for call_args in mock_logger_warning.call_args_list:
            if "Could not apply dtype 'int' to column 'column_a'" in call_args[0][0]:
                found_warning = True
                break
        self.assertTrue(found_warning, "Expected warning for column_a type conversion was not logged.")

        if warning_dt_path.exists():
            warning_dt_path.unlink()

    def test_excel_to_json_field_mapping(self):
        field_mapping = {
            "new_col_a": "column_a",
            "new_col_b": "column_b",
            "non_existent_source": "non_existent_df_col" # Should be ignored
        }
        output_file = excel_to_json(
            excel_path=str(self.test_excel_path),
            root_element="mapped_data",
            field_mapping=field_mapping,
            datatypes_file=str(self.datatypes_yaml_path), # Use original datatypes for mapped columns
            output_path=str(self.output_json_path)
        )
        self.assertTrue(Path(output_file).exists())
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn("mapped_data", data)
        records = data["mapped_data"]
        self.assertEqual(len(records), 3)
        
        # Check that mapped fields exist and original ones don't (unless also mapped)
        self.assertIn("new_col_a", records[0])
        self.assertIn("new_col_b", records[0])
        self.assertNotIn("column_a", records[0]) # Original name should be gone
        self.assertNotIn("non_existent_source", records[0])

        self.assertEqual(records[0]["new_col_a"], "text1")
        self.assertEqual(records[0]["new_col_b"], 10) # Type conversion should still apply


class TestCsvToJson(BaseConverterTest):

    def test_csv_to_json_with_datatypes(self):
        output_file = csv_to_json(
            csv_path=str(self.test_csv_path),
            root_element="csv_data",
            datatypes_file=str(self.datatypes_yaml_path),
            output_path=str(self.output_json_path)
        )
        self.assertTrue(Path(output_file).exists())
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn("csv_data", data)
        records = data["csv_data"]
        self.assertEqual(len(records), 3)

        # Check types based on datatypes_test.yaml
        self.assertIsInstance(records[0]["column_a"], str)
        self.assertEqual(records[0]["column_a"], "text1")

        self.assertIsInstance(records[0]["column_b"], int)
        self.assertEqual(records[0]["column_b"], 10)

        self.assertIsInstance(records[0]["column_c"], float)
        self.assertEqual(records[0]["column_c"], 1.1)
        
        # column_d: 'not_an_int', '200', 'another_text' -> specified as str in datatypes_test.yaml
        self.assertIsInstance(records[0]["column_d"], str)
        self.assertEqual(records[0]["column_d"], "not_an_int")
        self.assertIsInstance(records[1]["column_d"], str) # '200' becomes str
        self.assertEqual(records[1]["column_d"], "200")

        self.assertIsInstance(records[0]["column_e"], bool)
        self.assertEqual(records[0]["column_e"], True)
        self.assertIsInstance(records[1]["column_e"], bool)
        self.assertEqual(records[1]["column_e"], False)

        # numeric_with_comma: ['10,5', '20,0', '30,33'] -> specified as float
        # For read_csv, pandas handles comma decimal conversion if `decimal=','` is passed,
        # which it is in csv_to_json. So these should be floats directly.
        self.assertIsInstance(records[0]["numeric_with_comma"], float)
        self.assertEqual(records[0]["numeric_with_comma"], 10.5)
        self.assertIsInstance(records[1]["numeric_with_comma"], float)
        self.assertEqual(records[1]["numeric_with_comma"], 20.0)


if __name__ == '__main__':
    # This allows running the tests directly from the script
    # Create dummy files that are expected to exist from previous steps if not running in sequence
    # This is mostly for local testing of this script itself.
    # In the actual agent flow, these would be created by previous tool calls.
    
    test_dir_main = Path("tests")
    test_dir_main.mkdir(exist_ok=True)

    if not (test_dir_main / "datatypes_test.yaml").exists():
        print("Creating dummy datatypes_test.yaml for standalone run...")
        with open(test_dir_main / "datatypes_test.yaml", 'w') as f:
            yaml.dump({
                "fields": {
                    "column_a": "str", "column_b": "int", "column_c": "float",
                    "column_d": "str", "column_e": "bool", "numeric_with_comma": "float"
                }
            }, f)

    if not (test_dir_main / "test_csv.csv").exists():
        print("Creating dummy test_csv.csv for standalone run...")
        with open(test_dir_main / "test_csv.csv", 'w') as f:
            f.write("column_a;column_b;column_c;column_d;column_e;numeric_with_comma\n")
            f.write("text1;10;1.1;not_an_int;True;10,5\n")
            f.write("text2;20;2.2;200;false;20,0\n")
            f.write("text3;30;3.3;another_text;TRUE;30,33\n")

    if not (test_dir_main / "test_excel.xlsx").exists():
        print("Creating dummy test_excel.xlsx for standalone run...")
        try:
            df_excel = pd.DataFrame({
                'column_a': ['text1', 'text2', 'text3'],
                'column_b': ["10", "20", "30"], 
                'column_c': ["1.1", "2.2", "3.3"], 
                'column_d': ['not_an_int', '200', 'another_text'],
                'column_e': ['True', 'false', 'TRUE'],
                'numeric_with_comma': ['10,5', '20,0', '30,33']
            })
            df_excel.to_excel(test_dir_main / "test_excel.xlsx", index=False, engine='openpyxl')
        except Exception as e:
            print(f"Could not create dummy excel: {e}. openpyxl might be missing.")

    unittest.main(argv=['first-arg-is-ignored'], exit=False)
