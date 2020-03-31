from flask import Flask, request, Response
import jsonpickle
import json

from main import RedisWrapper

global redis_object
app = Flask(__name__)

@app.route("/api/ping", methods=['POST'])
def hello():
    response = jsonpickle.encode({ 'ping': 'pong' })
    return Response(response=response, status=200, mimetype="application/json")

@app.route("/api/getAll", methods=['GET'])
def keys():
    '''
        Return keys
    '''
    try:
        keys = redis_object.getAll()
        scan_keys = list()
        print('Keys: ', keys)
        for key in keys:
            print('String: ', key.decode)
            scan_keys.append(key)
        response = {
            'keys': scan_keys
        }
        return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")
    except Exception as e:
        response = {
            'trace': e,
            'error': True
        }
        return Response(response=jsonpickle.encode(response), status=500, mimetype="application/json")

@app.route("/api/fetch/<key>", methods=['GET'])
def fetchKey(key):
    '''
        Fetch a particular key in Redis
    '''
    try:
        value = redis_object.fetchValue(key)
        response = {
            'key': key,
            'value': value
        }
        return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")
    except Exception as e:
        response = {
            'trace': e,
            'error': True
        }
        return Response(response=jsonpickle.encode(response), status=500, mimetype="application/json")

@app.route('/api/set', methods=['POST'])
def setKeyValue():
    '''
        Set Key-Value Pair
    '''  
    r = request.get_json()
    print('Request received: ', r)
    try:
        print('R: ', r)
        key = r['key']
        value = r['value']
        print('Key: ', key)
        print('Value: ', value)
        redis_object.setValue(key, value)

        response = {
            'status': True,
            'key': key,
            'value': value
        }
        return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")
    except Exception as e:
        print('Error: ', e)
        response = {
            'trace': e,
            'error': True
        }
        return Response(response=jsonpickle.encode(response), status=500, mimetype="application/json")


@app.route('/api/join', methods=['POST'])
def nodeJoin():
    '''
        A Node joins the network
        Input: IP
        TODO: In future, stats about what resources this node can offer
        TODO: Implement Heartbeat and update Redis
    '''
    try:
        r = request.get_json()
        print('R: ', r)
        ip = r['ip']
        availableNodes = redis_object.availableNodes()
        print('Available Nodes: ', availableNodes)
        
        if availableNodes is not None:
            nodeList = json.loads(availableNodes)
            print('Node List: ', nodeList)
            print('Nodelist type: ', type(nodeList))
            if ip not in nodeList:
                nodeList.append(ip)

            redis_object.setValue("nodes", json.dumps(nodeList))
            
        else:
            nodeList = list()
            nodeList.append(ip)
            print('NodeList: ', nodeList)
            nodeList_string = json.dumps(nodeList)
            redis_object.setValue("nodes", nodeList_string)

        response = {
            'nodes': nodeList
        }
        return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")
    except Exception as e:
        print('E: ', e)
        response = {
            'trace': e,
            'error': True
        }
        return Response(response=jsonpickle.encode(response), status=500, mimetype="application/json")

if __name__ == "__main__":
    redis_object = RedisWrapper("0.0.0.0", "6379")
    app.run()