import os
import subprocess
import sys
import shutil

def clean_directory(directory):
    """
    Clean a directory by removing all files and subdirectories.

    Args:
        directory (str): Directory to clean
    """
    if os.path.exists(directory):
        print(f"Cleaning {directory} directory...")
        shutil.rmtree(directory)


def build_executable():
    """
    Build a standalone executable using PyInstaller
    """
    print("Building standalone executable...")

    # Clean any previous build files
    clean_directory("build")
    clean_directory("dist")

    # Path to the icon file
    icon_path = os.path.abspath("src/csv2json/resources/csv2json.ico")
    if not os.path.exists(icon_path):
        print(f"Warning: Icon file not found at {icon_path}")
        icon_option = []
    else:
        print(f"Using icon: {icon_path}")
        icon_option = [f"--icon={icon_path}"]

    # Copy the icon to the root directory for easier access
    import shutil
    try:
        shutil.copy(icon_path, "csv2json.ico")
        print(f"Copied icon to root directory: {os.path.abspath('csv2json.ico')}")
    except Exception as e:
        print(f"Warning: Could not copy icon to root directory: {e}")

    # Build the executable
    cmd = [
        "pyinstaller",
        "--clean",
        "--name=CSV2JSON_Converter",
        "--windowed",  # No console window
        "--onefile",   # Single executable file
        "--add-data=src/csv2json/data/*.dt;csv2json/data",  # Include all .dt files
        "--add-data=*.dt;.",  # Include .dt files in root directory
        "--add-data=src/csv2json/resources/*.ico;csv2json/resources",  # Include icon files
        "--add-data=src/csv2json/resources/*.png;csv2json/resources",  # Include icon files
        "--add-data=csv2json.ico;.",  # Include icon file in root directory
        "--paths=.",  # Add current directory to Python path
        "--collect-all=csv2json",  # Collect all csv2json modules
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=qtawesome",
        "--hidden-import=PIL",
    ] + icon_option + [
        "src/csv2json/__main__.py"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("\nBuild successful!")
        print(f"Executable created at: {os.path.abspath('dist/CSV2JSON_Converter.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
