"""Starts server if called as script"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server import *


def main():
    """Starts server"""
    start_server()


if __name__ == "__main__":
    main()
