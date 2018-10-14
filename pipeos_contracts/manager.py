from pathlib import Path
from typing import Dict

from solc import compile_files


_BASE = Path(__file__).parent


class ContractManager:
    def __init__(self) -> None:
        """Params:
            path: either path to a precompiled contract JSON file, or a list of
                directories which contain solidity files to compile
        """
        self.contracts_source_dirs = {
            'pipeos': _BASE.joinpath('contracts'),
            'test': _BASE.joinpath('contracts', 'test'),
        }
        self.contracts = dict()

    def compile_contracts(self) -> None:
        """
        Compile solidity contracts into ABI and BIN. This requires solc somewhere in the $PATH
        and also the :ref:`ethereum.tools` python library.
        """
        if self.contracts_source_dirs is None:
            raise TypeError("Missing contracts source path, can't compile contracts.")

        import_dir_map = ['%s=%s' % (k, v) for k, v in self.contracts_source_dirs.items()]
        try:
            for contracts_dir in self.contracts_source_dirs.values():
                res = compile_files(
                    [str(file) for file in contracts_dir.glob('*.sol')],
                    output_values=('abi', 'bin', 'ast', 'metadata'),
                    import_remappings=import_dir_map,
                    optimize=False,
                )

                # Strip `ast` part from result
                # TODO: Remove after https://github.com/ethereum/py-solc/issues/56 is fixed
                res = {
                    contract_name: {
                        content_key: content_value
                        for content_key, content_value in contract_content.items()
                        if content_key != 'ast'
                    } for contract_name, contract_content in res.items()
                }
                self.contracts.update(_fix_contract_key_names(res))
        except FileNotFoundError as ex:
            raise FileNotFoundError(
                'Could not compile the contract. Check that solc is available.',
            ) from ex

    def get_contract(self, contract_name: str) -> Dict:
        """ Return ABI, BIN of the given contract. """
        if not self.contracts:
            self.compile_contracts()
        return self.contracts[contract_name]

    def get_contract_abi(self, contract_name: str) -> Dict:
        """ Returns the ABI for a given contract. """
        if not self.contracts:
            self.compile_contracts()
        return self.contracts[contract_name]['abi']

    def get_event_abi(self, contract_name: str, event_name: str) -> Dict:
        """ Returns the ABI for a given event. """
        # Import locally to avoid web3 dependency during installation via `compile_contracts`
        from web3.utils.contracts import find_matching_event_abi

        if not self.contracts:
            self.compile_contracts()
        contract_abi = self.get_contract_abi(contract_name)
        return find_matching_event_abi(contract_abi, event_name)


def _fix_contract_key_names(input: Dict) -> Dict:
    result = {}

    for k, v in input.items():
        name = k.split(':')[1]
        result[name] = v

    return result
