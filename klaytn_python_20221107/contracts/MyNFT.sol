pragma solidity  ^0.5.0;
pragma experimental ABIEncoderV2;
import "./klaytn/contracts/token/KIP17/KIP17Token.sol";
import "./klaytn/contracts/Ownership/Ownable.sol";

contract MyNFT is KIP17Token,Ownable {



    constructor(string memory _name, string memory _symbol) public KIP17Token(_name, _symbol){
        
    }

    function multimint (address[] memory dests,uint256[] memory tokenIds, string[] memory tokenURIs) public onlyOwner returns (uint256) {
        uint256 i = 0;
        while (i < dests.length) {
        mintWithTokenURI(dests[i],tokenIds[i], tokenURIs[i]);
           i += 1;
        }
        return(i);
    }

}

