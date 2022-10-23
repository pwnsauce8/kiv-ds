from enum import Enum
from unittest.mock import DEFAULT

INTERFACE = 'eth0'
TIMEOUT = 1
DEFAULT_PORT = 5000
PREFIX = 'node-'

class NodeColor(Enum):
    NONE = 'NONE'
    GRAY = 'gray'
    GREEN = 'green'
    RED = 'red'