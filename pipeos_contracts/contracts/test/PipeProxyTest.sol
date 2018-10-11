pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

import 'pipeos/PipeProxy.sol';


contract TestPipeProxy {
    PipeProxy public pipe_proxy;
    address public test_contract;

    constructor (address _pipe_proxy, address _test_contract) public {
        pipe_proxy = PipeProxy(_pipe_proxy);
        test_contract = _test_contract;
    }

    function m_addr() view public returns(bytes32 addr) {
        bytes4 signature = bytes4(keccak256("m_addr()"));
        bytes memory input = abi.encodePacked(signature);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr := mload(add(answer, 32))
        }
    }

    function s_addr() view public returns(bytes32 addr) {
        bytes4 signature = bytes4(keccak256("s_addr()"));
        bytes memory input = abi.encodePacked(signature);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr := mload(add(answer, 32))
        }
    }

    function addr_addr() view public returns(bytes32 addr1, bytes32 addr2) {
        bytes4 signature = bytes4(keccak256("addr_addr()"));
        bytes memory input = abi.encodePacked(signature);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr1 := mload(add(answer, 32))
            addr2 := mload(add(answer, 64))
        }
    }

    function m_uint(uint256 value) view public returns(bytes32 val) {
        bytes4 signature = bytes4(keccak256("m_uint(uint256)"));
        bytes memory input = abi.encodeWithSelector(signature, value);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            val := mload(add(answer, 32))
        }
    }

    function s_uint() view public returns(bytes32 val) {
        bytes4 signature = bytes4(keccak256("s_uint()"));
        bytes memory input = abi.encodeWithSelector(signature);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            val := mload(add(answer, 32))
        }
    }

    function addr_uint() view public returns(bytes32 addr, bytes32 val) {
        bytes4 signature = bytes4(keccak256("addr_uint()"));
        bytes memory input = abi.encodeWithSelector(signature);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        assembly {
            addr := mload(add(answer, 32))
            val := mload(add(answer, 64))
        }
    }

    function m_uint_arr(uint256[4] uint_arr) view public returns(bytes32[4] arr_val) {
        bytes4 signature = bytes4(keccak256("m_uint_arr(uint256[4])"));
        bytes memory input = abi.encodeWithSelector(signature, uint_arr);
        bytes memory answer = pipe_proxy.proxy(test_contract, input, 70000);
        bytes32 val;
        for (uint256 i = 1; i <= uint_arr.length; i++) {
            assembly {
                val := mload(add(answer, mul(32, i)))
            }
            arr_val[i - 1] = val;
        }
    }

    function dynamic_uint_arr(uint256 value) public returns(uint256[] arr_val) {
        bytes4 signature = bytes4(keccak256("dynamic_uint_arr(uint256)"));
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
