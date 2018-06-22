from web3 import Web3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('address')
parser.add_argument('--host', help='Web3 Host Domain')
args = parser.parse_args()

w3 = Web3(Web3.HTTPProvider(args.host))

START_BLOCK = 0
LATEST_BLOCK = w3.eth.blockNumber

done = False
for block in range(START_BLOCK, LATEST_BLOCK+1):
    # loop through from block START_BLOCK to the latest block
    print('current block', block)

    # find the total number of transactions without block
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
        if transaction_receipt.contractAddress == args.address: 
            print('Block: ', w3.toHex(transaction_receipt.blockHash))
            print('Transaction: ', w3.toHex(transaction_receipt.transactionHash))
            done = True
            break
    if done:
        break
