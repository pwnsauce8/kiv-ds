from flask import Flask, request
from views import HTML_START, HTML_END

app = Flask(__name__)

DEFAULT_PORT = 5000
# Open config
config = open('/opt/lookup/config.ini', 'r')
lines = config.readlines()
config.close()

# Read lines and save nodes
nodes = []
for line in lines:
    line = line.strip()
    info = a.split(',')
    if line != '':
        if line not in nodes:
            nodes[info[0].strip()] = info[1].strip()
        else:
            print('Cannot read config file. Exit.')
            break

def create_table():
    response = HTML_START

    response = response + "<table><tr><th>Name</th><th>IP</th><th>Is coordinator</th><th>Color</th></tr>"
    for node in nodes.items():
        # Get details
        response = requests.get(f'http://{node[0]}:{DEFAULT_PORT}/get-details', verify=False, timeout=0.5)
            if response.status_code == 200:
                data = response.json()
                response = response + f'<tr><td>{node[0]}</td><td>{node[1]}</td><td>{data['isCoordinator']}</td><td style="color:{data['color']};">{data['color']}</td></tr>'
            else
                response = response + f'<tr><td>{node[0]}</td><td>{node[1]}</td><td>NONE</td><td>NONE</td></tr>'
    
    # Close table
    response = response + "</table>" + HTML_END


