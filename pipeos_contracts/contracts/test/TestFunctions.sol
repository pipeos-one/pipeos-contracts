pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;


contract TestFunctions {
    address public addr;
    uint256 public tvar = 10;
    uint256[] public arr = [1, 2, 3];


    struct TStruct {
        uint256 tvar1;
        address addr1;
    }

    constructor() {
        addr = msg.sender;
    }

    function m_addr() view public returns(address) {
        return msg.sender;
    }

    function s_addr() view public returns(address) {
        return addr;
    }

    function addr_addr() view public returns(address, address) {
        return (msg.sender, addr);
    }

    function m_uint(uint256 value) view public returns(uint256) {
        return value;
    }

    function s_uint() view public returns(uint256) {
        return tvar;
    }

    function addr_uint() view public returns(address, uint256) {
        return (addr, tvar);
    }

    function m_uint_arr(uint256[4] uint_arr) view public returns(uint256[4]) {
        return uint_arr;
    }

    function dynamic_uint_arr(uint256 value) public returns(uint256[]) {
        arr.push(value);
        return arr;
    }
}
