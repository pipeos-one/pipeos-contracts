import pytest
from pipeos_contracts.manager import ContractManager


@pytest.fixture
def contracts_manager():
    return ContractManager()
