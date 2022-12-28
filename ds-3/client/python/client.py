#
# Zookeeper client demo 1
#
# Basic client listing children of a node.

import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, jsonify, request
from flask import render_template, send_from_directory
from kazoo.client import KazooClient
from werkzeug.utils import secure_filename

from communication import ask_root_for_parent, ask_parent_for_key, ask_parent_for_put, ask_parent_for_delete
from config import DEFAULT_PORT
from tree_node import Node
from zookeeper import register

# =================== [Global variables] ===================
app = Flask(__name__)
root_ip_addr = None
node_ip_addr = None
parent_ip_addr = None
root_node = Node(None, parent_ip_addr)
local_cache = {}

spec = APISpec(
    title='KIV-DS',
    version='1.0.0',
    openapi_version='3.0.3',
    description='Distributed Cache API',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)


@app.route('/draw-tree', methods=['GET'])
def draw_tree():
    return jsonify(root_node.printTree(root_node, 0)), 200


@app.route('/get-details', methods=['GET'])
def get_details():
    return jsonify({
        'isRoot': root_ip_addr == node_ip_addr,
        'host': str(node_ip_addr),
        'parent': str(parent_ip_addr),
        'local_cache': local_cache
    }), 200


@app.route('/find_parent', methods=['GET'])
def find_parent():
    """Ask Root node for parent IP address
           ---
           get:
              tags:
                - Cache
              description: Ask Root node for parent IP address
              operationId: find_parent
              parameters:
                - in: query
                  name: ip
                  schema:
                    type: string
                  description: Node IP address
              responses:
                '200':
                  description: OK
                '400':
                  description: Invalid IP parameter
           """
    new_node_ip_addr = request.args.get('ip')
    parent_ip = root_node.insert(new_node_ip_addr)
    return jsonify(parent_ip), 200


@app.route('/api/swagger.json')
def create_swagger_spec():
    return jsonify(spec.to_dict())


@app.route('/cache', methods=['GET'])
def get_val():
    """Get key value
       ---
       get:
          tags:
            - Cache
          description: Get key value
          operationId: get_val
          parameters:
            - in: query
              name: key
              schema:
                type: string
              description: Key value
          responses:
            '200':
              description: OK
            '400':
              description: Invalid key parameter
            '404':
              description: No value exists for entered key
       """

    key = request.args.get('key')

    if key is None:
        return "Invalid key parameter", 400

    # Key exist in local cache
    if key in local_cache.keys():
        return jsonify(local_cache[key]), 200

    if parent_ip_addr is None:
        return "No value exists for entered key", 404

    # Find key in parent cache
    if parent_ip_addr is not None:
        response = ask_parent_for_key(parent_ip_addr, DEFAULT_PORT, key)
        if response is not None:
            # Save value to local cache
            local_cache[key] = response
            return jsonify(response), 200

    return "No value exists for entered key", 404


@app.route('/cache', methods=['DELETE'])
def delete_val():
    """Delete value
           ---
           delete:
              tags:
                - Cache
              description: Delete value
              operationId: delete_val
              parameters:
                - in: query
                  name: key
                  schema:
                    type: string
                  description: Key value
              responses:
                '200':
                  description: OK
                '400':
                  description: Invalid key parameter
                '404':
                  description: No value exists for entered key
           """

    key = request.args.get('key')

    if key is None:
        return "Invalid key parameter", 400

    # Remove value from a local cache
    removed = local_cache.pop(key, None)

    # Send update to parent
    if parent_ip_addr is not None:
        ask_parent_for_delete(parent_ip_addr, DEFAULT_PORT, key)

    return "OK", 200


@app.route('/cache', methods=['PUT'])
def put_key_val():
    """Add new key-value record
          ---
          put:
              tags:
                - Cache
              description: Add new key-value record
              operationId: put_key_val
              parameters:
                - in: query
                  name: key
                  schema:
                    type: string
                  description: Key value
                - in: query
                  name: value
                  schema:
                    type: string
                  description: Value which is stored in key
              responses:
                '200':
                  description: OK
                '400':
                  description: Invalid key or value parameters
              """

    key = request.args.get('key')
    val = request.args.get('value')

    if key is None or val is None:
        return "Invalid key or value parameters", 400

    # Save value into a local cache
    local_cache[key] = val

    # Send update to parent
    if parent_ip_addr is not None:
        ask_parent_for_put(parent_ip_addr, DEFAULT_PORT, key, val)

    return "OK", 200


@app.route('/docs')
@app.route('/docs/<path:path>')
def swagger_docs(path=None):
    if not path or path == 'index.html':
        return render_template('index.html', base_url='/docs', ip=node_ip_addr)
    else:
        return send_from_directory('static', secure_filename(path))


with app.test_request_context():
    spec.path(view=get_val)
    spec.path(view=delete_val)
    spec.path(view=put_key_val)

if __name__ == '__main__':
    ensemble = os.environ['ZOO_SERVERS']
    root_ip_addr = os.environ['ROOT_IP']
    node_ip_addr = os.environ['NODE_IP']

    if root_ip_addr == node_ip_addr:
        root_node.ip_addr = node_ip_addr
    else:
        # Notify root
        parent_ip_addr = ask_root_for_parent(root_ip_addr, DEFAULT_PORT, node_ip_addr)

    print(f'*** Zookeeper IP address: {ensemble}', flush=True)
    print(f'*** Node is root: {root_ip_addr == node_ip_addr}', flush=True)
    print(f'*** Root node ip address: {root_ip_addr}', flush=True)
    print(f'*** Node ip address: {node_ip_addr}', flush=True)
    print(f'*** Node parent ip address: {node_ip_addr}', flush=True)

    # Create the client instance
    zk = KazooClient(hosts=ensemble)
    # Start a Zookeeper session
    zk.start()

    register(zk, node_ip_addr, parent_ip_addr)

    app.run(host=str(node_ip_addr))
