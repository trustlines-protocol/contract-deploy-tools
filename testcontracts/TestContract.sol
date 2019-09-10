pragma solidity ^0.5.8;

import './subfolder/OtherContract.sol';

contract TestContract {

    uint public state;

    constructor(uint val) public {
        state = val;
    }

    function set(uint a) public {
        state = a;
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    function pay() payable public {}

    function testFunction(uint a) public view returns (uint) {
        return a + state;
    }

    function duplicatedDifferentArgumentLength(uint a) public {
        state = a;
    }

    function duplicatedDifferentArgumentLength(uint a, uint b) public {
        state = a + b;
    }

    function functionWithArrayArgument(address[] memory a) public {
    }

    function duplicatedSameArgumentLength(uint a) public pure returns (uint) {
        return a;
    }

    function duplicatedSameArgumentLength(bytes memory a) public pure returns (bytes memory) {
        return a;
    }

    function failingFunction() public pure returns (bytes memory) {
        require(false, "This function can only fail.");
    }
}
