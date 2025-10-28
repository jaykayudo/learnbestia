// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract Certificate is ERC721, AccessControl{
    // Define the admin role constant
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    constructor(address admin, string memory name, string memory symbol) ERC721(name, symbol) {
        _grantRole(ADMIN_ROLE, admin);
    }

    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
    // Mint certificate NFT with certificate ID of the student
    function mint(address to, uint256 tokenId) public onlyRole(ADMIN_ROLE) {
        _mint(to, tokenId);
    }
}