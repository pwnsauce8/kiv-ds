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

        # Open config
        conf = open('/opt/client/config.conf', 'r')
        lines = conf.readlines()
        conf.close()
        self._nodes_count = lines[0].strip()
        print(f"*** Node [{str(self._ip)}] has been created", flush=True)


    def disable(self):
        self._disabled = True
        self._color = config.NodeColor.GRAY
        print("*** Node [" + self._ip + "] was disabled", flush=True)
    
    def enable(self):
        self._disabled = False
        self._color = config.NodeColor.NONE
        print("*** Node [" + self._ip + "] was enabled", flush=True)

    def set_color(self, color):
        self._semafore.acquire()
        self._color = color
        self._semafore.release()
        print("*** Node [" + self._ip + "] is " + str(color.value).upper(), flush=True)

    def add_node(self, node_ip):
        self._semafore.acquire()
        if node_ip not in self._other_nodes:
            self._other_nodes.append(str(node_ip))
        self._semafore.release()
        print("*** New Node [" + node_ip + "] has been added", flush=True)

    def remove_node(self, node_ip):
        self._semafore.acquire()
        if node_ip in self._other_nodes:
            self._other_nodes.remove(str(node_ip))
        self._semafore.release()
        print("*** Node [" + node_ip + "] has been removed", flush=True)
    
    def set_coordinator(self):
        self._isCoordinator = True
        self._coordinator_ip = self._ip
        self.set_color(config.NodeColor.GREEN)  # Master node must be green
        print("*** Node [" + self._ip + "] is a Coordinator", flush=True)
    
    def unset_coordinator(self):
        self._isCoordinator = False
        self.set_color(config.NodeColor.NONE) 
        print("*** Node [" + self._ip + "] is not a Coordinator", flush=True)

    def set_coordinator_ip(self, cip):
        self._semafore.acquire()
        self._coordinator_ip = cip
        self._semafore.release()
        print("*** New coordinator is [" + self._coordinator_ip + "]", flush=True)

    def get_info(self):
        return{
            'nodes': self._other_nodes,
            'hostname': self._hostname,
            'isCoordinator': str(self._isCoordinator),
            'color': self._color.value
        }


