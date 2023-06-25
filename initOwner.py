import os
from web3 import Web3
from web3 import HTTPProvider

w3 = Web3(HTTPProvider('http://127.0.0.1:8545'))

if not os.path.exists('private.key') or not os.path.exists('public.key'):
    private_key = w3.eth.account.create()._private_key
    public_key = w3.eth.account.from_key(private_key).address
    with open('private.key', 'w') as file:
        file.write(private_key.hex())
    with open('public.key', 'w') as file:
        file.write(public_key)
else:
    with open('private.key', 'r') as file:
        private_key = file.read()
    with open('public.key', 'r') as file:
        public_key = file.read()


address = w3.to_checksum_address(public_key)
sender = w3.eth.accounts[0]

result = w3.eth.send_transaction({'from': sender, 'to': address, 'value': w3.to_wei(2, 'ether')})
print(result)
