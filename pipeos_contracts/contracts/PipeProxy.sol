pragma solidity ^0.6.2;
pragma experimental ABIEncoderV2;


contract PipeProxy {

    function proxyPayable(
        address _to,
        bytes memory input_bytes,
        uint256 gas_value
    )
        payable
        public
        returns (bytes memory)
    {
        uint256 value = msg.value;
        bytes memory output;
        uint256 output_len;
        assembly {
            let zero_mem_pointer := 0x80

            let input_size := mload(input_bytes)
            let input_ptr := add(zero_mem_pointer, 32)

            let result := call(
              gas_value, // gas limit
              _to,  // contract address to call
              value, // value of transferred ETH
              input_ptr, // inputs are stored at location input_ptr
              input_size, // input size
              0,  // store output at pointer 0x0
              0  // expected output size set to 0, because we will use returndatasize
            )

            output_len := returndatasize()
        }

        output = new bytes(output_len);

        assembly {
            // copy return data content after output length (first 32 bytes)
            returndatacopy(add(output, 32), 0, output_len)
        }

        return output;
    }

    function proxy(
        address _to,
        bytes memory input_bytes,
        uint256 gas_value
    )
        view
        public
        returns (bytes memory)
    {
        bytes memory output;
        uint256 output_len;
        assembly {
            let zero_mem_pointer := 0x80

            let input_size := mload(input_bytes)
            let input_ptr := add(zero_mem_pointer, 32)

            let result := staticcall(
              gas_value, // gas limit
              _to,  // contract address to call
              input_ptr, // inputs are stored at location input_ptr
              input_size, // input size
              0,  // store output at pointer 0x0
              0  // expected output size set to 0, because we will use returndatasize
            )

            output_len := returndatasize()
        }

        output = new bytes(output_len);

        assembly {
            // copy return data content after output length (first 32 bytes)
            returndatacopy(add(output, 32), 0, output_len)
        }

        return output;
    }
}
