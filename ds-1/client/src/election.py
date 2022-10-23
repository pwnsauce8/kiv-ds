from ipaddress import IPv4Interface
import netifaces as ni
import requests
import time
import math
import socket
import config as config

def start(current_node):
    # node_name = 'node-'
    # node_counter = 1
    # remaining_time = 1200

    # print("******* Started")
    # while remaining_time > 0:
    #     start_time = time.time()
    #     node_hostname = node_name + str(node_counter)
        
    #     try:
    #         if node_hostname == socket.gethostname(): 
    #             ip = socket.getsockname()[0]
    #         else:  
    #             print("******* " + node_hostname)
    #             node_ip = socket.gethostbyname(node_hostname)
    #             print("******* " + node_ip)
    #             # Send hello message
    #             hello = f'http://{node_ip}:{current_node._port}/hello'
    #             # Send hello message
    #             hello = f'http://{node_ip}:{current_node._port}/hello'
                
    #             response = requests.post(hello, verify=False, timeout=config.TIMEOUT)

    #             if response.status_code == 200:
    #                 print("Node [" + node_ip + "] was added")
    #                 current_node.add_node(str(node_ip))
    #             else:
    #                 print("Node [" + node_ip + "] sent status " + response.status_code)
    #     except:
    #         print("******* Error " + str(remaining_time))
            
    #     end_time = time.time()
    #     remaining_time -= (end_time - start_time)
        
    # print("******* FINISH\n")
    # Get interface address
    print(socket.gethostname())
    
    interface_address = ni.ifaddresses(config.INTERFACE)[ni.AF_INET][0]
    addr = interface_address['addr']
    mask = interface_address['netmask']
    interface = IPv4Interface(f'{addr}/{mask}')

    for ip in interface.network:
        if ip == current_node._ip:
            continue

        # Send hello message
        hello = f'http://{ip}:{current_node._port}/hello'
        
        response = requests.post(hello, verify=False, timeout=config.TIMEOUT)

        if response.status_code == 200:
            print("Node [" + ip + "] was added")
            current_node.add_node(str(ip))
        else:
            print("Node [" + ip + "] sent status " + response.status_code)
    
    election(current_node)

def election(current_node):
    at_least_one_response = False

    for ip in current_node._other_nodes:
        split_addr =  ip.split(".")
        split_addr_curr =  current_node._ip.split(".")

        # Send election to greater IPs
        if (split_addr > split_addr_curr):
            election = f'http://{ip}:{current_node._port}/election'
            response = requests.post(election, verify=False, timeout=config.TIMEOUT)
            if response.status_code == 200:
                at_least_one_response = True
    
    if not at_least_one_response:
        # Set as coordinator
        current_node.set_coordinator()

def set_colors(current_node):
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
        print("Cannot set colors no nodes.")
    