import sys
import os

# This is configuration file for pytest, pytest will recognize this file automatically

# This will add the backend folder to the sys.path for pytest to recognize the modules
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
)

def pytest_configure(config):
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "int: mark a test as an integration test")
    config.addinivalue_line("markers", "sys: mark a test as an system test")
    config.addinivalue_line("markers", "perf: mark a test as an performance test")
    config.addinivalue_line("markers", "sec: mark a test as an security test")

    