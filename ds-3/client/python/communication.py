import requests

import config


def ask_root_for_parent(root_ip_addr, port, node_ip_addr):
    message = f'http://{root_ip_addr}:{port}/find_parent?ip={node_ip_addr}'
    response = requests.get(message, verify=False, timeout=config.TIMEOUT)
    if response.status_code == 200:
        return response.json()
    return None


def ask_parent_for_key(dest_ip_addr, port, key):
    message = f'http://{dest_ip_addr}:{port}/cache?key={key}'
    response = requests.get(message, verify=False, timeout=config.TIMEOUT)
    if response.status_code == 200:
        return response.json()
    return None


def ask_parent_for_put(dest_ip_addr, port, key, val):
    message = f'http://{dest_ip_addr}:{port}/cache?key={key}&value={val}'
    requests.put(message, verify=False, timeout=config.TIMEOUT)


def ask_parent_for_delete(dest_ip_addr, port, key):
    message = f'http://{dest_ip_addr}:{port}/cache?key={key}'
    requests.delete(message, verify=False, timeout=config.TIMEOUT)
