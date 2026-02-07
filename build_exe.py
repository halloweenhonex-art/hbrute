import os
import subprocess
import sys

def build():
    print("[*] Starting build process...")
    
    # Get current directory
    cwd = os.getcwd()
    
    # Define command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--console",
        "--name", "hbrute",
        # Including the entire hbrute package for imports
        "--add-data", f"hbrute/data;hbrute/data",
        # Entry point
        "run_hbrute.py"
    ]
    
    print(f"[*] Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n[+] Build successful! Executable is in 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Build failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[*] PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    build()
