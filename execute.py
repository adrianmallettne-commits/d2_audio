"""D2 Audio Plugin - Dependency installer.

Run this from the Agent Zero Plugins UI to install required dependencies.
"""
import subprocess
import sys


def main() -> int:
    print("Installing D2 Audio plugin dependencies...")

    # Python packages
    packages = ["pydub", "numpy"]
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade"] + packages,
        text=True,
    )
    if result.returncode != 0:
        print("ERROR: pip install failed.")
        return result.returncode

    # ffmpeg (needed by pydub to handle MP3, AAC, etc.)
    print("Checking for ffmpeg...")
    check = subprocess.run(["which", "ffmpeg"], capture_output=True)
    if check.returncode != 0:
        print("ffmpeg not found — installing via apt-get...")
        apt = subprocess.run(
            ["apt-get", "install", "-y", "ffmpeg"],
            text=True,
        )
        if apt.returncode != 0:
            print("WARNING: ffmpeg installation failed. MP3/AAC support may be limited.")
    else:
        print("ffmpeg already installed.")

    print("\nD2 Audio dependencies ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
