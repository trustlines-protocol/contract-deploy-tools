from web3 import Web3


def deploy_compiled_contract(*, abi, bytecode, web3, constructor_args=()):
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    txhash = contract.constructor(*constructor_args).transact()
    receipt = wait_for_successful_transaction_receipt(web3, txhash)
    address = receipt["contractAddress"]
    return contract(address)


class TransactionFailed(Exception):
    pass


def wait_for_successful_transaction_receipt(web3: Web3, txid: str, timeout=180) -> dict:
    """See if transaction went through (Solidity code did not throw).
    :return: Transaction receipt
    """
    receipt = web3.eth.waitForTransactionReceipt(txid, timeout=timeout)
    tx_info = web3.eth.getTransaction(txid)
    status = receipt.get("status", None)
    if receipt["gasUsed"] == tx_info["gas"] or status is False:
        raise TransactionFailed
    return receipt
