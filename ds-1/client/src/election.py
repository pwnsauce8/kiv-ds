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

def start(current_node):
    coordinatorExists = False
    # Get interface address
    interface_address = ni.ifaddresses(config.INTERFACE)[ni.AF_INET][0]
    addr = interface_address['addr']
    mask = interface_address['netmask']
    interface = IPv4Interface(f'{addr}/{mask}')

    for ip in interface.network:
        if ip == interface.ip:
            continue

        # Send hello message
        hello = f'http://{ip}:{current_node._port}/hello'
        try:
            response = requests.post(hello, verify=False, timeout=config.TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if not coordinatorExists and data['isCoordinator'] is True:
                    coordinatorExists = True
                    current_node.set_coordinator_ip(ip)
                if coordinatorExists is True and data['isCoordinator'] is True:
                    os.kill(os.getpid(), signal.SIGKILL)
                
                print(f"Node [{str(ip)}] was added", flush=True)
                current_node.add_node(str(ip))
        except requests.exceptions.RequestException as e:
            print(f"Error Nodes count [{str(current_node._nodes_count)}] - {len(current_node._other_nodes)}", flush=True)
            if int(current_node._nodes_count) - 1 == (len(current_node._other_nodes)):
                break
            else:
                continue

        print(f"Nodes count [{str(current_node._nodes_count)}] - {len(current_node._other_nodes)}", flush=True)
        if int(current_node._nodes_count) - 1 == (len(current_node._other_nodes)):
                break
    
    print('Finnish traversing', flush=True)
    if current_node._coordinator_ip is not None:
        print(f"***** Follow coordinator", flush=True)
        Thread(target=handle_coordinator, args=(current_node, )).start()
    else:
        print('*****Check', flush=True)
        election(current_node)


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
        print(f"***** {split_addr_curr[3]} vs {split_addr[3]}", flush=True)
        # Is master
        if (int(split_addr_curr[3]) > int(split_addr[3])):
            isCoordinator = isCoordinator and True
        else:
            isCoordinator = isCoordinator and False
    
    if isCoordinator is True:
        current_node.set_coordinator()
        # Notify other nodes
        notify_others(current_node, 'set-coordinator', True)
        # Set colors
        print(f"***** Set colors", flush=True)
        set_colors(current_node)
        Thread(target=handle_nodes, args=(current_node, )).start()
    
    return isCoordinator


# def election(current_node):
#     at_least_one_response = False
#     at_least_one_bigger = False

#     print(f"***** Election started", flush=True)
#     for ip in current_node._other_nodes:
#         split_addr =  ip.split(".")
#         split_addr_curr =  str(current_node._ip).split(".")

#         print(f"***** {split_addr[3]} vs {split_addr_curr[3]}", flush=True)
#         # Send election to greater IPs
#         if (int(split_addr[3]) > int(split_addr_curr[3])):
#             at_least_one_bigger = True
#             election_msg = f'http://{ip}:{current_node._port}/election'
#             response = requests.post(election_msg, verify=False, timeout=config.TIMEOUT)
#             if response.status_code == 200:
#                 at_least_one_response = True
#                 print(f"Response OK", flush=True)
    
#     if at_least_one_bigger is True and not at_least_one_response:
#         # Set as coordinator
#         current_node.set_coordinator()
#         set_colors(current_node)
#         Thread(target=handle_nodes, args=(current_node, )).start()
    
#     print(f"***** Election finished", flush=True)
    

def set_colors(current_node):
    if current_node._isCoordinator is False:
        return
    isOk = True
    # Number of all nodes in network 
    node_count = len(current_node._other_nodes) + 1 
    # (1/3) of all nodes are GREEN
    green_nodes = math.ceil((1.0 / 3.0) * node_count) - 1  
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
    
    if not isOk:
        print("Cannot set colors to nodes.", flush=True)
    
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
                    print("Node [" + ip + "] was deleted", flush=True)
            except:
                current_node.remove_node(str(ip))
                notify_others(current_node, 'node-is-dead', True)
                print("Node [" + ip + "] was deleted", flush=True)
                time.sleep(3)
                continue
        time.sleep(3)

def check_nodes(current_node):
        print(f"***** Checking nodes", flush=True)
        for node_ip in current_node._other_nodes:
            hello = f'http://{node_ip}:{current_node._port}/is-alive'
            
            try:
                response = requests.get(hello, verify=False, timeout=5)
                if response.status_code != 200:
                    current_node.remove_node(str(node_ip))
                    print("Node [" + node_ip + "] was deleted", flush=True)
            except:
                current_node.remove_node(str(node_ip))
                print("Node [" + node_ip + "] was deleted", flush=True)
                continue

def notify_others(current_node, message, isPost):
    if current_node._isCoordinator is False:
        return

    print(f"***** Notify started", flush=True)
    for ip in current_node._other_nodes:
        coordinator = f'http://{ip}:{current_node._port}/{message}'
        if isPost is True:
            requests.post(coordinator, verify=False, timeout=config.TIMEOUT)
        else:
            requests.get(coordinator, verify=False, timeout=config.TIMEOUT)
    print(f"***** Notify finished", flush=True)
    
def handle_coordinator(current_node):
    while True:
        # Send hello message
        hello = f'http://{current_node._coordinator_ip}:{current_node._port}/is-alive'
        
        try:
            response = requests.get(hello, verify=False, timeout=5)
            if response.status_code != 200:
                current_node.remove_node(str(current_node._coordinator_ip))
                print("***** Coordinator was deleted", flush=True)
                break
        except:
            current_node.remove_node(str(current_node._coordinator_ip))
            print("***** Coordinator was deleted", flush=True)
            break
           
        time.sleep(3)

    # Start election
    election(current_node)
