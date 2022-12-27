#
# Zookeeper client demo 1
#
# Basic client listing children of a node.

import os
import pprint as pp

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, jsonify, render_template, send_from_directory
from marshmallow import Schema, fields
from werkzeug.utils import secure_filename

from flask import Flask, jsonify, request
from kazoo.client import KazooClient


app = Flask(__name__)

spec = APISpec(
    title='KIV-DS',
    version='1.0.0',
    openapi_version='3.0.3',
    description='Distributed Cache API',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)


@app.route('/api/swagger.json')
def create_swagger_spec():
    return jsonify(spec.to_dict())


@app.route('/cache/', methods=['GET'])
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
    return "OK2", 200


@app.route('/cache/', methods=['DELETE'])
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
    return "OK3", 200


@app.route('/cache/', methods=['PUT'])
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
    return "OK4", 200


with app.test_request_context():
    spec.path(view=get_val)
    spec.path(view=delete_val)
    spec.path(view=put_key_val)


@app.route('/docs')
@app.route('/docs/<path:path>')
def swagger_docs(path=None):
    if not path or path == 'index.html':
        return render_template('index.html', base_url='/docs')
    else:
        return send_from_directory('static', secure_filename(path))


# def main():
#     ensemble = os.environ['ZOO_SERVERS']
#     print(f"Client will use these servers: {ensemble}.")
#     # Create the client instance
#     zk = KazooClient(hosts=ensemble)
#     # Start a Zookeeper session
#     zk.start()
#
#     # List node children
#     children = zk.get_children("/ds")
#     pp.pprint(children)
#
#     # Close the session
#     zk.stop()


if __name__ == '__main__':
    app.run(host="localhost")
