from web3 import Web3
import solcx
import json
import datetime
solcx.install_solc('0.5.6')
"""
compile issue 기록 date 2022-10-17
erc-721는 0.5.0 버전으로 컴파일시 문제없으나
erc-20은 0.5.0 버전에서 상속 에러 발생
0.5.6으로 변경해서 상속부분 해결후 multisend 함수의 view부분을 삭제하고 payable로 변경해서 컴파일시 성공

"""


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

def getweb3_url(connect_host=None): #web3 connect rpcuri 선택
    if connect_host is None:
        infura_url = "http://localhost:8545"
    elif connect_host == "baobab":
        infura_url = "https://api.baobab.klaytn.net:8651"
    elif connect_host == "mainnet":
        infura_url = "https://klaytn-mainnet-rpc.allthatnode.com:8551"
    else:
        infura_url = "http://localhost:8545"
    return web3
def klaytn_contract_abi(web3,contractAddress,abi): #컨트랙트 abi 연결
    file = open(abi, 'r', encoding='utf-8')
    mycontract = web3.eth.contract(abi=file.read(), address=contractAddress)
    return mycontract

def klaytn_token_balance(web3,mycontract,useraddress): #coin 소유량 조회
    token_balance = mycontract.functions.balanceOf(useraddress).call()
    return token_balance

def klaytn_token_totalsuply(web3,mycontract):
    '''
    use              : Token총 발행량 조회
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract: abi로 활성화한 컨트랙트 함수들
    output parameter : total_token
     '''

    total_token = mycontract.functions.totalSupply().call()
    print(total_token)
    return total_token
def klaytn_get_first_block(web3,mycontract):
    '''
    use              : Token 컨트랙트 첫거래 Block number를 가져옴(주의: 후에 추가 발행시 함수 사용불가 최초 1회용 함수)
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
    output parameter : first_block_num
    '''
    total = klaytn_token_totalsuply(web3, mycontract)
    myFilter = mycontract.events.Transfer.createFilter(fromBlock=0, argument_filters={'value': total})
    txs = myFilter.get_all_entries()
    first_block_num = txs[0].blockNumber
    return first_block_num


def klaytn_token_list(web3,mycontract,startBlock,fromadress = None):
    '''
        use              : filter를 이용해서 거래내역을 가져온다
        input parameter  : 1. web3 : web3 네트워크 연결
                           2. mycontract : abi로 활성화한 컨트랙트 함수들
                           3. startBlock : 토큰이 거래가시작되는 블록
                           4. fromadress : 발신자 주소를 지정하면 그주소에 관한 거래 내역이 출력된다 (선택사항)
        output parameter : tx_list
    '''
    tx_list = []
    if fromadress is None:
        myFilter =  mycontract.events.Transfer.createFilter(fromBlock=startBlock)
    else:
        myFilter =  mycontract.events.Transfer.createFilter(fromBlock=startBlock, argument_filters={'from': fromadress})
    txs = myFilter.get_all_entries()
    for tx in txs:
        tx_hash = (tx.transactionHash).hex()
        getblock = web3.eth.get_block(tx.blockNumber).timestamp
        date = datetime.datetime.fromtimestamp(int(getblock)).strftime('%Y-%m-%d %H:%M:%S')
        tx_data = {'from': tx.args['from'], 'to': tx.args['to'], 'value': tx.args['value'], 'event': tx.event,'transactionHash': tx_hash, 'blockNumber': tx.blockNumber ,'date': date }

        tx_list.append(tx_data)
    return tx_list

def klaytn_token_tx_display(tx_list):
    '''
            use              : klaytn_token_list에서 나온 리스트를 조건에 맞춰 보기 좋게 나열하기위한 함수
            input parameter  : 1. tx_list : klaytn_token_list에서 나온 결과값
            output parameter :
    '''
    for tx_data in tx_list:
        print(f"from=[{tx_data['from']}], to=[{tx_data['to']}],value=[{tx_data['value']}], event=[{tx_data['event']}], transactionHash=[{tx_data['transactionHash']}],blockNumber=[{tx_data['blockNumber']}],date=[{tx_data['date']}]")

def get_timestamp(web3, tx_list):
    """
    use : klaytn_token_list 함수 연계 해서 거래 시간 정보 가져오는 함수
    """
    timestamp = []
    for tx_data in tx_list:
        blocknum = tx_data['blockNumber']
        # print(blocknum)
        getblock = web3.eth.get_block(blocknum).timestamp
        date = datetime.datetime.fromtimestamp(int(getblock)).strftime('%Y-%m-%d %H:%M:%S')
        timestamp.append(date)

    print(timestamp)
    return timestamp
def klaytn_token_transfer(web3,mycontract,sender_pv,sender_add,reciver_add,amt):
    '''
            use              : kip-7 기반의 토큰을 보내기 위한 메서드
            input parameter  : 1. web3 : web3 네트워크 연결
                               2. mycontract : abi로 활성화한 컨트랙트 함수들
                               3. sender_pv : 발신자의 pvkey
                               4. sender_add : 발신자 주소
                               5. reciver_add : 수신자 주소
                               6. amt : 보내는 양
            output parameter : gncHash
    '''

    sendAddress = web3.toChecksumAddress(sender_add)
    receiveAddress = web3.toChecksumAddress(reciver_add)
    nonce = web3.eth.get_transaction_count(sendAddress)
    amount = amt * web3.toWei(1, "ether")
    gas_estimate = mycontract.functions.safeTransfer(receiveAddress, amount).estimate_gas({'from': sendAddress})

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

def klaytn_token_multisend(web3,mycontract,sender_pv,sender_add,reciver_addresses,amts):
    '''
                use              : kip-7 기반의 토큰 여러명에게 한번에 보내기
                input parameter  : 1. web3 : web3 네트워크 연결
                                   2. mycontract : abi로 활성화한 컨트랙트 함수들
                                   3. sender_pv : 발신자의 pvkey
                                   4. sender_add : 발신자 주소
                                   5. reciver_add : 수신자의 주소(리스트로 받아야 한다.)
                                   6. amt : 보내는 양(리스트로 받아야 한다.)
                output parameter : gncHash
        '''

    sendAddress = web3.toChecksumAddress(sender_add)
    for i in range(len(reciver_addresses)):
        reciver_addresses[i] = web3.toChecksumAddress(reciver_addresses[i])
        amts[i] = amts[i] * web3.toWei(1, "ether")
    nonce = web3.eth.get_transaction_count(sendAddress)
    gas_estimate = mycontract.functions.multisend(reciver_addresses, amts).estimate_gas({'from': sendAddress})
    print(gas_estimate)
    tx = mycontract.functions.multisend(reciver_addresses, amts).build_transaction(
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







def Klaytn_deploy_kip7_contract(web3,file_path,address,pk_key,name,symbol,totalsupply):
    '''
        use              :  kip-7 컨트랙트 배포
        input parameter  : 1. web3 : web3 네트워크 연결
                           2. file_path : sol 파일 경로
                           3. address : 발행하는 사람의 주소
                           4. pk_key : 발행하는 사람의 pvkey
                           5. name : 컨트랙트 이름
                           6. symbol : 컨트랙트 symbol
                           7. totalsupply : 총수량
        output parameter : contractAddress,abi
         '''
    res = solcx.compile_files(
        [file_path],
        output_values=["abi", "bin"],
        solc_version="0.5.6"
    )
    abi = res[file_path +':Mycoin']['abi']
    with open('kip7_contract_abi', 'w') as f:
        json.dump(abi, f)

    bytecode = res[file_path +':Mycoin']['bin']

    mycontract = web3.eth.contract(abi=abi, bytecode=bytecode)
    acct = web3.eth.account.privateKeyToAccount(pk_key)
    nonce = web3.eth.get_transaction_count(address)
    total = totalsupply * web3.toWei(1, "ether")
    tx = mycontract.constructor(name, symbol, 18, total).build_transaction(
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

if __name__ == "__main__":
    """
    테스트 완료 
    2022-10-17
    """
    web3 = connectWeb3("baobab")
    address = '...'
    pv = '...'
    #contract_add = Klaytn_deploy_kip7_contract(web3, r"./contracts/Mycoin.sol", address, pv, "JangT3P2s", "T4P2s", 50000000)
    #print(contract_add)
    contract_add = "..."
    mycontract = klaytn_contract_abi(web3, contract_add, 'kip7_contract_abi')

    reciver_add = ["...","..."]
    amts = [50,10]
    #klaytn_token_multisend(web3, mycontract, pv, address, reciver_add, amts)
    #klaytn_token_transfer(web3, mycontract, pv, address, reciver_add[1], amts[1])
    startBlock = klaytn_get_first_block(web3, mycontract)

    lists = klaytn_token_list(web3, mycontract, startBlock)


    klaytn_token_tx_display(lists)


