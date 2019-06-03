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

}
