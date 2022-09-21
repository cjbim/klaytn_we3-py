from web3 import Web3
import asyncio



def connectWeb3(connect_host=None): #web3 connect rpcuri 선택
    if connect_host is None:
        infura_url = "http://localhost:8545"
    elif connect_host == "baobab":
        infura_url = "https://api.baobab.klaytn.net:8651"
    elif connect_host == "mainnet":
        infura_url = "https://klaytn-mainnet-rpc.allthatnode.com:8551"
    else:
        infura_url = "http://localhost:8545"
    web3 = Web3(Web3.HTTPProvider(infura_url))
    return web3
def klaytn_contract_abi(web3,contractAddress,abi): #컨트랙트 abi 연결
    file = open(abi, 'r', encoding='utf-8')
    mycontract = web3.eth.contract(abi=file.read(), address=contractAddress)
    return mycontract

def klaytn_coin_balance(web3,mycontract,useraddress): #coin 소유량 조회
    token_balance = mycontract.functions.balanceOf(useraddress).call()
    return token_balance

def klaytn_coin_totalsuply(web3,mycontract):
    '''
    use              : Token총 발행량 조회
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract: abi로 활성화한 컨트랙트 함수들
    output parameter : total_token
     '''

    total_token = mycontract.functions.totalSupply().call()
    print(total_token)
    return total_token
def get_first_block(web3,mycontract):
    '''
    use              : Token 컨트랙트 첫거래 Block number를 가져옴
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
    output parameter : first_block_num
    '''
    total = klaytn_coin_totalsuply(web3, mycontract)
    myFilter = mycontract.events.Transfer.createFilter(fromBlock=0, argument_filters={'value': total})
    txs = myFilter.get_all_entries()
    for tx in txs:
        tx_hash = (tx.transactionHash).hex()
        tx_data = {'from': tx.args['from'], 'to': tx.args['to'], 'value': tx.args['value'], 'event': tx.event,'transactionHash': tx_hash, 'blockNumber': tx.blockNumber }
        print(tx_data)
    first_block_num = tx.blockNumber
    return first_block_num


def klaytn_coin_list(web3,mycontract,startBlock,fromadress = None):# 해당 컨트랙트 거래내역 조회후 리스트로 저장
    tx_list = []
    if fromadress is None:
        myFilter =  mycontract.events.Transfer.createFilter(fromBlock=startBlock)
    else:
        myFilter =  mycontract.events.Transfer.createFilter(fromBlock=startBlock, argument_filters={'from': fromadress})
    txs = myFilter.get_all_entries()
    for tx in txs:
        tx_hash = (tx.transactionHash).hex()
        tx_data = {'from': tx.args['from'], 'to': tx.args['to'], 'value': tx.args['value'], 'event': tx.event,'transactionHash': tx_hash, 'blockNumber': tx.blockNumber }

        tx_list.append(tx_data)
    return tx_list

def klaytn_coin_tx_display(tx_list):
    for tx_data in tx_list:
        print(f"from=[{tx_data['from']}], to=[{tx_data['to']}],value=[{tx_data['value']}], event=[{tx_data['event']}], transactionHash=[{tx_data['transactionHash']}],blockNumber=[{tx_data['blockNumber']}]")
def klaytn_coin_transfer(web3,mycontract,sender_pv,sender_add,reciver_add,amt):

    sendAddress = web3.toChecksumAddress(sender_add)
    receiveAddress = web3.toChecksumAddress(reciver_add)
    nonce = web3.eth.get_transaction_count(sendAddress)
    amount = amt * web3.toWei(1, "ether")
    gas_estimate = mycontract.functions.transfer(receiveAddress, amount).estimate_gas({'from': sendAddress})

    tx = mycontract.functions.safeTransfer(receiveAddress, amount).build_transaction(
        {
            'from': sendAddress,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            'gasPrice': 25000000000,

        }
    )

    signed_txn = web3.eth.account.sign_transaction(tx, sender_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    print(f"gncHash=[{gncHash}]")
    return gncHash


if __name__ == "__main__":
    web3 = connectWeb3("baobab")
    mycontract = klaytn_contract_abi(web3, "", 'kip7deployedABI', )
    first_block = get_first_block(web3, mycontract)
    print(first_block)
    ret_list = klaytn_coin_list(web3, mycontract, first_block)
    klaytn_coin_tx_display(ret_list)
    print("---------------------------------")
    ret_list2 = klaytn_coin_list(web3, mycontract, 1,'')
    klaytn_coin_tx_display(ret_list2)


