# APIAuto-mesonfi

## 单个交易对：single.yaml

1. 在 `single.yaml` 文件中配置你所需的交易信息：
   1. 配置你的 `from` 和 `to` 的地址、金额。
   2. 配置你的私钥（注意：请不要泄露，只限在本地运行）
   3. 配置你的 `from` 和 `to` 的网络和币种（从 from第一个网络 作为起点交易，请确保里面有足够的稳定币）

2. 在 `test_main.py` 文件中修改这行代码：
   ```python
   if self.data is None:
       with open('single.yaml', 'r') as file:




# 多个交易对：multiChain.yaml

在 `multiChain.yaml` 文件中配置你所需的交易信息：

1. 在 `multiChain.yaml` 文件中配置你所需的交易信息：
    1. 配置你的 `from` 和 `to` 的地址、金额。
    2. 配置你的私钥（注意：请不要泄露，只限在本地运行）
    3. 配置你的 `from` 和 `to` 的网络和币种（从 from第一个网络 作为起点交易，请确保里面有足够的稳定币）

2. 在 `test_main.py` 文件中修改这行代码：
   ```python
   if self.data is None:
       with open('multiChain.yaml', 'r') as file:
   

其他：

如果需要无限循环，在 `test_main.py` 文件中注释以下代码段：

```python
if count >= num_pairs-1:
    break
break

