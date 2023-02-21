from web3 import Web3
import urllib
import json
import solcx
import datetime
from urllib3.util.retry import Retry
version = solcx.install_solc('0.5.6') # 최초 1회에만 사용
'''
update realize
date = 2022-10-07
2022-10-11 deploy 추가 
2023-01-06 transaction return값 dict로 리턴 설정
2023-01-27 contract abi 함수 파라미터가 josn형태로 받으므로 file read 부분 삭제
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
    web3 = Web3(Web3.HTTPProvider(klaytn_url,request_kwargs={'timeout': 10}))
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
    elif connect_host == "klaytn":
        klaytn_url = "https://klaytn-mainnet-rpc.allthatnode.com:8551"
    else:
        klaytn_url = "http://localhost:8545"
    return klaytn_url


def klaytn_check_network(web3):
    check = web3.net.version
    if check == "1001":
        network = "baobab"
    elif check == "8217":
        network = "klaytn"
    else: 
        network = "unknown"

    return network

def klaytn_klayscope_link(network,contract_address):
    if network == "klaytn":
        uri = f"https://scope.klaytn.com/account/{contract_address}?tabId=txList"
    if network == "baobab":
        uri = f"https://baobab.scope.klaytn.com/account/{contract_address}?tabId=txList"
    else:
        uri = "unknown"
    return uri

def klaytn_klay_getbalance(web3,account):
        account = web3.toChecksumAddress(account)
        balance = web3.fromWei(web3.eth.getBalance(account), 'ether')
        return balance

def klaytn_NFT_contract_abi(web3, contractAddress, abi):
    '''
    use              : 컨트랙트 주소와 abi를 통해 스마트 컨트랙트 함수를 사용하기위해 연결
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. contractAddress: 컨트랙트 주소
                       3. abi: abi 경로
    output parameter : mycontract
    '''
    #file = open(abi, 'r', encoding='utf-8')
    contractaddress = web3.toChecksumAddress(contractAddress)
    #mycontract = web3.eth.contract(abi=file.read(), address=contractaddress)
    mycontract = web3.eth.contract(abi=abi, address=contractaddress)
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
    gnc_dict = {'transactionHash': web3.toHex(gncHash.transactionHash), 'blockNumber': gncHash.blockNumber,
                'blockhash': web3.toHex(gncHash.blockHash),
                'tx_fee': (gncHash.effectiveGasPrice * gncHash.gasUsed) * web3.fromWei(1, "ether"), 'to': gncHash.to}
    return gnc_dict

def klaytn_NFT_isOwner(web3, mycontract,address):
    confirm_address = web3.toChecksumAddress(address)
    role = mycontract.functions.owner().call()
    owner_address = web3.toChecksumAddress(role)

    if confirm_address == owner_address:
        txt = "owner 권한이 있습니다."
    else :
        txt = "owner 권한이 없습니다."

    print(txt)

    return txt

def klaytn_NFT_addminter(web3, mycontract, owner_add, owner_pv, reciever_add):
    '''
            use             : NFT 컨트랙트의 민팅 권한을 부여 완전한 권한을 넘기려면 이것도 사용해야한다.
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

    gas_estimate = mycontract.functions.addMinter(reciverAddress).estimate_gas({'from': senderAddress})
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
    gnc_dict = {'transactionHash': web3.toHex(gncHash.transactionHash), 'blockNumber': gncHash.blockNumber,
                'blockhash': web3.toHex(gncHash.blockHash),
                'tx_fee': (gncHash.effectiveGasPrice * gncHash.gasUsed) * web3.fromWei(1, "ether"), 'to': gncHash.to}
    return gnc_dict
def klaytn_NFT_isminter(web3, mycontract,address):
    confirm_address = web3.toChecksumAddress(address)
    role = mycontract.functions.isMinter(confirm_address).call()
    if role is True:
        txt = "발행 권한이 있습니다."
    else :
        txt = "발행 권한이 없습니다."

    print(txt)

    return txt


def klaytn_NFT_addpauser(web3, mycontract, owner_add, owner_pv, reciever_add):
    '''
            use             : NFT 컨트랙트의 중지 권한을 부여 완전한 권한을 넘기려면 이것도 사용해야한다.
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

    gas_estimate = mycontract.functions.addPauser(reciverAddress).estimate_gas({'from': senderAddress})
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
    gnc_dict = {'transactionHash': web3.toHex(gncHash.transactionHash), 'blockNumber': gncHash.blockNumber,
                'blockhash': web3.toHex(gncHash.blockHash),
                'tx_fee': (gncHash.effectiveGasPrice * gncHash.gasUsed) * web3.fromWei(1, "ether"), 'to': gncHash.to}
    return gnc_dict


def klaytn_NFT_isPauser(web3, mycontract,address):
    confirm_address = web3.toChecksumAddress(address)
    role = mycontract.functions.isPauser(confirm_address).call()
    if role is True:
        txt = "중지 권한이 있습니다."
    else :
        txt = "중지 권한이 없습니다."

    print(txt)

    return txt

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
    gnc_dict = {'transactionHash': web3.toHex(gncHash.transactionHash), 'blockNumber': gncHash.blockNumber,
                'blockhash': web3.toHex(gncHash.blockHash),
                'tx_fee': (gncHash.effectiveGasPrice * gncHash.gasUsed) * web3.fromWei(1, "ether"), 'to': gncHash.to}
    return gnc_dict

def klaytn_NFT_multimint(web3, mycontract, sender_add , sender_pv, receiver_adds, ipfsUris, tokenids):

    nonce = web3.eth.get_transaction_count(sender_add)
    senderAddress = web3.toChecksumAddress(sender_add)
    for i in range(len(receiver_Adds)):
        receiver_Adds[i] = web3.toChecksumAddress(receiver_adds[i])

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
    gnc_dict = {'transactionHash': web3.toHex(gncHash.transactionHash), 'blockNumber': gncHash.blockNumber,
                'blockhash': web3.toHex(gncHash.blockHash),
                'tx_fee': (gncHash.effectiveGasPrice * gncHash.gasUsed) * web3.fromWei(1, "ether"), 'to': gncHash.to}
    return gnc_dict


def klaytn_NFT_transfer(web3, mycontract, sender_add, sender_pv, reciver_add, token_id):
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
    gnc_dict = {'transactionHash': web3.toHex(gncHash.transactionHash), 'blockNumber': gncHash.blockNumber, 'blockhash': web3.toHex(gncHash.blockHash), 'tx_fee': (gncHash.effectiveGasPrice * gncHash.gasUsed) * web3.fromWei(1, "ether") , 'to': gncHash.to }

    return gnc_dict


def klaytn_deploy_kip17_contract(web3, file_path, address, pk_key, name, symbol,reciever):
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
   # with open(f'./common/{name}abi', 'w') as f:
   #     json.dump(abi, f)
    bytecode = res[file_path+':MyNFT']['bin']
    mycontract = web3.eth.contract(abi=abi, bytecode=bytecode)
    address = web3.toChecksumAddress(address)
    acct = web3.eth.account.privateKeyToAccount(pk_key)
    nonce = web3.eth.get_transaction_count(address)
    tx = mycontract.constructor(name, symbol,reciever).build_transaction(
        {
            "from": address,
            "nonce": nonce,
            "gasPrice": 25000000000

        }
    )
    signed = acct.signTransaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(tx_hash)
    gnc_dict = {'transactionHash': web3.toHex(gncHash.transactionHash), 'blockNumber': gncHash.blockNumber,
                'blockhash': web3.toHex(gncHash.blockHash),
                'tx_fee': (gncHash.effectiveGasPrice * gncHash.gasUsed) * web3.fromWei(1, "ether"), 'to': gncHash.to}

    return gncHash.contractAddress,abi, gnc_dict


if __name__ == "__main__":
    

