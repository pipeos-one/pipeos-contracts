pragma solidity ^0.5.4;
pragma experimental ABIEncoderV2;

import 'pipeos/PipeProxy.sol';


contract PipedContract {
    PipeProxy public pipe_proxy;
    address public MarketPlace_address;
    address public Utils_address;

    constructor(address _pipe_proxy, address _MarketPlace_address, address _Utils_address) public {
        pipe_proxy = PipeProxy(_pipe_proxy);
        MarketPlace_address = _MarketPlace_address;
        Utils_address = _Utils_address;
    }

    function addUint(uint256 x, uint256 y) pure public returns(uint256 z) {
        z = x + y;
    }

    function PipedFunction1(address vendor, address vendor_2, address vendor_3, uint256 input_uint) payable public  {
        bytes4 signature42;
        bytes memory input42;
        bytes memory answer42;
        uint wei_value = msg.value;
        address tx_sender = msg.sender;

        signature42 = bytes4(keccak256("pipe_uint256(uint256)"));
        input42 = abi.encodeWithSelector(signature42, input_uint);
        answer42 = pipe_proxy.proxy(Utils_address, input42, 32);
        uint256 output_uint;
        assembly {
            output_uint := mload(add(answer42, 32))
        }

        signature42 = bytes4(keccak256("getQuantity(address,uint256)"));
        input42 = abi.encodeWithSelector(signature42, vendor_3,output_uint);
        answer42 = pipe_proxy.proxy(MarketPlace_address, input42, 32);
        uint256 quantity_2;
        assembly {
            quantity_2 := mload(add(answer42, 32))
        }

        signature42 = bytes4(keccak256("getQuantity(address,uint256)"));
        input42 = abi.encodeWithSelector(signature42, vendor_2,output_uint);
        answer42 = pipe_proxy.proxy(MarketPlace_address, input42, 32);
        uint256 quantity;
        assembly {
            quantity := mload(add(answer42, 32))
        }

        uint256 z;
        (z) = addUint(quantity,quantity_2);

        signature42 = bytes4(keccak256("setQuantity(address,uint256,uint256)"));
        input42 = abi.encodeWithSelector(signature42, vendor,output_uint,z);
        pipe_proxy.proxy(MarketPlace_address, input42, 32);
    }
}
