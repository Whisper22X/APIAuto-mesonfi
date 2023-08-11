# APIAuto-mesonfi

#单个交易对：single.yaml
在 single.yaml 文件中配置你所需的交易信息即可

#多个交易对：multiChain.yaml
在 multiChain.yaml 文件中配置你所需对交易信息即可

需要无限循环：
去除：
``            if count >= num_pairs-1:
                break
        break``
即可实现无限循环