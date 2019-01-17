pragma solidity ^0.4.25;

import './subfolder/OtherContract.sol';

contract TestContract {

    int public state = 5;

    constructor() public {
        state = 1;
    }

    function testFunction(int a) public view returns (int) {
        return a + state;
    }
}
