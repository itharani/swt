# test file

import subprocess
import difflib
import shutil
from termcolor import cprint

def read_requirements(file_path):
    """Read the requirements.txt file and return its contents as a list."""
    try:
        with open(file_path, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []

def uninstall_all_packages():
    """Uninstall all installed Python packages."""
    print("Uninstalling all packages...")
    subprocess.run(["pip", "freeze"], stdout=open("temp_freeze.txt", "w"), check=True)
    subprocess.run(["pip", "uninstall", "-y", "-r", "temp_freeze.txt"], check=True)
    print("All packages uninstalled.")

def install_requirements():
    """Install packages from requirements.txt."""
    print("Installing packages from requirements.txt...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    print("Installation complete.")

def run_pip_audit():
    """Run pip-audit and return True if vulnerabilities exist."""
    pip_audit_path = shutil.which("pip-audit")  # Find full path of pip-audit
    if not pip_audit_path:
        print("Error: pip-audit not found. Install it with 'pip install pip-audit'")
        return False
    
    try:
        result = subprocess.run([pip_audit_path], capture_output=True, text=True, check=False)
        print(result.stdout)
        return "Vulnerabilities found" in result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running pip-audit: {e.stderr}")
        return False
    
def fix_vulnerabilities():
    """Run pip-audit --fix in a loop until no vulnerabilities remain."""
    while True:
        print("Running pip-audit --fix...")
        result = subprocess.run(["pip-audit", "--fix"], capture_output=True, text=True, check=False)
        print(result.stdout)
        if "No known vulnerabilities found" in result.stdout:
            break

def show_requirements_diff(original, updated):
    """Show the difference between the original and final requirements.txt."""
    diff = difflib.unified_diff(original, updated, fromfile="Original", tofile="Updated", lineterm="")
    diff_output = "\n".join(diff)
    print("\n===== Requirements.txt Changes =====")
    # Iterate over the diff and color-code lines
    for line in diff:
        if line.startswith("+"):
            cprint(line, "green", end="")  # Additions in green
        elif line.startswith("-"):
            cprint(line, "red", end="")  # Deletions in red
        else:
            print(line, end="")  # No change lines in default format
    print("====================================")

def main():
    # Backup original requirements
    original_requirements = read_requirements("requirements.txt")

    # Uninstall all packages
    uninstall_all_packages()

    # Reinstall from requirements.txt
    install_requirements()

    # Run pip-audit and attempt fixes
    if run_pip_audit():
        fix_vulnerabilities()

    # Backup final requirements
    subprocess.run(["pip", "freeze"], stdout=open("requirements.txt", "w"), check=True)
    updated_requirements = read_requirements("requirements.txt")

    # Show difference between original and final requirements.txt
    show_requirements_diff(original_requirements, updated_requirements)

if __name__ == "__main__":
    main()
