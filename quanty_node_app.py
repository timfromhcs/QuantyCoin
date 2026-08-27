"""
QuantyCoin Node GUI Entrypoint (v4.0)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ui.node_gui import launch_node_gui

if __name__ == "__main__":
    launch_node_gui()
