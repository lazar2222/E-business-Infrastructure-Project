pragma solidity ^0.8.2;

contract Delivery 
{
    address customer;
    address payable owner;
    address payable courier;
    uint value;

    enum State {
        CREATED,
        PAID,
        COURIER_ASSIGNED,
        DELIVERED
    }
    State state;

    modifier onlyInState(State req)
    {
        require(state == req, 'Invalid State.');
        _;
    }

    modifier only(address adr)
    {
        require(msg.sender == adr, 'Invalid Address.');
        _;
    }

    modifier exactly(uint val)
    {
        require(msg.value == val, 'Invalid Value.');
        _;
    }

    constructor(address payable _customer, uint _value)
    {
        customer = _customer;
        owner = payable(msg.sender);
        courier = payable(address(0));
        value = _value;
        state = State.CREATED;
    }

    function pay() external payable onlyInState(State.CREATED) only(customer) exactly(value)
    {
        state = State.PAID;
    }

    function assingCourier(address payable _courier) external onlyInState(State.PAID)
    {
        courier = _courier;
        state = State.COURIER_ASSIGNED;
    }

    function delivered() external onlyInState(State.COURIER_ASSIGNED)
    {
        owner.transfer((value * 8) / 10);
        courier.transfer((value * 2) / 10);
        state = State.DELIVERED;
    }
}