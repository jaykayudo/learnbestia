// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


contract Payment is AccessControl{
    // Define the admin role constant
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    // Define the status enum
    enum Status {
        INITIATED,
        PAID,
        CANCELLED
    }

    // Define the transaction struct
    struct Transaction {
        string ref;
        uint256 amount;
        address token;
        Status status;
        uint256 date_created;
        uint256 date_updated;
    }

    // 
    mapping(string => Transaction) public transactions;

    constructor(address admin) {
        _grantRole(ADMIN_ROLE, admin);
    }

    function createInvoice(string memory ref, uint256 amount, address token) public onlyRole(ADMIN_ROLE) {
        Status initial_status = Status.INITIATED;
        Transaction memory transaction = Transaction(ref, amount, token, initial_status, block.timestamp, block.timestamp);
        transactions[ref] = transaction;
    }

    function payInvoice(string memory ref) public payable {
        Transaction memory transaction = transactions[ref];
        require(transaction.status == Status.INITIATED, "Invoice already paid or cancelled");
        address caller = msg.sender;
        IERC20 tokenInterface = IERC20(transaction.token);
        // Check caller balance
        uint256 balance = tokenInterface.balanceOf(caller);
        require(balance >= transaction.amount, "Insufficient balance");
        // Check allowance
        uint256 allowance = tokenInterface.allowance(caller, address(this));
        require(allowance >= transaction.amount, "Allowance not set");
        // Transfer amount
        tokenInterface.transferFrom(caller, address(this), transaction.amount);
        // Update transaction
        transaction.status = Status.PAID;
        transaction.date_updated = block.timestamp;
        transactions[ref] = transaction;
    }

    function checkPaymentStatus(string memory ref) public view returns (bool) {
        Transaction memory transaction = transactions[ref];
        return transaction.status == Status.PAID;
    }

    function cancelInvoice(string memory ref) public {
        require(hasRole(ADMIN_ROLE, msg.sender), "Only admin can cancel invoice");
        Transaction memory transaction = transactions[ref];
        require(transaction.status == Status.INITIATED, "Invoice already paid or cancelled");
        transaction.status = Status.CANCELLED;
        transaction.date_updated = block.timestamp;
        transactions[ref] = transaction;
    }

    function grantRole(bytes32 role, address account) public override onlyRole(ADMIN_ROLE) {
        _grantRole(role, account);
    }

    function getInvoice(string memory ref) public view returns (Transaction memory) {
        return transactions[ref];
    }

}