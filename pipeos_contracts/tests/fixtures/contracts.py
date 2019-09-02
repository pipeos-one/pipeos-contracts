import pytest


@pytest.fixture
def pipe_proxy_contract(contracts_manager, deploy_contract):
    json_contract = contracts_manager.get_contract('PipeProxy')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
    )
    return contract


@pytest.fixture
def pipe_graph_proxy_contract(contracts_manager, deploy_contract):
    json_contract = contracts_manager.get_contract('PipeGraphProxy')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
    )
    return contract


@pytest.fixture
def test_functions_contract(contracts_manager, deploy_contract):
    json_contract = contracts_manager.get_contract('TestFunctions')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
    )
    return contract


@pytest.fixture
def piped_test_contract(
        contracts_manager,
        deploy_contract,
        pipe_proxy_contract,
        test_functions_contract,
):
    json_contract = contracts_manager.get_contract('TestPipeProxy')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
        [pipe_proxy_contract.address, test_functions_contract.address],
    )
    return contract


@pytest.fixture
def utils_contract(contracts_manager, deploy_contract):
    json_contract = contracts_manager.get_contract('Utils')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
    )
    return contract


@pytest.fixture
def vendor_reg_contract(contracts_manager, deploy_contract):
    json_contract = contracts_manager.get_contract('VendorRegistration')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
    )
    return contract


@pytest.fixture
def vendor_prices_contract(contracts_manager, deploy_contract):
    json_contract = contracts_manager.get_contract('VendorPrices')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
    )
    return contract


@pytest.fixture
def market_contract(
        contracts_manager,
        deploy_contract,
        vendor_reg_contract,
        vendor_prices_contract,
):
    json_contract = contracts_manager.get_contract('MarketPlace')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
        [vendor_reg_contract.address, vendor_prices_contract.address],
    )
    return contract


@pytest.fixture
def pipegraph_proxy_test(contracts_manager, deploy_contract):
    json_contract = contracts_manager.get_contract('PipeGraphProxyTest')
    (contract, txn_hash) = deploy_contract(
        json_contract['abi'],
        json_contract['bin'],
    )
    return contract
