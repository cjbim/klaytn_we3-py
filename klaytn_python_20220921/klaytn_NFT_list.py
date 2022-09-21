from web3 import Web3
import urllib
import json

'''
creater : cho jung bin

'''

def connectWeb3(connect_host=None):
    '''
    use              : Network 연결
    input parameter  : 1. None      : parameter가 없는 경우 localhost로 연결
                       2. 'baobab'  : Klaytn 테스트넷
                       3. 'mainnet' : Klaytn 메인넷
    output parameter : web3
    '''
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

def klaytn_contract_abi(web3,contractAddress,abi):
    '''
    use              : 컨트랙트 주소와 abi를 통해 스마트 컨트랙트 함수를 사용하기위해 연결
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. contractAddress: 컨트랙트 주소
                       3. abi: abi 경로
    output parameter : mycontract
    '''
    file = open(abi, 'r', encoding='utf-8')
    contractaddress = web3.toChecksumAddress(contractAddress)
    mycontract = web3.eth.contract(abi=file.read(), address=contractaddress)
    return mycontract

def klaytn_NFT_totalsuply(web3,mycontract):
    '''
    use              : NFT총 발행량 조회
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract: abi로 활성화한 컨트랙트 함수들
    output parameter : total_token
     '''

    total_token = mycontract.functions.totalSupply().call()
    print(total_token)
    return total_token


def klaytn_NFT_owner(web3,mycontract,token_id):
    '''
    use              : NFT Token id Owner 주소 조회
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
                       3. token_id : 조회할 토큰 id
    output parameter : token_owner
    '''
    token_owner = mycontract.functions.ownerOf(token_id).call()
    return token_owner

def klaytn_NFT_uri(web3,mycontract,token_id):
    '''
    use             : NFT Token id uri 조회
    input parameter : 1. web3 : web3 네트워크 연결
                      2. mycontract : abi로 활성화한 컨트랙트 함수들
                      3. token_id : 조회할 토큰 id
    output parameter : tokenid_uri
    '''
    tokenid_uri = mycontract.functions.tokenURI(token_id).call()
    return tokenid_uri
def get_first_block(web3,mycontract):
    '''
    use              : NFT 컨트랙트 첫거래 Block number를 가져옴
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
    output parameter : first_block_num
    '''
    myFilter = mycontract.events.Transfer.createFilter(fromBlock=0, argument_filters={'tokenId': 1})
    txs = myFilter.get_all_entries()
    for tx in txs:
        tx_hash = (tx.transactionHash).hex()
        tx_data = {'from': tx.args['from'], 'to': tx.args['to'], 'tokenId': tx.args['tokenId'], 'event': tx.event,'transactionHash': tx_hash, 'blockNumber': tx.blockNumber }
        print(tx_data)
    first_block_num = tx.blockNumber
    return first_block_num


def klaytn_NFT_list(web3, mycontract, startBlock, token_id=None):
    '''
    use              : 해당 컨트랙트 거래내역 조회후 리스트로 저장
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
                       3. startBlock : 탐색 시작 블록 넘버
                       4. token_id=None : 특정 token id 거래기록 (선택 사항)
    output parameter : tx_list
    '''

    tx_list = []
    if token_id is None:
        myFilter = mycontract.events.Transfer.createFilter(fromBlock=startBlock)
    else :
        myFilter = mycontract.events.Transfer.createFilter(fromBlock=startBlock, argument_filters={ 'tokenId': token_id})
    txs = myFilter.get_all_entries()
    for tx in txs:
        tx_hash = (tx.transactionHash).hex()
        tx_data = {'from': tx.args['from'], 'to': tx.args['to'], 'tokenId': tx.args['tokenId'], 'event': tx.event,'transactionHash': tx_hash, 'blockNumber': tx.blockNumber }

        tx_list.append(tx_data)
    return tx_list

def klaytn_nft_tx_display(web3, mycontract, tx_list):
    '''
    use              : 리스트에 담긴 거래 내역을 Display 표기
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
                       3. tx_list : 거래 내역이 담긴 리스트
    output parameter : None
    '''
    for tx_data in tx_list:
        token_uri = klaytn_NFT_uri(web3, mycontract, tx_data['tokenId'])
        print(f"from=[{tx_data['from']}], to=[{tx_data['to']}], tokenId=[{tx_data['tokenId']}], event=[{tx_data['event']}], transactionHash=[{tx_data['transactionHash']}],token_uri=[{token_uri}], blockNumber=[{tx_data['blockNumber']}]")


def get_image_url(tokenuri):

    with urllib.request.urlopen(tokenuri) as url:
        s = url.read()
        sdata = json.loads(s)
        imageurl = sdata['image']

        return imageurl

def NFT_snapshot(web3,mycontract):
    '''
    use              : Token id 별 owner와 Token uri를 리스트로 정리
    input parameter  : web3 : web3 네트워크 연결
          mycontract : abi로 활성화한 컨트랙트 함수들
    output parameter : owner_list
    '''
    from web3.middleware import geth_poa_middleware
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    total = klaytn_NFT_totalsuply(web3, mycontract)
    owner_list = []
    for i in range(1, total+1):
        try:
            owner = klaytn_NFT_owner(web3, mycontract, i)
            uri = klaytn_NFT_uri(web3, mycontract, i)
            owner_data = {'TokenId': i, 'Owner': owner, 'URI': uri}
            owner_list.append(owner_data)
        except Exception as e:
            continue
    return owner_list


def Klaytn_mintNFT(web3, mycontract, sender_pv, sender_Add, ipfsUri):
    '''
    use             : NFT minting
    input parameter : 1. web3 : web3 네트워크 연결
                      2. mycontract : abi로 활성화한 컨트랙트 함수들
                      3. sender_pv : 보내는 사람의 privateKey
                      4. sender_Add : 보내는 사람의 주소
                      5. ipfsUri : 민팅시킬 그림의 Meta data
    output parameter : gncHash
    '''
    senderAddress = web3.toChecksumAddress(sender_Add)
    nonce = web3.eth.get_transaction_count(senderAddress)
    print(nonce)
    gas_estimate = mycontract.functions.mintNFT(ipfsUri).estimate_gas({'from': senderAddress})
    tx =  mycontract.functions.mintNFT(ipfsUri).build_transaction(
        {
            'from': senderAddress,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            'gasPrice': 25000000000,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, sender_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    return gncHash


def Klaytn_airdrop_mint(web3,mycontract,sender_pv,sender_Add,reciver_Add,ipfsUri):
    '''
    use              : 다른 계정에 보내면서 minting
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
                       3. sender_pv : 보내는 사람의 privateKey
                       4. sender_Add : 보내는 사람의 주소
                       5. reciver_Add : NFT를 받는 사람의 주소
                       6. ipfsUri : 민팅시킬 그림의 Meta data
    output parameter : gncHash
    '''
    nonce = web3.eth.get_transaction_count(sender_Add)
    senderAddress = web3.toChecksumAddress(sender_Add)
    reciverAddress = web3.toChecksumAddress(reciver_Add)
    toKenID = klaytn_NFT_totalsuply(web3, mycontract)+1
    gas_estimate =mycontract.functions.mintWithTokenURI(reciverAddress, toKenID, ipfsUri).estimate_gas({'from': senderAddress})
    tx = mycontract.functions.mintWithTokenURI(reciverAddress, toKenID, ipfsUri).build_transaction(
        {
            'from': senderAddress,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            'gasPrice': 25000000000,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, sender_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    return gncHash

def Klaytn_NFT_transfer(web3,mycontract,sender_pv,sender_Add,reciver_Add,token_id):
    '''
    use             : 소유중인 nft 보내기
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
                       3. sender_pv : 보내는 사람의 privateKey
                       4. sender_Add : 보내는 사람의 주소
                       5. reciver_Add : NFT를 받는 사람의 주소
                       6. token_id : 보낼 NFT의 Token id
    output parameter : gncHash
     '''
    senderAddress = web3.toChecksumAddress(sender_Add)
    reciverAddress = web3.toChecksumAddress(reciver_Add)
    nonce = web3.eth.get_transaction_count(senderAddress)

    gas_estimate = mycontract.functions.transferFrom(sender_Add, reciverAddress, token_id).estimate_gas({'from': senderAddress})
    tx =  mycontract.functions.transferFrom(sender_Add, reciverAddress, token_id).build_transaction(
        {
            'from': senderAddress,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            'gasPrice': 25000000000,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, sender_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    return gncHash



if __name__ == "__main__":
    web3 = connectWeb3("baobab")
    mycontract = klaytn_contract_abi(web3,"", '')
    klaytn_NFT_totalsuply(web3, mycontract)
    first_block = get_first_block(web3, mycontract)
    print(first_block)
    NFT_snapshot1 = NFT_snapshot(web3, mycontract)
    print(NFT_snapshot1)
    ret_list = klaytn_NFT_list(web3,mycontract,first_block,100)
    klaytn_nft_tx_display(web3,mycontract,ret_list)
    print("-------------")


