// SPDX-License-Identifier: MIT

pragma solidity >=0.7.0 <0.9.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

contract Certificate is ERC721, AccessControl{
    // Define the admin role constant
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    // Define base URI
    string public baseURI;


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

    // Set the base URI
    function setBaseURI(string memory URI) public onlyRole(ADMIN_ROLE) {
        baseURI = URI;
    }

    // Override token uri to return in the format of baseURI/{tokenID}
    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        _requireOwned(tokenId);
        return bytes(baseURI).length > 0 ? string.concat(baseURI, Strings.toString(tokenId)) : "";
    }

}