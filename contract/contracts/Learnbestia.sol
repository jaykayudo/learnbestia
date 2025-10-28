// SPDX-License-Identifier: MIT

pragma solidity >=0.7.0 <0.9.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";


contract TestToken is ERC20, AccessControl{
    // Define the admin role constant
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    constructor()ERC20("LearnBestia Token", "LERB"){
        _grantRole(ADMIN_ROLE, msg.sender);
        _mint(msg.sender, 200000000e18);
    }
}
