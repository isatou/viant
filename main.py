from web3 import Web3
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('address')
parser.add_argument('--host', help='Web3 Host Domain')
args = parser.parse_args()

w3 = Web3(Web3.HTTPProvider(args.host))

def find_transaction(address, block):
    """ checks if the block contains the contract creation
        transaction of the contract address provided
    """

    # find the total number of transactions within block
    total_transactions = w3.eth.getBlockTransactionCount(block)

    transaction_hashes = []
    for j in range(total_transactions):
        # loop through the transactions in the block, and check to see
        # if the "to" field is empty, that means that a new contract
        # was created in that transaction
        d = w3.eth.getTransactionFromBlock(block, j)
        if d.to is None:
            transaction_hashes.append(d.hash)

    for transaction_hash in transaction_hashes:
        # loop through the transactions where a new contract was created,
        # and compare the contract addresses
        # if there is a match, then it is the transaction that was used
        # to deploy the contract
        transaction_receipt = w3.eth.getTransactionReceipt(transaction_hash)
        if transaction_receipt.contractAddress == address:
            return True, w3.toHex(transaction_receipt.blockHash), w3.toHex(transaction_receipt.transactionHash)
    return False, None, None

def get_contract_details(address, start_block, end_block):
    """
        searches for the hashes of the block and transaction
        from which a contract address was deployed
    """
    block = int((start_block + end_block)/2) 
    try:
        code = w3.eth.getCode(address, block_identifier=block)
    except ValueError:
        """ a ValueError occurs sometimes, e.g.
            ValueError: {'code': -32000, 
            'message': 'missing trie node 1af75aaf74309466d672fbaeb28d0b7e29ba7278de4771f2284c090855185894 (path )'}
        """
        return get_contract_details(address, start_block, end_block)
    if code == b'':
        if start_block == end_block:
            # transaction details could not be found 
            return None, None
        start_block = block
        return get_contract_details(address, start_block, end_block)
    else:
        found, block_hash, transaction_hash = find_transaction(address, block)
        if found:
            return block_hash, transaction_hash
        end_block = block
        return get_contract_details(address, start_block, end_block)

START_BLOCK = 0
LATEST_BLOCK = w3.eth.blockNumber

if not w3.isChecksumAddress(args.address):
    print("Invalid address")
else:
    block_hash, transaction_hash = get_contract_details(args.address, START_BLOCK, LATEST_BLOCK)
    print('Block: ', block_hash)
    print('Transaction: ', transaction_hash)
