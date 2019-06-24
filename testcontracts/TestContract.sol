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

    function testFunction(uint a) public view returns (uint) {
        return a + state;
    }

    function duplicatedDifferentArgumentLength(uint a) public {
        state = a;
    }

    function duplicatedDifferentArgumentLength(uint a, uint b) public {
        state = a + b;
    }

    function duplicatedSameArgumentLength(uint a) public pure returns (uint) {
        return a;
    }

    function duplicatedSameArgumentLength(bytes memory a) public pure returns (bytes memory) {
        return a;
    }

}
