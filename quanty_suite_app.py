"""
QuantyCoin Suite GUI Entrypoint (v4.0)
"""
import os
import sys

# Inject current directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ui.suite_gui import launch_suite_gui

if __name__ == "__main__":
    launch_suite_gui()
