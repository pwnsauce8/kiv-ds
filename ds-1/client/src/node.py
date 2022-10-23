from pickle import TRUE
import socket
import threading
import requests
import config as config
from election import set_colors

class Node:

    def __init__(self):
        self._isCoordinator = False
        self._coordinator_ip = None
        self._color = config.NodeColor.NONE
        self._port = config.DEFAULT_PORT
        self._hostname = socket.gethostname()
        self._ip = socket.gethostbyname(self._hostname)
        self._semafore = threading.Semaphore(1)
        self._disabled = False
        self._other_nodes = []
        print("*******" + socket.gethostbyname(self._hostname))

    def disable(self):
        self._disabled = True
        self._color = config.NodeColor.GRAY
        print("Node [" + self._ip + "] was disabled")
    
    def enable(self):
        self._disabled = False
        self._color = config.NodeColor.NONE
        print("Node [" + self._ip + "] was enabled")

    def set_color(self, color):
        self._color = color
        print("Node [" + self._ip + "] set color to " + str(color))

    def add_node(self, node_ip):
        if node_ip not in self._other_nodes:
            self._other_nodes.append(str(node_ip))
        print("Added Node [" + node_ip + "]")

    def remove_node(self, node_ip):
        if node_ip in self._other_nodes:
            self._other_nodes.remove(str(node_ip))
        print("Removed Node [" + node_ip + "]")
    
    def set_coordinator(self):
        self._isCoordinator = True
        self.set_color(config.NodeColor.GREEN)  # Master node must be green
        print("Node [" + self._ip + "] is a Coordinator")
        # Notify all nodes
        for ip in self._other_nodes:
            coordinator = f'http://{ip}:{self._port}/set-coordinator'
            requests.post(coordinator, verify=False, timeout=config.TIMEOUT)
        # set colors no other nodes
        set_colors(self)
    
    def unset_coordinator(self):
        self._isCoordinator = False
        self.set_color(config.NodeColor.NONE) 
        print("Node [" + self._ip + "] is not a Coordinator")

    def set_coordinator_ip(self, cip):
        self._coordinator_ip = cip
        print("New coordinator is [" + self._coordinator_ip + "]")
            
    def get_info(self):
        return{
            'isCoordinator': self._isCoordinator,
            'color': self._color
        }


