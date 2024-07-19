# coding: utf-8
from flask import Flask, request, Response
from threading import Lock
import json
from jsonrpcserver import dispatch, method, Result, Success, Error
from jsonrpcclient import parse, Ok
from jsonrpcclient import request as request2
import requests
from hash import ConsistentHash
from cache import Cache
import os

app = Flask(__name__)  # 初始化Flask
lock = Lock()  # 初始化锁
cache = Cache()  # 初始化缓存
self_addr = None  # 节点地址
servers = ['http://sdcs0:80', 'http://sdcs1:80', 'http://sdcs2:80']  # 分布式节点列表
consistent_hash = ConsistentHash(servers)  # 初始化一致性哈希


@method
def get_remote(key) -> Result:
    """从远程获取key对应的value
    :param key: 键
    :return: 包含value的Result

    """
    value = cache.get(key)  # 从本地获取
    if value is not None:
        return Success(cache.get(key))
    else:
        return Error(-32000, "Key not found at this server")


@method
def set_remote(key, value) -> Result:
    """设置远程的key-value
    :param key: 键
    :param value: 值
    :return: 包含设置结果的Result
    """
    with lock:  # 获取锁
        cache.set(key, value)  # 设置key-value
    return Success("Set successfully")


@method
def delete_remote(key) -> Result:
    """
    删除远程的key
    :param key: 键
    :return: 包含删除结果的Result
    """
    with lock:  # 获取锁
        result = cache.delete(key)  # 删除key
    return Success(result)


@app.route('/<key>')
def get(key):
    """
    获取key对应的value
    :param key: 键
    :return: 包含value的Response
    """
    targetServer = consistent_hash.get_node(key)  # 获取目标服务器
    if self_addr == targetServer:  # 如果目标服务器是本机
        value = cache.get(key)
    else:  # 如果目标服务器不是本机
        value = call_rpc(targetServer, 'get_remote', {"key": key})  # 调用远程的jsonrpc
    if value is None:
        return Response(status=404)
    else:
        return json.dumps({key: value})


@app.route('/', methods=['POST'])
def set():
    """
    设置key-value
    :request data: json格式的数据，包含key和value
    :return:
    """
    data = request.get_json()
    for key, value in data.items():  # 遍历data中的每一个key-value
        targetServer = consistent_hash.get_node(key)  # 获取目标服务器
        if self_addr == targetServer:  # 如果目标服务器是本机
            with lock:  # lock the cache
                cache.set(key, value)
        else:
            call_rpc(targetServer, 'set_remote', {"key": key, "value": value})  # 调用远程的jsonrpc

    return Response(status=200)


@app.route('/<key>', methods=['DELETE'])
def delete(key):
    """
    删除key
    :param key: 待删除的key
    :return: 删除的key的数量
    """
    target_server = consistent_hash.get_node(key)  # 获取目标服务器
    if self_addr == target_server:
        with lock:
            num = cache.delete(key)
    else:
        num = call_rpc(target_server, 'delete_remote', {"key": key})
    return num


@app.route('/rpc', methods=['POST'])
def jsonrpc():
    """
    统一处理jsonrpc请求
    :return: 请求结果
    """
    return Response(
        dispatch(request.get_data().decode()), content_type="application/json"
    )


def call_rpc(target_server, method: str, params):
    """
    调用远程的jsonrpc
    :param target_server: 目标服务器的地址
    :param method: 远程调用的方法名
    :param params: 远程调用的参数
    :return: 远程调用的结果
    """
    requests.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()  # 创建session对象
    s.keep_alive = False  # 不保持连接
    response = requests.post(target_server + "/rpc", json=request2(method, params=params))  # 发送请求
    parsed = parse(response.json())  # 解析结果
    if isinstance(parsed, Ok):  # 解析成功
        return parsed.result
    else:
        # print(parsed.message)
        return None  # 解析失败


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description="start setting")
    # parser.add_argument('--id',dest='id',type=int)
    # parser.add_argument('--port',dest='port',type=int)
    # args = parser.parse_args()
    selfId = os.environ.get('id', 0)
    self_addr = 'http://sdcs' + str(selfId) + ':80'
    app.run(host='0.0.0.0', port=80, debug=False)
