import os
from flask import Flask, request, json
import requests

app = Flask(__name__)
url = "http://host.docker.internal:8079/api/order"

def make_response(code, message, data={}):
    is_success = True
    if code != 200:
        is_success = False
    response = {
        "success": is_success,
        "message": message,
    }
    if data != {}:
        response['data'] = data

    return response

@app.route('/check', methods=['GET'])
def check_connection():
   return "Server Running!"

@app.route('/order', methods=['POST'])
def post_order():
    header = request.headers
    request_data = json.loads(request.data)
    print(request_data)
    response = requests.post(url, headers={'Authorization': header.get('Authorization')}, data=json.dumps(request_data))
    data = {}
    res = response.json()
    if res.get('data'):
        data = res.get('data')
    return make_response(response.status_code, res.get('message'), data)

@app.route('/order/<int:order_id>', methods=['GET', 'PUT'])
def get_put_order(order_id):
    print(url)
    header = request.headers
    if request.method == 'GET':
        response = requests.get(url+'/%s'%(order_id), headers={'Authorization': header.get('Authorization')},)
        data = {}
        res = response.json()
        if res.get('data'):
            data = res.get('data')
        return make_response(response.status_code, res.get('message'), data)
    if request.method == 'PUT':
        request_data = json.loads(request.data)
        response = requests.put(url+'/%s'%(order_id) % (order_id), headers={'Authorization': header.get('Authorization')}, data=json.dumps(request_data))
        data = {}
        res = response.json()
        if res.get('data'):
            data = res.get('data')
        return make_response(response.status_code, res.get('message'), data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
