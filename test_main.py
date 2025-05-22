import json
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_load():
    # 读取 resource/load.json 文件的内容
    with open('resource/load.json', 'r') as file:
        data = json.load(file)

    # 发送 POST 请求到 /load 端点
    response = client.post("/load", json=data)

    # 断言响应状态码为 200
    assert response.status_code == 200

    # 根据需要添加更多的断言
    # 例如，检查响应内容
    # assert response.json() == expected_response


def test_load_v2():
    # 读取 resource/load.json 文件的内容
    with open('resource/simulation_config_v2.json', 'r') as file:
        data = json.load(file)

    # 发送 POST 请求到 /load 端点
    response = client.post("/calc_load_v2", json=data)

    # 断言响应状态码为 200
    assert response.status_code == 200

    # 根据需要添加更多的断言
    # 例如，检查响应内容
    # assert response.json() == expected_response
