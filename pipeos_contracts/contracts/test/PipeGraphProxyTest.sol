pragma solidity ^0.6.2;
pragma experimental ABIEncoderV2;


contract PipeGraphProxyTest {
    struct TestStruct {
        uint256 number;
        uint256[] array;
        address addr;
    }

    function t_uint(uint256 length) pure public returns(uint256[] memory uarray) {
        uarray = new uint256[](length);
        for (uint256 i = 0; i < length; i++) {
            uarray[i] = i + 1;
        }
    }

    function t_address() view public returns(address addr) {
        return msg.sender;
    }

    function t_array(uint256[] memory uarray, uint256 number, address addr) pure public returns(TestStruct memory ts) {
        ts = TestStruct(number, uarray, addr);
    }

    function t_struct(TestStruct memory ts) pure public returns(uint256 number, uint256[] memory uarray, address addr) {
        return (ts.number, ts.array, ts.addr);
    }
}
