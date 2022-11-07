pragma solidity  >=0.5.0;
import "./klaytn/contracts/token/KIP7/KIP7Token.sol";
import "./klaytn/contracts/Ownership/Ownable.sol";

contract Mycoin is KIP7Token,Ownable{

    constructor(string memory name, string memory symbol, uint8 decimals, uint256 initialSupply) KIP7Token(name, symbol, decimals,initialSupply) public {}
    function multisend (address[] memory dests, uint256[] memory values) public payable returns (uint256) { //멀티샌드 함수 구성
        uint256 i = 0;
        while (i < dests.length) {
        transfer(dests[i], values[i]);
           i += 1;
        }
        return(i);
    }
} 