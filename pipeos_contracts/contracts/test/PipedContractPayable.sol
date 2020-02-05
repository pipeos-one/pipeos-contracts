pragma solidity ^0.6.2;
pragma experimental ABIEncoderV2;


interface PipeProxyInterface {
function proxy(
    address _to,
    bytes calldata input_bytes,
    uint256 gas_value
)
    payable
    external
    returns (bytes memory);
}

contract PipedContractPayable {
    PipeProxyInterface public pipe_proxy;
    address public getVendor_0 ;
    address public calculateQuantity_1 ;
    address public buy_2 ;
constructor(address _pipe_proxy, address _getVendor_0, address _calculateQuantity_1, address _buy_2
    ) public {
        pipe_proxy = PipeProxyInterface(_pipe_proxy);
    getVendor_0 = _getVendor_0;
calculateQuantity_1 = _calculateQuantity_1;
buy_2 = _buy_2;
}


function PipedFunction0(uint256 i_product_id_0, uint256 i_buy_2_wei_value_2, address i_buyer_2) public payable  {
    bytes4 signature42;
    bytes memory input42;
    bytes memory answer42;
    address tx_sender = msg.sender;

signature42 = bytes4(keccak256("getVendor(uint256)"));
input42 = abi.encodeWithSelector(signature42, i_product_id_0);
    answer42 = pipe_proxy.proxy(getVendor_0, input42, 400000);
address o_vendor_0;
assembly {
o_vendor_0 := mload(add(answer42, 32))
}


signature42 = bytes4(keccak256("calculateQuantity(uint256,address,uint256)"));
input42 = abi.encodeWithSelector(signature42, i_product_id_0, o_vendor_0, i_buy_2_wei_value_2);
    answer42 = pipe_proxy.proxy(calculateQuantity_1, input42, 400000);
uint256 o_quantity_1;
assembly {
o_quantity_1 := mload(add(answer42, 32))
}


signature42 = bytes4(keccak256("buy(address,address,uint256,uint256)"));
input42 = abi.encodeWithSelector(signature42, o_vendor_0, i_buyer_2, i_product_id_0, o_quantity_1);
    answer42 = pipe_proxy.proxy.value(i_buy_2_wei_value_2)(buy_2, input42, 400000);

}}
