"""
QuantyCoin Miner GUI Entrypoint (v4.0)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ui.miner_gui import launch_miner_gui

if __name__ == "__main__":
    launch_miner_gui()
