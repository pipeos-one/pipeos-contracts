pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;


contract TestFunctions {
    address public addr;
    uint256 public svar = 10;
    uint256[] public arr = [1, 2, 3];


    struct TStruct {
        uint256 tvar1;
        address addr1;
    }

    constructor() public {
        addr = msg.sender;
    }

    function get_arr() view public returns(uint256[]) {
        return arr;
    }

    function m_uint256(uint256 value) pure public returns(uint256) {
        return value;
    }

    function s_uint256() view public returns(uint256) {
        return svar;
    }

    function m_addr(address value) pure public returns(address) {
        return value;
    }

    function s_addr() view public returns(address) {
        return addr;
    }

    function addr_addr(address value) view public returns(address, address) {
        return (value, addr);
    }

    function addr_uint_uint(uint256 value) view public returns(address, uint256, uint256) {
        return (addr, svar, value);
    }

    function addr_uint_bytes32(bytes32 value) view public returns(address, uint256, bytes32) {
        return (addr, svar, value);
    }

    function m_uint256_arr_static(uint256[4] uint_arr) pure public returns(uint256[4]) {
        return uint_arr;
    }

    function s_uint256_arr_dynamic(uint256 value) public returns(uint256[]) {
        arr.push(value);
        return arr;
    }
}
