from urllib import response
from flask import Flask, request
import netifaces as ni
import requests
import socket
from ipaddress import IPv4Interface
from views import HTML_START, HTML_END

app = Flask(__name__)

DEFAULT_PORT = 5000
# Open config
config = open('/opt/lookup/config.conf', 'r')
lines = config.readlines()
config.close()

node_count = lines[0].strip()

def create_table():
    response = "<table><tr><th>Name</th><th>IP</th><th>Is coordinator</th><th>Color</th></tr>"
    interface_address = ni.ifaddresses("eth0")[ni.AF_INET][0]
    addr = interface_address['addr']
    mask = interface_address['netmask']
    interface = IPv4Interface(f'{addr}/{mask}')
    for i in range(int(node_count) + 3):
        try:
            resp = requests.get(f'http://{interface.network[i]}:{DEFAULT_PORT}/get-details', verify=False, timeout=0.5)
            if resp.status_code == 200:
                data = resp.json()
                response = response + f"<tr><td>{data['hostname']}</td><td>{interface.network[i]}</td><td>{data['isCoordinator']}</td><td style=\"color:{data['color']};\">{data['color']}</td></tr>"
        except:
            continue
    
    # Close table
    response = response + "</table>"
    return response

def table():
    interfaces = ni.interfaces()
    response = ''
    for i in range(3):
        try:
            host = socket.gethostbyname(f'node-{str(i)}')
            response = response + f"<h3>{str(host)}</h3>"
        except:
            continue
    return response


def table2():
    interfaces = ni.interfaces()
    response = ''      

    for i in interfaces:
        interface_address = ni.ifaddresses(i)[ni.AF_INET]
        for intaddr in interface_address:
            addr = intaddr['addr']
            mask = intaddr['netmask']
            interface = IPv4Interface(f'{addr}/{mask}')
            response = response + f"<h3>{i} - {str(interface)}</h3>"
    return response        

def table3():
    interfaces = ni.interfaces()
    response = ''      
    interface_address = ni.ifaddresses("eth0")[ni.AF_INET][0]
    addr = interface_address['addr']
    mask = interface_address['netmask']
    interface = IPv4Interface(f'{addr}/{mask}')
    for intaddr in interface.network:
        response = response + f"<h3>eth0 - {str(intaddr)}</h3>"  
        
    return response     

@app.route('/info', methods=['GET'])
def get_view():
    return HTML_START + create_table() + HTML_END

@app.route('/info2', methods=['GET'])
def get_view2():
    return HTML_START + table3() + HTML_END

if __name__ == '__main__':
    app.run(host='0.0.0.0')