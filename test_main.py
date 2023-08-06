# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import json

from eth_account import Account, messages

import sha3
import yaml
from collections import deque
import time
import allure
import subprocess


class api:
    def __init__(self):
        self.data = None
        self.from_index = 0
        self.to_index = 1

    def test_yaml_data(self):
        if self.data is None:
            with open('rotationChain.yaml', 'r') as file:
                self.data = yaml.load(file, Loader=yaml.SafeLoader)

        # Get the 'from' and 'to' elements based on the current indices
        from_item = self.data['from'][self.from_index]
        to_item = self.data['to'][self.to_index]

        # Update the indices for the next pair
        self.from_index = (self.from_index + 1) % len(self.data['from'])
        self.to_index = (self.to_index + 1) % len(self.data['to'])

        return {
            'from_item': from_item,
            'to_item': to_item,
            'data': self.data
        }

    def list_supported_chains(self):
        # url = "https://relayer.meson.fi/api/v1/list"
        url = "https://relayer.meson.fi/api/v1/list"

        payload={}
        headers = {
          'Accept': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

    def test_get_price(self, data):

        data_dict = data['data']

        # url = "https://relayer.meson.fi/api/v1/price"
        url = "https://relayer.meson.fi/api/v1/price"

        payload = json.dumps({
            "from": data['from_item'],
            "to": data['to_item'],
            "amount": data_dict['amount'],
            "fromAddress": data_dict['address-from']
        })
        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        try:
            result = response.json()
            print(result)
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON response.")

    def test_encode_swap(self, data):
        data_dict = data['data']
        # url = "https://relayer.meson.fi/api/v1/swap"
        url = "https://relayer.meson.fi/api/v1/swap"

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

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        data = response.json()
        print(data)
        result = data_dict['result']

        print(result)

        return result



    def test_submit_swap_signatures(self, result, data):
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

        # 创建一个 Ethereum message 对象
        # message_0 = messages.encode_defunct(keccak_hash0)
        # message_1 = messages.encode_defunct(keccak_hash1)

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



    def test_submit_swap(self, hash1, hash2, encoded, data):
        data_dict = data['data']
        # url = "https://relayer.meson.fi/api/v1/swap/:encoded"
        url = "https://relayer.meson.fi/api/v1/swap/" + encoded

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

        response = requests.request("POST", url, headers=headers, data=payload)

        # print(response.text)
        data = response.json()
        swapId = data['result']['swapId']
        print(swapId)
        return swapId

    def test_check_status(self, swapId):
        # time.sleep(10)
        # url = "https://relayer.meson.fi/api/v1/swap/:swapId"
        url = "https://relayer.meson.fi/api/v1/swap/" + swapId
        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }


        while True:
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            # print(data)
            # 这里可以添加一些等待的逻辑，可以使用time.sleep()等方法
            # 这样测试用例会在检查失败的情况下持续重复执行，直到满足条件为止
            # 检查交易状态是否为 "EXECUTED"，如果是则跳出循环
            if "EXECUTED" in data["result"]:
                print(data["result"])
                return data["result"]
        time.sleep(3)
        # assert "EXECUTED" in data["result"]
        # print(data['result'])

    def test_change_chain(self, swapStatus, chain):
        time.sleep(5)
        # print(swapStatus["EXECUTED"])
        print(chain["from"])

        # 如果 chain['from'] 的值为 "avax:usdc"，则修改 input.yaml 文件
        if chain.get("from") == "avax:usdc":
            with open('input.yaml', 'r') as file:
                data = yaml.load(file, Loader=yaml.SafeLoader)
                # 修改 from 和 to 字段的值
                data['from'] = "polygon:usdc"
                data['to'] = "avax:usdc"
            # 将修改后的数据写回 input.yaml 文件
            with open('input.yaml', 'w') as file:
                yaml.dump(data, file, default_style='"')
        else:
            # 如果 chain['from'] 的值不是 "avax:usdc"，则修改 from 和 to 字段的值为对应的值
            with open('input.yaml', 'r') as file:
                data = yaml.load(file, Loader=yaml.SafeLoader)
                # 修改 from 和 to 字段的值为对应的值，这里可以根据具体情况修改
                data['from'] = "avax:usdc"
                data['to'] = "polygon:usdc"
            # 将修改后的数据写回 input.yaml 文件
            with open('input.yaml', 'w') as file:
                yaml.dump(data, file, default_style='"')






if __name__ == '__main__':

    count = 0  # 初始化计数器为 0
    Testapi = api()
    data = Testapi.test_yaml_data()

    num_pairs = min(len(Testapi.data['from']), len(Testapi.data['to']))
    for _ in range(num_pairs):
        data = Testapi.test_yaml_data()
        count += 1  # 每次执行测试用例后计数器加一

        Testapi = api()
        data = Testapi.test_yaml_data()
        with allure.step(f"Executing Test Case {count}"):
            print(f"执行第 {count} 次测试用例")
        with allure.step("Test Get Price"):
            Testapi.test_get_price(data)
        with allure.step("Test Encode Swap"):
            swapInfo = Testapi.test_encode_swap(data)
            Testapi.test_submit_swap_signatures(swapInfo, data)
        with allure.step("Test Submit Swap Signatures"):
            sig0, sig1, encoded = Testapi.test_submit_swap_signatures(swapInfo, data)
        with allure.step("Test Submit Swap"):
            swapId = Testapi.test_submit_swap(sig0, sig1, encoded, data)
        with allure.step("Test Check Status"):
            swapStatus = Testapi.test_check_status(swapId)
        with allure.step("Test Change Chain"):
            Testapi.test_change_chain(swapStatus, data)
        print(data)
        time.sleep(80)
    # pytest.main(['-vs', '-k', 'test_yaml_data'])
    # count = 0  # 初始化计数器为 0
    # while True:
    #     count += 1  # 每次执行测试用例后计数器加一
    #     print(f"执行第 {count} 次测试用例")
    #     Testapi = api()
    #     data = Testapi.test_yaml_data()
    #     Testapi.test_get_price(data)
    #     swapInfo = Testapi.test_encode_swap(data)
    #     Testapi.test_submit_swap_signatures(swapInfo, data)
    #     sig0, sig1, encoded = Testapi.test_submit_swap_signatures(swapInfo, data)
    #     swapId = Testapi.test_submit_swap(sig0, sig1, encoded, data)
    #     swapStatus = Testapi.test_check_status(swapId)
    #     Testapi.test_change_chain(swapStatus, data)

        # subprocess.run(['pytest', '-vs'])

        # time.sleep(120)
        # 创建 Api 类的实例
        # api_instance = api()


