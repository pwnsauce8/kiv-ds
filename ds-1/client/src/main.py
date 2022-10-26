from flask import Flask, jsonify, request   
import socket   
import sys      
from threading import Thread    
from node import Node   
from election import start, handle_coordinator, check_nodes
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
    return jsonify(current_node.get_info()), 200

# -----[POST methods]-----

@app.route('/node-is-dead', methods=['POST'])
def remove_node():
    Thread(target=check_nodes, args=(current_node, )).start()
    return "OK", 200

@app.route('/hello', methods=['POST'])
def hello():
    current_node.add_node(request.remote_addr)
    return jsonify(current_node.get_info()), 200

@app.route('/set-coordinator', methods=['POST'])
def set_coordinator():
    # remove current coordinator
    current_node.unset_coordinator()
    current_node.set_coordinator_ip(request.remote_addr)
    Thread(target=handle_coordinator, args=(current_node, )).start()
    return "OK", 200

@app.route('/election', methods=['POST'])
def election():
    return "OK", 200

@app.route('/set-color-green', methods=['POST'])
def set_color_green():
    current_node.set_color(config.NodeColor.GREEN)
    return "OK", 200

@app.route('/set-color-red', methods=['POST'])
def set_color_red():
    current_node.set_color(config.NodeColor.RED)
    return "OK", 200

if __name__ == '__main__':
    app.run(host=current_node._ip)

# EOF
