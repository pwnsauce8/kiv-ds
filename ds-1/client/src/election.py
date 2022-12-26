from ipaddress import IPv4Interface
import signal
import netifaces as ni
import requests
import time
import math
import os
import sys
import config as config
from threading import Thread

# Method is going through all IP in the network until it reaches count out configured node 
# After all nodes are found, the election proceess will start
def start(current_node):
    coordinatorExists = False
    # Get interface address
    interface_address = ni.ifaddresses(config.INTERFACE)[ni.AF_INET][0]
    addr = interface_address['addr']
    mask = interface_address['netmask']
    interface = IPv4Interface(f'{addr}/{mask}')

    # Go through all ip in the network
    for ip in interface.network:
        if ip == interface.ip:
            continue

        # Send hello message
        hello = f'http://{ip}:{current_node._port}/hello'
        try:
            response = requests.post(hello, verify=False, timeout=config.TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                # Coorinator validation
                if not coordinatorExists and data['isCoordinator'] is True:
                    coordinatorExists = True
                    current_node.set_coordinator_ip(ip)
                if coordinatorExists is True and data['isCoordinator'] is True:
                    os.kill(os.getpid(), signal.SIGKILL)
                
                current_node.add_node(str(ip))
        except requests.exceptions.RequestException as e:
            if int(current_node._nodes_count) - 1 == (len(current_node._other_nodes)):
                break
            else:
                continue

        if int(current_node._nodes_count) - 1 == (len(current_node._other_nodes)):
                break
    
    if current_node._coordinator_ip is not None:
        Thread(target=handle_coordinator, args=(current_node, )).start()
    else:
        election(current_node)

# The simple Bully algorithm implementation
def election(current_node):
    isCoordinator = True
    # Get interface address
    interface_address = ni.ifaddresses(config.INTERFACE)[ni.AF_INET][0]
    addr = interface_address['addr']
    mask = interface_address['netmask']
    interface = IPv4Interface(f'{addr}/{mask}')

    split_addr_curr =  str(interface.ip).split(".")
    
    for ip in current_node._other_nodes:
        split_addr =  ip.split(".")
        # looking for master
        if (int(split_addr_curr[3]) > int(split_addr[3])):
            isCoordinator = isCoordinator and True
        else:
            isCoordinator = isCoordinator and False
    
    if isCoordinator is True:
        current_node.set_coordinator()
        # Notify other nodes coordinator has been found
        notify_others(current_node, 'set-coordinator', True)
        # Set colors of each node
        set_colors(current_node)
        # Handle all nodes whether its alive
        Thread(target=handle_nodes, args=(current_node, )).start()
    
    return isCoordinator

# Coordinator is printig information about all nodes
def print_nodes(current_node):
    if current_node._isCoordinator is False:
        return
    
    for ip in current_node._other_nodes:
        hello = f'http://{ip}:{current_node._port}/get-details'
        try:
            response = requests.get(hello, verify=False, timeout=config.TIMEOUT)
            if response.status_code == 200:
                data = response.json()

                print(f'*** {data["hostname"]} [{ip}] - {data["color"]}', flush=True)
        except requests.exceptions.RequestException as e:
            continue
 
# Setting color to nodes (1/3) is GREEN and (2/3) is RED 
def set_colors(current_node):
    if current_node._isCoordinator is False:
        return
    isOk = True
    # Number of all nodes in network 
    node_count = len(current_node._other_nodes) + 1 
    # (1/3) of all nodes are GREEN
    green_nodes = math.ceil((1.0 / 3.0) * node_count)  
    green_nodes = green_nodes - 1
    # (2/3) of all nodes are RED
    red_nodes = node_count - green_nodes 

    for ip in current_node._other_nodes:
        if green_nodes != 0:
            # Change node color to GREEN
            set_color = f'http://{ip}:{current_node._port}/set-color-green'
            response = requests.post(set_color, verify=False, timeout=config.TIMEOUT)
            if response.status_code != 200:
                isOk = False
                break
            green_nodes -= 1
            continue

        if red_nodes != 0:
            # Change node color to RED
            set_color = f'http://{ip}:{current_node._port}/set-color-red'
            response = requests.post(set_color, verify=False, timeout=config.TIMEOUT)
            if response.status_code != 200:
                isOk = False
                break
            red_nodes -= 1

    print_nodes(current_node)
    if not isOk:
        print("*** Cannot set colors to nodes.", flush=True)
    
# Handle all nodes, if some node is dead, the Coordinator will notify all nodes
def handle_nodes(current_node):
    while True:
        for ip in current_node._other_nodes:
            # Send hello message
            hello = f'http://{ip}:{current_node._port}/is-alive'
            
            try:
                response = requests.get(hello, verify=False, timeout=5)
                if response.status_code != 200:
                    current_node.remove_node(str(ip))
                    notify_others(current_node, 'node-is-dead', True)
                    time.sleep(3)
                    set_colors(current_node)
            except:
                current_node.remove_node(str(ip))
                notify_others(current_node, 'node-is-dead', True)
                time.sleep(3)
                set_colors(current_node)
                time.sleep(3)
                continue
        time.sleep(3)

# If node recieve a msg from Coordinator about another node's termination, 
# node will find and delete the terminated nodes from its list
def check_nodes(current_node):
        for node_ip in current_node._other_nodes:
            hello = f'http://{node_ip}:{current_node._port}/is-alive'
            
            try:
                response = requests.get(hello, verify=False, timeout=5)
                if response.status_code != 200:
                    current_node.remove_node(str(node_ip))
            except:
                current_node.remove_node(str(node_ip))
                continue

# Method is used to send message for all nodes
def notify_others(current_node, message, isPost):
    if current_node._isCoordinator is False:
        return

    for ip in current_node._other_nodes:
        coordinator = f'http://{ip}:{current_node._port}/{message}'
        if isPost is True:
            requests.post(coordinator, verify=False, timeout=config.TIMEOUT)
        else:
            requests.get(coordinator, verify=False, timeout=config.TIMEOUT)

# Handle Coordinator 
def handle_coordinator(current_node):
    while True:
        # Send hello message
        hello = f'http://{current_node._coordinator_ip}:{current_node._port}/is-alive'
        
        try:
            response = requests.get(hello, verify=False, timeout=5)
            if response.status_code != 200:
                current_node.remove_node(str(current_node._coordinator_ip))
                break
        except:
            current_node.remove_node(str(current_node._coordinator_ip))
            break
           
        time.sleep(3)

    # Start election
    election(current_node)
