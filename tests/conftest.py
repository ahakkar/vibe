import sys
import os

# This is configuration file for pytest, pytest will recognize this file automatically

# This will add the backend folder to the sys.path for pytest to recognize the modules
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
)
