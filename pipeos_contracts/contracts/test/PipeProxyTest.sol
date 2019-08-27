pragma solidity ^0.5.4;
pragma experimental ABIEncoderV2;

import 'pipeos/PipeProxy.sol';


contract TestPipeProxy {
    PipeProxy public pipe_proxy;
    address public test_contract;

    constructor (address _pipe_proxy, address _test_contract) public {
        pipe_proxy = PipeProxy(_pipe_proxy);
        test_contract = _test_contract;
    }

    function m_uint256(uint256 value) view public returns(uint256 val) {
        bytes4 signature = bytes4(keccak256("m_uint256(uint256)"));
        bytes memory input = abi.encodeWithSelector(signature, value);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            val := mload(add(answer, 32))
        }
    }

    function s_uint256() view public returns(uint256 val) {
        bytes4 signature = bytes4(keccak256("s_uint256()"));
        bytes memory input = abi.encodeWithSelector(signature);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            val := mload(add(answer, 32))
        }
    }

    function m_uint8(uint8 value) view public returns(uint8 val) {
        bytes4 signature = bytes4(keccak256("m_uint8(uint8)"));
        bytes memory input = abi.encodeWithSelector(signature, value);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            val := mload(add(answer, 32))
        }
    }

    function m_uint8_uint8(uint8 value1, uint8 value2) view public returns(uint8 val1, uint8 val2) {
        bytes4 signature = bytes4(keccak256("m_uint8_uint8(uint8,uint8)"));
        bytes memory input = abi.encodeWithSelector(signature, value1, value2);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            val1 := mload(add(answer, 32))
            val2 := mload(add(answer, 64))
        }
    }

    function m_addr(address value) view public returns(address addr) {
        bytes4 signature = bytes4(keccak256("m_addr(address)"));
        bytes memory input = abi.encodeWithSelector(signature, value);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr := mload(add(answer, 32))
        }
    }

    function s_addr() view public returns(address addr) {
        bytes4 signature = bytes4(keccak256("s_addr()"));
        bytes memory input = abi.encodeWithSelector(signature);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr := mload(add(answer, 32))
        }
    }

    function addr_addr(address value) view public returns(address addr1, address addr2) {
        bytes4 signature = bytes4(keccak256("addr_addr(address)"));
        bytes memory input = abi.encodeWithSelector(signature, value);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr1 := mload(add(answer, 32))
            addr2 := mload(add(answer, 64))
        }
    }

    function addr_uint_uint(uint256 value) view public returns(address addr, uint256 val1, uint256 val2) {
        bytes4 signature = bytes4(keccak256("addr_uint_uint(uint256)"));
        bytes memory input = abi.encodeWithSelector(signature, value);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr := mload(add(answer, 32))
            val1 := mload(add(answer, 64))
            val2 := mload(add(answer, 96))
        }
    }

    function addr_uint_bytes32(bytes32 value) view public returns(address addr, uint256 val, bytes32 byte_value) {
        bytes4 signature = bytes4(keccak256("addr_uint_bytes32(bytes32)"));
        bytes memory input = abi.encodeWithSelector(signature, value);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr := mload(add(answer, 32))
            val := mload(add(answer, 64))
            byte_value := mload(add(answer, 96))
        }
    }

    function m_uint256_arr_static(uint256[4] memory uint_arr) view public returns(uint256[4] memory arr_val) {
        bytes4 signature = bytes4(keccak256("m_uint256_arr_static(uint256[4])"));
        bytes memory input = abi.encodeWithSelector(signature, uint_arr);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        uint256 val;
        for (uint256 i = 1; i <= uint_arr.length; i++) {
            assembly {
                val := mload(add(answer, mul(32, i)))
            }
            arr_val[i - 1] = val;
        }
    }

    function s_uint256_arr_dynamic(uint256 value) public returns(uint256[] memory arr_val) {
        bytes4 signature = bytes4(keccak256("s_uint256_arr_dynamic(uint256)"));
        bytes memory input = abi.encodeWithSelector(signature, value);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        uint256 array_length;
        uint256 val;
        uint256 offset;
        assembly {
            // first 32 bytes are answer length
            // next 32 bytes are offset
            // then we have the array length
            array_length := mload(add(answer, 64))
        }
        require(array_length > 0, 'Something bad');
        arr_val = new uint256[](array_length);

        for (uint256 i = 0; i < array_length; i++) {
            offset = 96 + 32*i;
            assembly {
                val := mload(add(answer, offset))
            }
            arr_val[i] = val;
        }
        return arr_val;
    }
}
