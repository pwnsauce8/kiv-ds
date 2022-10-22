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
        self.port = port
        self.timeout = 1
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.semafore = threading.Semaphore(1)
        self.disabled = False

    def disable(self):
        self.disabled = True
        self.color = NodeColor.GRAY
        print("Node [" + self.ip + "] was disabled")
    
    def enable(self):
        self.disabled = False
        self.color = NodeColor.NONE
        print("Node [" + self.ip + "] was enabled")

    def setcolor(self, color):
        self.color = color
        print("Node [" + self.ip + "] color is " + color)



