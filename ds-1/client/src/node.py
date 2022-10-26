import socket
import threading
import requests
import config as config

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

        print(f"Node [{str(self._ip)}] was created", flush=True)
        # Open config
        conf = open('/opt/client/config.conf', 'r')
        lines = conf.readlines()
        conf.close()
        self._nodes_count = lines[0].strip()


    def disable(self):
        self._disabled = True
        self._color = config.NodeColor.GRAY
        print("Node [" + self._ip + "] was disabled")
    
    def enable(self):
        self._disabled = False
        self._color = config.NodeColor.NONE
        print("Node [" + self._ip + "] was enabled")

    def set_color(self, color):
        self._semafore.acquire()
        self._color = color
        self._semafore.release()
        print("Node [" + self._ip + "] set color to " + str(color))

    def add_node(self, node_ip):
        self._semafore.acquire()
        if node_ip not in self._other_nodes:
            self._other_nodes.append(str(node_ip))
        self._semafore.release()
        print("Added Node [" + node_ip + "]")

    def remove_node(self, node_ip):
        self._semafore.acquire()
        if node_ip in self._other_nodes:
            self._other_nodes.remove(str(node_ip))
        self._semafore.release()
        print("Removed Node [" + node_ip + "]")
    
    def set_coordinator(self):
        self._isCoordinator = True
        self._coordinator_ip = self._ip
        self.set_color(config.NodeColor.GREEN)  # Master node must be green
        print("Node [" + self._ip + "] is a Coordinator")
    
    def unset_coordinator(self):
        self._isCoordinator = False
        self.set_color(config.NodeColor.NONE) 
        print("Node [" + self._ip + "] is not a Coordinator")

    def set_coordinator_ip(self, cip):
        self._semafore.acquire()
        self._coordinator_ip = cip
        self._semafore.release()
        print("New coordinator is [" + self._coordinator_ip + "]")

    def get_info(self):
        return{
            'nodes': self._other_nodes,
            'hostname': self._hostname,
            'isCoordinator': str(self._isCoordinator),
            'color': self._color.value
        }


