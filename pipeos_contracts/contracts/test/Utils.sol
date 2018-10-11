pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;


/// @title Utils contract to be used by Pipeline
/// @notice This contract contains utility functions to be used by Pipeline.
contract Utils {

    /// @notice This function returns it's input.
    /// @param input_uint The input to be returned as output.
    /// @return output_uint Same as the input.
    function pipe_uint256(uint256 input_uint) pure public returns (uint256 output_uint) {
       output_uint = input_uint;
    }

    /// @notice This function returns it's input.
    /// @param input_address The input to be returned as output.
    /// @return output_address Same as the input.
    function pipe_address(address input_address) pure public returns (address output_address) {
       output_address = input_address;
    }

    /// @notice This function returns it's input.
    /// @param input_bytes32 The input to be returned as output.
    /// @return output_bytes32 Same as the input.
    function pipe_bytes32(bytes32 input_bytes32) pure public returns (bytes32 output_bytes32) {
       output_bytes32 = input_bytes32;
    }
}
