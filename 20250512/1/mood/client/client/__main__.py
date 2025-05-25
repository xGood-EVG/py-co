"""Client side of MOOD"""

import sys
import os
import io
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from client import *


if __name__ == "__main__":
    start_client()
    sys.exit(0)
