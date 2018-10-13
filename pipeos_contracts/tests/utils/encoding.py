from web3 import Web3
from eth_abi import encode_abi



def get_function_signature(function_name, types=[]):
    types_string = ','.join(types)
    return Web3.sha3(text=f'{function_name}({types_string})')[:4]


def encode_with_selector(function_name, types=[], args=[]):
    function_signature = get_function_signature(function_name, types)
    encoded_args = Web3.soliditySha3(types, args)
    return function_signature + encoded_args


def to_bytes(primitive=None, hexstr=None, text=None):
    return Web3.toBytes(primitive, hexstr, text)
