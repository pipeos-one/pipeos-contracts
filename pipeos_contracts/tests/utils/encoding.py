from itertools import accumulate
from web3 import Web3
from eth_abi import encode_single


def get_function_signature(function_name, types=None):
    if types is None:
        types = []
    types_string = ','.join(types)
    return Web3.keccak(text=f'{function_name}({types_string})')[:4]


def encode_with_selector(function_name, types=None, args=None):
    if types is None:
        types = []
    if args is None:
        args = []
    function_signature = get_function_signature(function_name, types)
    encoded_args = Web3.solidityKeccak(types, args)
    return function_signature + encoded_args


def to_bytes(primitive=None, hexstr=None, text=None):
    return Web3.toBytes(primitive, hexstr, text)


def prepareGraphProxyInputs(types=(), values=()):
    if len(types) != len(values):
        raise ValueError('Types and values must have the same length.')

    abi_encoded = [encode_single(types[i], values[i]) for (i, _) in enumerate(types)]

    # We need to increase the index of each element with 1; position 0 is not used
    # So valueIndex can have a value of 0 if it is not set
    starts = [0] + [len(x) for (_, x) in enumerate(abi_encoded)]
    starts = [0] + list(accumulate(starts))
    inputSizeIsSlot = [False] + [len(x) == 32 for (_, x) in enumerate(abi_encoded)]

    return (b"".join(abi_encoded), starts, inputSizeIsSlot)
