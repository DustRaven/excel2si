import os
import platform
import subprocess
import sys
import shutil
import glob

def clean_directory(directory):
    """Clean a directory by removing all files and subdirectories."""
    if os.path.exists(directory):
        print(f"Cleaning {directory} directory...")
        shutil.rmtree(directory)

def is_windows():
    """Check if running on Windows."""
    return platform.system() == "Windows"

def get_data_files():
    """Get all data files that exist."""
    data_files = []

    # Check for .dt files in data directory
    dt_files = glob.glob(os.path.join("src", "csv2json", "data", "*.dt"))
    if dt_files:
        data_files.append(("src/csv2json/data/*.dt", "csv2json/data"))

    # Check for .dt files in root
    root_dt_files = glob.glob("*.dt")
    if root_dt_files:
        data_files.append(("*.dt", "."))

    # Check for icon files
    ico_files = glob.glob(os.path.join("src", "csv2json", "resources", "*.ico"))
    if ico_files:
        data_files.append(("src/csv2json/resources/*.ico", "csv2json/resources"))

    # Check for PNG files
    png_files = glob.glob(os.path.join("src", "csv2json", "resources", "*.png"))
    if png_files:
        data_files.append(("src/csv2json/resources/*.png", "csv2json/resources"))

    # Check for root icon
    if os.path.exists("csv2json.ico"):
        data_files.append(("csv2json.ico", "."))

    return data_files

def build_executable():
    """Build a standalone executable using PyInstaller"""
    print("Building standalone executable...")

    # Clean any previous build files
    clean_directory("build")
    clean_directory("dist")

    # Path to the icon file
    icon_path = os.path.abspath(os.path.join("src", "csv2json", "resources", "csv2json.ico"))
    if not os.path.exists(icon_path):
        print(f"Warning: Icon file not found at {icon_path}")
        icon_option = []
    else:
        print(f"Using icon: {icon_path}")
        icon_option = [f"--icon={icon_path}"]

        # Copy the icon to the root directory for easier access
        try:
            shutil.copy(icon_path, "csv2json.ico")
            print(f"Copied icon to root directory: {os.path.abspath('csv2json.ico')}")
        except Exception as e:
            print(f"Warning: Could not copy icon to root directory: {e}")

    # Get existing data files
    data_files = get_data_files()
    data_options = []
    for src, dst in data_files:
        data_options.append(f"--add-data={src};{dst}" if is_windows() else f"--add-data={src}:{dst}")

    # Build the executable
    cmd = [
        "pyinstaller",
        "--clean",
        "--name=CSV2JSON_Converter",
        "--windowed",  # No console window
        "--onefile",   # Single executable file
    ] + data_options + [
        "--paths=.",  # Add current directory to Python path
        "--collect-all=csv2json",  # Collect all csv2json modules
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=qtawesome",
        "--hidden-import=PIL",
    ] + icon_option + [
        os.path.join("src", "csv2json", "__main__.py")
    ]

    print("Running PyInstaller with command:")
    print(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("\nBuild successful!")
        exe_path = os.path.abspath(os.path.join("dist", "CSV2JSON_Converter.exe"))
        print(f"Executable created at: {exe_path}")

        if not os.path.exists(exe_path):
            print(f"Warning: Expected executable not found at {exe_path}")
            return False

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        print("PyInstaller output:")
        print(e.stdout)
        print("PyInstaller errors:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
