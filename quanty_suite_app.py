"""
QuantyCoin Master Suite GUI Entrypoint (Native Qt6 v4.0)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ui.qt_suite_app import main

if __name__ == "__main__":
    main()
