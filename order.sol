pragma solidity ^0.8.2;

contract Delivery 
{
    address customer;
    address payable owner;
    address payable courier;
    uint value;

    enum State 
    {
        CREATED,
        PAID,
        COURIER_ASSIGNED,
        DELIVERED
    }
    State state;
    mapping(State => string) state_names;

    modifier onlyInState(State req)
    {
        require(state == req, string.concat('Invalid state:', state_names[state]));
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

        state_names[State.CREATED] = "CREATED";
        state_names[State.PAID] = "PAID";
        state_names[State.COURIER_ASSIGNED] = "COURIER_ASSIGNED";
        state_names[State.DELIVERED] = "DELIVERED";
    }

    function pay() external payable onlyInState(State.CREATED) only(customer) exactly(value)
    {
        state = State.PAID;
    }

    function assignCourier(address payable _courier) external onlyInState(State.PAID)
    {
        courier = _courier;
        state = State.COURIER_ASSIGNED;
    }

    function delivered() external onlyInState(State.COURIER_ASSIGNED) only(customer)
    {
        owner.transfer((value * 8) / 10);
        courier.transfer((value * 2) / 10);
        state = State.DELIVERED;
    }
}