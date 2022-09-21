from web3 import Web3
import random

def connectWeb3(connect_host=None):
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


def randomnum():
    list_datas = list(range(1, 101))
    del_lists = [17, 1, 10, 19, 23, 26, 27, 31]
    for del_list in del_lists:
#        print(f"del_list=[{del_list}]")
        list_datas.remove(del_list)

    #print(list_datas)
    random.shuffle(list_datas)
    #print(list_datas[0])

    return list_datas

def user_address():
    file = open('user_Address.txt','r')
    new_list = list(file)
    lt = list(map(lambda s: ''.join(s.split()), new_list))
    #print(lt)
    return lt

def mintNFT(web3,contractAddress,i):
    private_key1 = ''
    fromadress = ''
    nonce = web3.eth.get_transaction_count(fromadress)
    contractAddress = web3.toChecksumAddress(contractAddress)
    token_id = randomnum()
    user = user_address()
    file = open('17deployedABI', 'r', encoding='utf-8')
    mycontract = web3.eth.contract(address=contractAddress, abi=file.read())
    gas_estimate = mycontract.functions.transferFrom(fromadress, f"'{user[i]}'", token_id[i]).estimate_gas()
    print(f"gas_estimate=[{gas_estimate}]")
    tx = mycontract.functions.transferFrom(fromadress,f"'{user[i]}'",token_id[i]).build_transaction(
        {   #1.보내는사람주소 2.받을사람 3.토큰id
            'from': fromadress,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            'gasPrice': 25000000000,

        }
    )

    # 새토큰 띄워서 테스트 진행 바람

    signed_txn = web3.eth.account.sign_transaction(tx, private_key1)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    print(f"gncHash=[{gncHash}]")


if __name__ == "__main__":
    token_id = randomnum()
    print(token_id[0])
    user = user_address()
    print(f"'{user[0]}'")