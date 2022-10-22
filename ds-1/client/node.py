from enum import Enum
import socket
import threading

class NodeColor(Enum):
    NONE = 'NONE'
    GRAY = 'GRAY'
    GREEN = 'GREEN'
    RED = 'RED'

class Node:

    def __init__(self, port):
        self._isCoordinator = False
        self._color = NodeColor.NONE
        self._port = port
        self._timeout = 1
        self._hostname = socket.gethostname()
        self._ip = socket.gethostbyname(self.hostname)
        self._semafore = threading.Semaphore(1)
        self._disabled = False
        self._other_nodes = []

    def disable(self):
        self._disabled = True
        self._color = NodeColor.GRAY
        print("Node [" + self.ip + "] was disabled")
    
    def enable(self):
        self._disabled = False
        self._color = NodeColor.NONE
        print("Node [" + self.ip + "] was enabled")

    def setcolor(self, color):
        self._color = color
        print("Node [" + self.ip + "] color is " + color)



