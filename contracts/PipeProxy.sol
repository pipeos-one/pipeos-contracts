pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;


contract PipeProxy  {
    uint256 public table_contracts = 11;
    uint256 public table_functions = 12;
    uint256 public table_ios = 13;

    function proxyCallInternal(address _to, bytes input_bytes, uint256 output_size) payable public returns (bytes) {
        uint256 value = msg.value;
        assembly {
            let zero_mem_pointer := 0x80

            let input_size := mload(input_bytes)
            let input_ptr := add(zero_mem_pointer, 32)

            let result := call(
              100000, // gas limit
              _to,  // to addr. append var to _slot to access storage variable
              value, // not transfer any ether
              input_ptr, // Inputs are stored at location ptr
              input_size, // Input size
              input_ptr,  //Store output
              output_size
            )

            mstore(sub(zero_mem_pointer, 32), 32)
            mstore(zero_mem_pointer, output_size)

            return(sub(zero_mem_pointer, 32), add(64, output_size))
        }
    }
}
