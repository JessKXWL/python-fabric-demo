import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from test.integration.e2e_sdk import E2eSDK
import asyncio
import json
from flask import Flask, jsonify, request

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# def main():
#     loop = asyncio.get_event_loop()
#     h = E2eSDK()
#     # try:
#     h.setUp()
#     print("通道建立")
#     loop.run_until_complete(h.channel_create())
#     print("通道加入")
#     loop.run_until_complete(h.channel_join())
#     print("链码安装")
#     loop.run_until_complete(h.chaincode_install())
#     print("链码初始化")
#     loop.run_until_complete(h.chaincode_instantiate())
#     time.sleep(1)
#     print("数据添加")
#     response = loop.run_until_complete(h.chaincode_invoke(['add', '{\"identifier\": \"client1_to_rsu1_epoch1\",\"data\": {\"enc_vectors\": \"enc_vectors1\",\"dec_aes_key\": \"dec_aes_key\",\"loss_slice\": \"loss_slice\"}}']))
#     print(response)
#     print("数据查询")
#     response = loop.run_until_complete(h.chaincode_query(['query', 'client1_to_rsu1_epoch1']))
#     print(response)
#     print("数据更新")
#     response = loop.run_until_complete(h.chaincode_invoke(['update', '{\"identifier\": \"client1_to_rsu1_epoch1\",\"data\": {\"enc_vectors\": \"enc_vectors1_update\",\"dec_aes_key\": \"dec_aes_key_update\",\"loss_slice\": \"loss_slice_update\"}}']))
#     print(response)
#     print("数据查询")
#     response = loop.run_until_complete(h.chaincode_query(['query', 'client1_to_rsu1_epoch1']))
#     print(response)
#     print("关闭网络")
#     # except Exception as e:
#     #     logger.info("E2E: Chaincode query start")
#     # h.tearDown()

loop = asyncio.get_event_loop()
h = E2eSDK()
# try:
h.setUp()
print("通道建立")
loop.run_until_complete(h.channel_create())
print("通道加入")
loop.run_until_complete(h.channel_join())
print("链码安装")
loop.run_until_complete(h.chaincode_install())
print("链码初始化")
loop.run_until_complete(h.chaincode_instantiate())
time.sleep(1)

app = Flask(__name__)

@app.route('/api/new', methods=['POST'])
def add():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['identifier', 'data']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # create a new transaction
    response = loop.run_until_complete(h.chaincode_invoke(['add', json.dumps(values)]))
    if response == "信息添加成功":
        return jsonify(response), 201
    return jsonify(response), 400

@app.route('/api/update', methods=['PUT'])
def update():
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['identifier', 'data']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # create a new transaction
    response = loop.run_until_complete(h.chaincode_invoke(['update', json.dumps(values)]))
    if response == "信息更新成功":
        return jsonify(response), 201
    return jsonify(response), 400

@app.route('/api/query', methods=['GET'])
def query():
    try:
        values = request.args.get('identifier')
    except Exception as e:
        return {"message": e}, 400
    response = loop.run_until_complete(h.chaincode_query(['query', values]))
    if check_json(response):
        return json.loads(response, encoding='utf-8'), 200
    return response, 400

def check_json(msg):
    if isinstance(msg, str):  # 首先判断变量是否为字符串
        try:
            json.loads(msg, encoding='utf-8')
        except ValueError:
            return False
        return True
    else:
        return False


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)