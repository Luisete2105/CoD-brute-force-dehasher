# main.py
import sys
import os

# Optional: set up paths early
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)           # helps when running from anywhere

from src.application.app import run_application


if __name__ == "__main__":
    sys.exit(run_application())