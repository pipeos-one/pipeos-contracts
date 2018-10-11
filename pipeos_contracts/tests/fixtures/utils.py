import pytest

from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from web3.utils.threads import Timeout

from eth_utils import denoms, is_same_address
from eth_tester import EthereumTester, PyEVMBackend
from eth_tester.exceptions import TransactionFailed

from pipeos_contracts.tests.utils.logs import LogHandler
from pipeos_contracts.tests.fixtures.config import passphrase


@pytest.fixture(scope='session')
def ethereum_tester():
    """Returns an instance of an Ethereum tester"""
    return EthereumTester(PyEVMBackend())


@pytest.fixture(scope='session')
def patch_genesis_gas_limit():
    import eth_tester.backends.pyevm.main as pyevm_main
    original_gas_limit = pyevm_main.GENESIS_GAS_LIMIT
    pyevm_main.GENESIS_GAS_LIMIT = 6 * 10 ** 6

    yield

    pyevm_main.GENESIS_GAS_LIMIT = original_gas_limit


@pytest.fixture(scope='session')
def web3(
        patch_genesis_gas_limit,
        ethereum_tester,
):
    """Returns an initialized Web3 instance"""
    provider = EthereumTesterProvider(ethereum_tester)
    web3 = Web3(provider)
    yield web3


@pytest.fixture()
def owner(web3):
    return web3.eth.accounts[0]


@pytest.fixture()
def get_accounts(web3, owner):
    def get(number):
        new_accounts = []
        for _ in range(0, number):
            new_account = web3.personal.newAccount(passphrase)
            amount = int(web3.eth.getBalance(web3.eth.accounts[0]) / 2 / number)
            web3.eth.sendTransaction({
                'from': web3.eth.accounts[1],
                'to': new_account,
                'value': amount,
            })
            web3.personal.unlockAccount(new_account, passphrase)
            new_accounts.append(new_account)
        return new_accounts
    return get


@pytest.fixture
def get_private_key(web3, ethereum_tester):
    def get(account_address):
        keys = [
            key.to_hex() for key in ethereum_tester.backend.account_keys
            if is_same_address(
                key.public_key.to_address(),
                account_address,
            )
        ]
        assert len(keys) == 1
        return keys[0]
    return get


@pytest.fixture
def deploy_contract(web3, owner):
    """Returns a function that deploys a compiled contract"""
    def fn(
            abi,
            bytecode,
            args,
    ):
        if args is None:
            args = []

        contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        txhash = deploy_contract_txhash(web3, deployer_address, abi, bytecode, args)

        txhash = contract.constructor(*args).transact({'from': owner})
        contract_address = web3.eth.getTransactionReceipt(txhash).contractAddress
        web3.testing.mine(1)

        return contract(contract_address), txhash
    return fn


def check_succesful_tx(web3: Web3, txid: str, timeout=180) -> dict:
    '''See if transaction went through (Solidity code did not throw).
    :return: Transaction receipt
    '''
    receipt = wait_for_transaction_receipt(web3, txid, timeout=timeout)
    txinfo = web3.eth.getTransaction(txid)
    assert receipt['status'] != 0
    assert txinfo['gas'] != receipt['gasUsed']
    return receipt


def wait_for_transaction_receipt(web3, txid, timeout=180):
    with Timeout(timeout) as time:
            while not web3.eth.getTransactionReceipt(txid):
                time.sleep(5)

    return web3.eth.getTransactionReceipt(txid)


@pytest.fixture()
def event_handler(contracts_manager, web3):
    def get(contract=None, address=None, abi=None):
        if contract:
            abi = contract.abi
            address = contract.address

        if address and abi:
            return LogHandler(web3, address, abi)
        else:
            raise Exception('event_handler called without a contract instance')
    return get


@pytest.fixture
def txn_cost(web3, txn_gas):
    def get(txn_hash):
        return txn_gas(txn_hash) * web3.eth.gasPrice
    return get


@pytest.fixture
def txn_gas(web3):
    def get(txn_hash):
        receipt = web3.eth.getTransactionReceipt(txn_hash)
        return receipt['gasUsed']
    return get


@pytest.fixture
def print_gas(web3, txn_gas):
    def get(txn_hash, message=None, additional_gas=0):
        gas_used = txn_gas(txn_hash)
        if not message:
            message = txn_hash

        print('----------------------------------')
        print('GAS USED ' + message, gas_used + additional_gas)
        print('----------------------------------')
    return get


@pytest.fixture()
def get_block(web3):
    def get(txn_hash):
        receipt = web3.eth.getTransactionReceipt(txn_hash)
        return receipt['blockNumber']
    return get
