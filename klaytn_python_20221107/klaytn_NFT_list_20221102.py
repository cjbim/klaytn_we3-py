from web3 import Web3
import urllib
import json
import solcx
import datetime
version = solcx.install_solc('0.5.6') # 최초 1회에만 사용
'''
date = 2022-10-07
2022-10-11 deploy 추가 
'''

def klaytn_connect_web3(connect_host=None):
    '''
    use              : Network 연결
    input parameter  : 1. None      : parameter가 없는 경우 localhost로 연결
                       2. 'baobab'  : Klaytn 테스트넷
                       3. 'mainnet' : Klaytn 메인넷
    output parameter : web3
    '''
    if connect_host is None:
        klaytn_url = "http://localhost:8545"
    elif connect_host == "baobab":
        klaytn_url = "https://api.baobab.klaytn.net:8651"
    elif connect_host == "klaytn":
        klaytn_url = "https://klaytn-mainnet-rpc.allthatnode.com:8551"
    else:
        klaytn_url = "http://localhost:8545"
    web3 = Web3(Web3.HTTPProvider(klaytn_url))
    return web3


def getweb3_uri(connect_host=None):
    '''
    use              : Network uri 가져오기
    input parameter  : 1. None      : parameter가 없는 경우 localhost로 연결
                       2. 'baobab'  : Klaytn 테스트넷
                       3. 'mainnet' : Klaytn 메인넷
    output parameter : klaytn_url
    '''
    if connect_host is None:
        klaytn_url = "http://localhost:8545"
    elif connect_host == "baobab":
        klaytn_url = "https://api.baobab.klaytn.net:8651"
    elif connect_host == "mainnet":
        klaytn_url = "https://klaytn-mainnet-rpc.allthatnode.com:8551"
    else:
        klaytn_url = "http://localhost:8545"
    return klaytn_url


def klaytn_check_network(web3):
    check = web3.net.version
    if check == "1001":
        print("baobab")
    elif check == "8217":
        print("mainnet")
    else:
        print("unknown network")


def klaytn_NFT_contract_abi(web3, contractAddress, abi):
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

def klaytn_NFT_totalsuply(web3, mycontract):
    '''
    use              : NFT총 발행량 조회
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract: abi로 활성화한 컨트랙트 함수들
    output parameter : total_token
     '''
    total_token = mycontract.functions.totalSupply().call()
    print(total_token)
    return total_token


def klaytn_NFT_owner(web3, mycontract, token_id):
    '''
    use              : NFT Token id Owner 주소 조회
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
                       3. token_id : 조회할 토큰 id
    output parameter : token_owner
    '''
    token_owner = mycontract.functions.ownerOf(token_id).call()
    return token_owner

def klaytn_NFT_uri(web3, mycontract, token_id):
    '''
    use             : NFT Token id uri 조회
    input parameter : 1. web3 : web3 네트워크 연결
                      2. mycontract : abi로 활성화한 컨트랙트 함수들
                      3. token_id : 조회할 토큰 id
    output parameter : tokenid_uri
    '''
    tokenid_uri = mycontract.functions.tokenURI(token_id).call()
    return tokenid_uri

def klaytn_NFT_change_ownership(web3, mycontract, owner_add , owner_pv, new_owner_add):
    '''
        use             : NFT 컨트랙트의 모든 권한을 위임하는 함수이다 ( 민감한 함수 주의 요함 !!)
        input parameter : 1. web3 : web3 네트워크 연결
                          2. mycontract : abi로 활성화한 컨트랙트 함수들
                          3. pv : 현재 주인의 개인키
                          4. owner : 현재 주인의 주소
                          5. new_owner : 새로운 주인의 주소
        output parameter : gncHash
    '''

    senderAddress = web3.toChecksumAddress(owner_add)
    reciverAddress = web3.toChecksumAddress(new_owner_add)
    nonce = web3.eth.get_transaction_count(senderAddress)

    gas_estimate = mycontract.functions.transferOwnership(reciverAddress).estimate_gas(
        {'from': senderAddress})
    tx = mycontract.functions.transferOwnership(reciverAddress).build_transaction(
        {
            'from': senderAddress,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            'gasPrice': 25000000000,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, owner_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)

    return gncHash

def klaytn_NFT_addminter(web3, mycontract, owner_add, owner_pv, reciever_add):
    '''
            use             : NFT 컨트랙트의 민팅 권한을 부여한다 ownership은 유지 
            input parameter : 1. web3 : web3 네트워크 연결
                              2. mycontract : abi로 활성화한 컨트랙트 함수들
                              3. owner_add : 주인 주소
                              4. owner_pv : 주인 개인키
                              5. reciever_add : 권한 받을 주소
            output parameter : gncHash
    '''

    senderAddress = web3.toChecksumAddress(owner_add)
    reciverAddress = web3.toChecksumAddress(reciever_add)
    nonce = web3.eth.get_transaction_count(senderAddress)

    gas_estimate = mycontract.functions.addMinter(reciverAddress).estimate_gas(
        {'from': senderAddress})
    tx = mycontract.functions.addMinter(reciverAddress).build_transaction(
        {
            'from': senderAddress,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            'gasPrice': 25000000000,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, owner_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)

    return gncHash

def klaytn_NFT_get_first_block(web3, mycontract):
    '''
    use              : NFT 컨트랙트 첫거래 Block number를 가져옴
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
    output parameter : first_block_num
    '''
    myFilter = mycontract.events.Transfer.createFilter(fromBlock=0, argument_filters={'tokenId': 1})
    txs = myFilter.get_all_entries()

    try:
        first_block_num = txs[0].blockNumber
    except Exception as e:
        raise e

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
        getblock = web3.eth.get_block(tx.blockNumber).timestamp
        date = datetime.datetime.fromtimestamp(int(getblock)).strftime('%Y-%m-%d %H:%M:%S')
        tx_data = {'from': tx.args['from'], 'to': tx.args['to'], 'tokenId': tx.args['tokenId'], 'event': tx.event,'transactionHash': tx_hash, 'blockNumber': tx.blockNumber, 'date': date }
        tx_list.append(tx_data)
    return tx_list

def klaytn_NFT_tx_display(web3, mycontract, tx_list):
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


def klaytn_NFT_get_image_url(tokenuri):

    with urllib.request.urlopen(tokenuri) as url:
        s = url.read()
        sdata = json.loads(s)
        imageurl = sdata['image']

        return imageurl

def klaytn_NFT_snapshot(web3,mycontract):
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


def klaytn_NFT_airdrop_mint(web3, mycontract, sender_add , sender_pv, receiver_add, ipfsUri):
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
    senderAddress = web3.toChecksumAddress(sender_add)
    reciverAddress = web3.toChecksumAddress(receiver_add)
    nonce = web3.eth.get_transaction_count(senderAddress)
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

def Klaytn_NFT_multimint(web3, mycontract, sender_add , sender_pv, receiver_adds, ipfsUris, tokenids):

    nonce = web3.eth.get_transaction_count(sender_add)
    senderAddress = web3.toChecksumAddress(receiver_adds)
    for i in range(len(receiver_Adds)):
        receiver_Adds[i] = web3.toChecksumAddress(receiver_Adds[i])

    gas_estimate = mycontract.functions.multimint(receiver_Adds, tokenids, ipfsUris).estimate_gas(
        {'from': senderAddress})
    tx = mycontract.functions.multimint(receiver_Adds, tokenids, ipfsUris).build_transaction(
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


def Klaytn_NFT_transfer(web3, mycontract, sender_add, sender_pv, reciver_add, token_id):
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
    senderAddress = web3.toChecksumAddress(sender_add)
    reciverAddress = web3.toChecksumAddress(reciver_add)
    nonce = web3.eth.get_transaction_count(senderAddress)

    gas_estimate = mycontract.functions.transferFrom(senderAddress, reciverAddress, token_id).estimate_gas({'from': senderAddress})
    tx =  mycontract.functions.transferFrom(senderAddress, reciverAddress, token_id).build_transaction(
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


def Klaytn_deploy_kip17_contract(web3, file_path, address, pk_key, name, symbol):
    '''
        use              :  kip-17 컨트랙트 배포
        input parameter  : 1. web3 : web3 네트워크 연결
                           2. file_path : sol 파일 경로
                           3. address : 발행하는 사람의 주소
                           4. pk_key : 발행하는 사람의 pvkey
                           5. name : 컨트랙트 이름
                           6. symbol : 컨트랙트 symbol
        output parameter : contractAddress,abi
         '''
    res = solcx.compile_files(
        [file_path],
        output_values=["abi", "bin"],
        solc_version="0.5.6"
    )
    abi = res[file_path+':MyNFT']['abi']
    with open(f'{name}abi', 'w') as f:
        json.dump(abi, f)
    bytecode = res[file_path+':MyNFT']['bin']
    mycontract = web3.eth.contract(abi=abi, bytecode=bytecode)
    address = web3.toChecksumAddress(address)
    acct = web3.eth.account.privateKeyToAccount(pk_key)
    nonce = web3.eth.get_transaction_count(address)
    tx = mycontract.constructor(name, symbol).build_transaction(
        {
            "from": address,
            "nonce": nonce,
            "gasPrice": 25000000000

        }
    )
    signed = acct.signTransaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress



def klaytn_NFT_result_list(web3, gncHash):
    tx_list = []
    transactionHash = {'transactionHash': web3.toHex(gncHash.transactionHash)}
    tx_list.append(transactionHash)
    blockNumber = {'blockNumber': gncHash.blockNumber}
    tx_list.append(blockNumber)
    blockhash = web3.toHex(gncHash.blockHash)
    blcok_hash = {'blockhash': blockhash}
    tx_list.append(blcok_hash)
    cumulativeGasUsed = {'cumulativeGasUsed': gncHash.cumulativeGasUsed}
    tx_list.append(cumulativeGasUsed)
    to = {'to': gncHash.to}
    tx_list.append(to)
    print(tx_list)



if __name__ == "__main__":
    web3 = klaytn_connect_web3("baobab")
    klaytn_check_network(web3)
    address = '...'
    pv = '...'
    reciever = '...'
    reciever_pv = "..."
    #contract_address = Klaytn_deploy_kip17_contract(web3, r"./contracts/MyNFT.sol", address , pv,'newtelas','nts')
    #print(contract_address)
    mycontract = klaytn_NFT_contract_abi(web3, "0xd466D84cC1D80ba30a245dde6386BF52D232a295",'newtelasabi')
    receiver_Adds = ["0xE15C93e446C9E726d997017e222B2aA6C110009a","0x867c3DDa7CD6d92EaF206b010d8c687693A97485",address , address]
    meta = "https://ipfs.io/ipfs/QmYFU8SiheGqSVY5Vyr6CLfDHhqExmg38pSjfmL8LZiP8L"
    ipfsUris = [ meta,  meta,  meta,  meta]
    total =  klaytn_NFT_totalsuply(web3,mycontract)
    tokenids = [total+1,total+2,total+3,total+4]
    #multi = Klaytn_NFT_multimint(web3, mycontract, pv, address, receiver_Adds, ipfsUris, tokenids)
    #print(multi)
    mint = klaytn_NFT_airdrop_mint(web3, mycontract, pv, address, address, meta)
    print(mint)
    klaytn_NFT_result_list(web3, mint)
    #approval = klaytn_NFT_setApprovalForAll(web3, mycontract, address, pv, reciever)
    #print(approval)
    #change__owner = klaytn_NFT_uri(web3, mycontract, pv, address, reciever)
    #print(change__owner)

    exit()
    for i in range(1,2):
        #meta = get_metadata(f'{i}.json','image')
        meta = "https://ipfs.io/ipfs/QmYFU8SiheGqSVY5Vyr6CLfDHhqExmg38pSjfmL8LZiP8L"
        mint = klaytn_NFT_airdrop_mint(web3,mycontract,pv,address,address,meta)
        print(mint)

