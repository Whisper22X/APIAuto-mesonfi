# from web3 import Web3
#
# # Connect to an Ethereum node (e.g., Infura)
# w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/0ccf4a37af6848e0a63abe11106c5fce'))
#
# # Your Ethereum wallet address
# wallet_address = '0x4Fc928e89435F13B3dbf49598F9fFe20C4439CaD'
#
# # USDC contract address on Ethereum mainnet
# usdc_contract_address = '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E'
#
# # USDC contract ABI (Application Binary Interface)
# usdc_contract_abi = [
#     {
#         "constant": True,
#         "inputs": [{"name": "_owner", "type": "address"}],
#         "name": "balanceOf",
#         "outputs": [{"name": "balance", "type": "uint256"}],
#         "type": "function"
#     }
# ]
#
# # Create a contract object for USDC
# usdc_contract = w3.eth.contract(address=usdc_contract_address, abi=usdc_contract_abi)
#
# # Print contract address for verification
# print("Contract Address:", usdc_contract_address)
#
# # Print wallet address for verification
# print("Wallet Address:", wallet_address)
#
# # Get the USDC balance in wei
# usdc_balance_wei = usdc_contract.functions.balanceOf(wallet_address).call()
#
# # Print the balance in wei for verification
# print("USDC Balance in Wei:", usdc_balance_wei)
#
# # Convert the balance to USDC (USDC has 6 decimals)
# usdc_balance = usdc_balance_wei / 10**6
# print("USDC Balance:", usdc_balance)
