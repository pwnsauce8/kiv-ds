from distutils.command.config import config
from flask import Flask, request
import socket
from threading import Thread
from node import Node
from election import start
import config as config

app = Flask(__name__)

# Create node instance
current_node = Node()
# Create parallel process
Thread(target=start, args=(current_node, )).start()

# -----[GET methods]-----

@app.route('/is-alive', methods=['GET'])
def is_alive():
    return "OK", 200

@app.route('/get-details', methods=['GET'])
def get_details():
    current_node.get_info()

# -----[POST methods]-----

@app.route('/hello', methods=['POST'])
def hello():
    return "OK", 200

@app.route('/set-coordinator', methods=['POST'])
def set_coordinator():
    # remove current coordinator
    if current_node._isCoordinator:
        current_node.set_coordinator_ip(request.remote_addr)

@app.route('/election', methods=['POST'])
def election():
    return "OK", 200

@app.route('/set-color-green', methods=['POST'])
def set_color_green():
    current_node.set_color(config.NodeColor.GREEN)

@app.route('/set-color-red', methods=['POST'])
def set_color_red():
    current_node.set_color(config.NodeColor.RED)

if __name__ == '__main__':
    app.run(host=current_node._ip)

# EOF
