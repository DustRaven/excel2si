import pandas as pd

data = {
    'column_a': ['text1', 'text2', 'text3'],
    'column_b': [10, 20, 30], # Will be int
    'column_c': [1.1, 2.2, 3.3], # Will be float
    'column_d': ['not_an_int', '200', 'another_text'], # Mixed, '200' can be int
    'column_e': ['True', 'false', 'TRUE'], # Boolean-like strings
    'numeric_with_comma': ['10,5', '20,0', '30,33'] # String representation of numbers with commas
}
df = pd.DataFrame(data)

# Ensure no implicit conversion of '200' to int by pandas if object type is desired initially
df['column_d'] = df['column_d'].astype(str)
df['column_b'] = df['column_b'].astype(str) # Store as string to test conversion
df['column_c'] = df['column_c'].astype(str) # Store as string to test conversion


excel_file_path = "tests/test_excel.xlsx"
df.to_excel(excel_file_path, index=False, engine='openpyxl')

print(f"Excel file '{excel_file_path}' created successfully.")
