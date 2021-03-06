pragma solidity ^0.5.4;

import './VendorRegistration.sol';
import './VendorPrices.sol';


/// @title Market Place contract. This is where users buy products from registered vendors.
/// @notice This is where users buy products from registered vendors.
contract MarketPlace {
    VendorRegistration public registration_contract;
    VendorPrices public prices_contract;

    mapping (bytes32 => uint256) public available_quantities;

    event MarketBuy(address vendor, uint256 product_id, uint256 quantity, address buyer);
    event QuantitySet(address vendor, uint256 product_id, uint256 quantity);

    constructor(address registration_address, address prices_address) public {
        registration_contract = VendorRegistration(registration_address);
        prices_contract = VendorPrices(prices_address);

        setQuantity(msg.sender, 1, 1000);
    }

    /// @notice This function allows a user to buy a product from a registered vendor.
    /// @param vendor The Ethereum address of the vendor.
    /// @param buyer The Ethereum address of the buyer.
    /// @param product_id The id of the product registered in the system.
    /// @param quantity The amount of product that the user wants to buy.
    function buy(address vendor, address buyer, uint256 product_id, uint256 quantity) payable public {
        bytes32 key = getKey(vendor, product_id);
        require(available_quantities[key] >= quantity);
        uint256 computed_quantity = prices_contract.calculateQuantity(product_id, vendor, msg.value);
        require(computed_quantity >= quantity);
        available_quantities[key] -= quantity;

        emit MarketBuy(vendor, product_id, quantity, buyer);
    }

    /// @notice This function sets the quantity of a product that a registered vendor has available for purchase.
    /// @param vendor The Ethereum address of the vendor.
    /// @param product_id The id of the product registered in the system.
    /// @param quantity The amount of product that the vendor has available for purchase.
    function setQuantity(address vendor, uint256 product_id, uint256 quantity) public {
        bytes32 key = getKey(vendor, product_id);
        available_quantities[key] = quantity;

        emit QuantitySet(vendor, product_id, quantity);
    }

    /// @notice This function returns the quantity of product that a registered vendor has available for purchase.
    /// @param vendor The Ethereum address of the vendor.
    /// @param product_id The id of the product registered in the system.
    /// @return quantity The amount of the product that the vendor has available for purchase.
    function getQuantity(address vendor, uint256 product_id) view public returns (uint256 quantity) {
        bytes32 key = getKey(vendor, product_id);
        return available_quantities[key];
    }

    /// @dev This function returns the key for the available_quantities mapping
    /// @param vendor The Ethereum address of the vendor.
    /// @param product_id The id of the product registered in the system.
    /// @return key The key for the available_quantities mapping
    function getKey(address vendor, uint256 product_id) pure public returns (bytes32 key) {
        return keccak256(abi.encodePacked(vendor, product_id));
    }
}
