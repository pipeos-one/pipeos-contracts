import pytest
from eth_tester.exceptions import TransactionFailed


def test_uint256(
        get_accounts,
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    (A, B) = get_accounts(2)
    assert piped_test_contract.functions.pipe_proxy().call() == pipe_proxy_contract.address
    assert piped_test_contract.functions.test_contract().call() == test_functions_contract.address
