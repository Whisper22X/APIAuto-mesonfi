# APIAuto-mesonfi

运行前，请在命令行中输入：
```shell
pip install -r requirements.txt
```

## multiChain.yaml

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

修改 `multiChain.yaml` 文件中 `repetition`
是否开启自动执行（Yes:开启，No:关闭）



