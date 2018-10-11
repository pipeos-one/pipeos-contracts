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
