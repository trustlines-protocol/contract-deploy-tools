pragma solidity ^0.5.8;

contract ManyArgumentsContract {

    uint public a;
    int public b;
    int32 public c;
    bool public d;
    address public e;
    bytes public f;

    constructor(uint _a, int _b, int32 _c, bool _d, address _e, bytes memory _f) public {
        a = _a;
        b = _b;
        c = _c;
        d = _d;
        e = _e;
        f = _f;
    }
}
