import secrets
import httpx
from datetime import datetime
from eth_account import Account
from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy


class Wallet:

    def crate_new_wallet(self):
        """Create ETH wallet"""
        hex_string = secrets.token_hex(32)
        private_key = "0x" + hex_string
        return self.create_wallet(private_key)

    @staticmethod
    def create_wallet(private_key):
        """Import ETH wallet"""
        account = Account.from_key(private_key)
        return account.address


class BaseDecoder:

    @staticmethod
    def timestamp_to_period(time_stamp):
        date_time = datetime.fromtimestamp(int(time_stamp))
        period = datetime.now() - date_time
        return period.seconds


class BaseClient:
    INFURA = str('https://sepolia.infura.io/v3/7c8d5f115738446d9bf671107b64c3a7')

    @property
    def client(self):
        return httpx.Client()

    @property
    def provider(self):
        return Web3(Web3.HTTPProvider(self.INFURA))

    @staticmethod
    def send_request(request):
        try:
            with httpx.Client() as client:
                response = client.send(request)
            return response
        except Exception as error:
            raise error


class InfuraClient(BaseClient, BaseDecoder):
    def __init__(self):
        self.endpoint = self.INFURA

    def get_balance(self):
        return self.provider.fromWei(provider.eth.get_balance('0x71Df913fab8083A7ed2529fd02eebEcB066E7549'), 'ether')


class EtherscanClient(BaseClient, BaseDecoder):

    def __init__(self):
        self.endpoint = 'https://api-sepolia.etherscan.io/api/'

    def get_result(self, data):
        formatted_result = ''
        for result in data.get('result'):
            formatted_result += f'Txn Hash - {result.get("hash")}\n' \
                                f'From - {result.get("from")}\n' \
                                f'To - {result.get("to")}\n' \
                                f'Value - {self.provider.fromWei(int(result.get("value")), "ether")} - ETH\n' \
                                f'Age - {self.timestamp_to_period(result.get("timeStamp"))} - seconds ago\n' \
                                f'Status - {result.get("txreceipt_status")}\n\n'
        return formatted_result

    def get_list_transactions(self):
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': '0x71Df913fab8083A7ed2529fd02eebEcB066E7549',
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': 10,
            'sort': 'asc',
            'apikey': '31AHFCVRWK7WF866J4V4XCHZ59FVCR7HUN'
        }
        request = self.client.build_request(method='GET',
                                            url=self.endpoint,
                                            params=params)
        response = self.send_request(request)
        result = response.json()
        return self.get_result(result)


if __name__ == '__main__':
    # Web3 provider
    base = BaseClient()
    provider = base.provider
    # clients
    infura = InfuraClient()
    etherscan = EtherscanClient()
    # Balance
    print(f'Balance: {infura.get_balance()} - ETH')
    print('\n')
    # Transactions list
    print(etherscan.get_list_transactions())

    print('Send transaction....\n\n')
    # Test transaction
    account_from = {
        "private_key": "0x3849bcb502f2ec978aab612a04b3a9da3886411f639716ddbc410cb597cdb2e6",
        "address": "0x71Df913fab8083A7ed2529fd02eebEcB066E7549",
    }
    address_to = '0xB18573694921F9C99d0183c7BA47c9ae2E734664'
    provider.eth.set_gas_price_strategy(rpc_gas_price_strategy)

    tx_create = provider.eth.account.sign_transaction(
        {
            "nonce": provider.eth.get_transaction_count(account_from["address"]),
            "gasPrice": provider.eth.generate_gas_price(),
            "gas": 21000,
            "to": address_to,
            "value": provider.toWei('0.1', "ether"),
            'chainId': 11155111
        },
        account_from["private_key"],
    )

    tx_hash = provider.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = provider.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction successful with hash: {tx_receipt.transactionHash.hex()}")

    print(f'Balance: {infura.get_balance()} - ETH')
