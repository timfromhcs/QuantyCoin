"""
QuantyCoin Full Node Daemon CLI Entrypoint (v4.0)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from node.daemon import main

if __name__ == "__main__":
    main()
