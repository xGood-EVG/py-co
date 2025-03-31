"""This is module."""
import sys
from math import *


def thefun(a, b, c): # noqa: D401, D404
    """Some function."""
    return int(a) / int(b) + sin(int(c))


l = sys.argv[1]
a = b = l
print(a, b, sin(l))
