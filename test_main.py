# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import json
from eth_account import Account, messages
import sha3
import yaml
import time
import pytest
import allure
import os
import urllib3

# @classmethod
# def setup_class(self):
#     self.dataNone = None
#     self.from_index = 0
#     self.to_index = 1

class initData:
    def __init__(self):
        self.data = None
        self.from_index = 0
        self.to_index = 1

    def yaml_data(self):

        if self.data is None:
            with open('multiChain.yaml', 'r') as file:
                self.data = yaml.load(file, Loader=yaml.SafeLoader)

        # 对于单个交易对的情况，根据当前索引返回相应的对
        if len(self.data['from']) == 1 and len(self.data['to']) == 1:
            self.data['from'], self.data['to'] = self.data['to'], self.data['from']

            print(self.data['from'][0], self.data['to'][0])
            print("这是单个交易对")

            data = {
                'from_item': self.data['from'][0],
                'to_item': self.data['to'][0],
                'data': self.data
            }

            return data

        else:
            # 对于多个对的情况，根据当前索引返回相应的对
            from_item = self.data['from'][self.from_index]
            to_item = self.data['to'][self.to_index]

            # 更新索引以获取下一对
            self.from_index = (self.from_index + 1) % len(self.data['from'])
            self.to_index = (self.to_index + 1) % len(self.data['to'])
            print("这是多个交易对")
            print(from_item, to_item)

            data = {
                'from_item': from_item,
                'to_item': to_item,
                'data': self.data
            }

            return data

@pytest.fixture
def data():
    Testapi = initData()
    return Testapi.yaml_data()

# def test_change_chain(self, swapStatus, chain):
#     time.sleep(5)
#     if 'from' in chain:
#         print(chain['from'])
#
#         # 交换 from 和 to 字段的值
#         chain["from"], chain["to"] = chain["to"], chain["from"]
#
#         # 如果 chain['from'] 的值为 "avax:usdc"，则修改 single.yaml 文件
#         if chain["from"] == "avax:usdc":
#             # 将修改后的数据写回 single.yaml 文件
#             with open('single.yaml', 'w') as file:
#                 yaml.dump(chain, file, default_style='"')
#         else:
#             # 如果 chain['from'] 的值不是 "avax:usdc"，则修改 from 和 to 字段的值为对应的值
#             # 这里可以根据具体情况修改
#             chain["from"] = "avax:usdc"
#             chain["to"] = "polygon:usdc"
#
#         # 输出修改后的 from 和 to 字段的值
#         print(f"New 'from' value: {chain['from']}")
#         print(f"New 'to' value: {chain['to']}")
#     else:
#         print("Key 'from' not found in the 'chain' dictionary.")


def test_list_supported_chains():
    # url = "https://relayer.meson.fi/api/v1/list"
    url = "https://relayer.meson.fi/api/v1/list"
    payload = {}
    headers = {
        'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)


@allure.title("get_price")
def test_get_price(data):
    # print("from为："+data['from_item'])
    #print(data)
    data_dict = data['data']
    url = data['data']['interface'] + "api/v1/price"

    payload = json.dumps({
        "from": data['from_item'],
        "to": data['to_item'],
        "amount": data_dict['amount'],
        "fromAddress": data_dict['address-from']
    })
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    urllib3.disable_warnings()

    try:
        result = response.json()
        print(result)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON response.")


@allure.title("encode_swap")
def test_encode_swap(data):
    data_dict = data['data']
    # url = "https://relayer.meson.fi/api/v1/swap"
    url = data['data']['interface'] + "api/v1/swap"

    payload = json.dumps({
        "from": data['from_item'],
        "to": data['to_item'],
        "amount": data_dict['amount'],
        "fromAddress": data_dict['address-from'],
        "recipient": data_dict['address-to'],
        "dataToContract": ""
    })
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    urllib3.disable_warnings()
    #print(response)
    data = response.json()
    # print(data)
    result = data['result']
    return result

@pytest.fixture
def result():
    result = test_encode_swap(data)
    return result

@allure.title("submit swap signatures")
def test_submit_swap_signatures(data, result):
    # print(data)
    # print(result)
    data_dict = data['data']
    private_key = data_dict['private-key']
    # 假设第一条哈希的十六进制字符串
    hash_hex_0 = result['dataToSign'][0]['message']
    hash_hex_1 = result['dataToSign'][1]['message']

    # 将第一条哈希转换为字节串
    hash_bytes_0 = bytes.fromhex(hash_hex_0[2:])
    hash_bytes_1 = bytes.fromhex(hash_hex_1[2:])

    # 计算 keccak256 哈希

    keccak_hash0 = sha3.keccak_256(hash_bytes_0).digest()
    keccak_hash1 = sha3.keccak_256(hash_bytes_1).digest()

    # 将 keccak256 哈希转换回十六进制字符串
    hash0 = keccak_hash0.hex()
    hash1 = keccak_hash1.hex()
    if (
            hash0 != result['dataToSign'][0]['hash'][2:] or
            hash1 != result['dataToSign'][1]['hash'][2:]
    ):
        raise ValueError('Invalid hash')

    account = Account.from_key(private_key)
    sig0 = account.signHash(keccak_hash0)
    sig1 = account.signHash(keccak_hash1)

    sig0_serialized = sig0.signature.hex()
    sig1_serialized = sig1.signature.hex()

    return sig0_serialized, sig1_serialized, result['encoded']


@allure.title("submit swap")
def test_submit_swap(hash1, hash2, encoded, data):
    data_dict = data['data']
    # print(encoded)
    # print(data)
    # url = "https://relayer.meson.fi/api/v1/swap/:encoded"
    url = data['data']['interface'] + "api/v1/swap/" + encoded

    payload = json.dumps({
        "fromAddress": data_dict['address-from'],
        "recipient": data_dict['address-to'],
        "signatures": [
            "" + hash1 + "",
            "" + hash2 + ""
        ],
        "signer": data_dict['address-from']
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    urllib3.disable_warnings()
    # print(response.text)

    d = response.json()
    swapId = d['result']['swapId']
    print(swapId)
    return swapId

    # 可以在这里进行断言或其他逻辑
    # assert swap_id is not None



def test_check_status(swapId, data):
    # time.sleep(10)
    # url = "https://relayer.meson.fi/api/v1/swap/:swapId"
    url = data['data']['interface'] + "api/v1/swap/" + swapId
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    while True:
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        urllib3.disable_warnings()
        data = response.json()
        # print(data)
        # 这里可以添加一些等待的逻辑，可以使用time.sleep()等方法
        # 这样测试用例会在检查失败的情况下持续重复执行，直到满足条件为止
        # 检查交易状态是否为 "EXECUTED"，如果是则跳出循环
        if "EXECUTED" in data["result"]:
            print(data["result"])
            return data["result"]


# 在这里调用 test_submit_swap() 并传递参数
# def test_submit_swap_execution():
#     Testapi = initData()
#     data = Testapi.yaml_data()
#     test_get_price(data)
#     test_encode_swap(data)
#     swapInfo = test_encode_swap(data)
#     test_submit_swap_signatures(swapInfo, data)
#     sig0, sig1, encoded = test_submit_swap_signatures(swapInfo, data)
#     swap_id = test_submit_swap(sig0, sig1, encoded)
#     test_check_status(swap_id)



if __name__ == '__main__':
    import pytest

    count = 0  # 初始化计数器为 0
    stop = False  # 终止执行
    Testapi = initData()
    # data = Testapi.yaml_data()
    # data = Testapi.yaml_data()

    # 在循环之前先执行一次获取价格的操作
    # test_get_price()
    while not stop:
        # for _ in range(num_pairs):
        # Testapi = TestApi()
        #Testapi = initData()
        count += 1  # 每次执行测试用例后计数器加一
        print(f"执行第 {count} 次测试用例")

        data = Testapi.yaml_data()
        num_pairs = min(len(data['data']['from']), len(data['data']['to']))
        test_list_supported_chains()
        test_get_price(data)
        print(f"num_pairs: {num_pairs}, repetition: {Testapi.data['repetition']}")
        swapInfo = test_encode_swap(data)
        test_submit_swap_signatures(data, swapInfo)
        sig0, sig1, encoded = test_submit_swap_signatures(data, swapInfo)
        swapId = test_submit_swap(sig0, sig1, encoded, data)
        swapStatus = test_check_status(swapId, data)
        # 更新索引以获取下一对
        if count >= num_pairs and Testapi.data['repetition'] == "No":
            stop = True
            break
    # time.sleep(20)
    # if stop:
    #     break