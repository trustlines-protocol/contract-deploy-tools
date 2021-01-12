from typing import Dict, Iterable

from hexbytes import HexBytes
from web3 import Web3
from web3._utils.transactions import fill_transaction_defaults
from web3.eth import Account
from web3.types import TxParams, TxReceipt


class TransactionsFailed(Exception):
    def __init__(self, failed_tx_hashs):
        self.failed_tx_hashs = failed_tx_hashs


class TransactionFailed(Exception):
    pass


def send_transaction(*, web3: Web3, transaction_options: TxParams, private_key=None):
    """
    Send the transaction with given transaction options
    Will either use an account of the node(default), or a local private key(if given) to sign the transaction.
    It will not block until the transaction was successfully mined.

    Returns: The sent transaction hash
    """

    if private_key is not None:
        account = Account.from_key(private_key)

        if (
            "from" in transaction_options
            and transaction_options["from"] != account.address
        ):
            raise ValueError(
                "From can not be set in transaction_options if a private key is used"
            )
        transaction_options["from"] = account.address

        transaction = fill_nonce(web3, transaction_options)
        transaction = fill_transaction_defaults(web3, transaction)
        signed_transaction = account.sign_transaction(transaction)
        tx_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)

    else:
        _set_from_address(web3, transaction_options)
        tx_hash = web3.eth.sendTransaction(transaction_options)

    return tx_hash


def wait_for_successful_transaction(
    *, web3: Web3, transaction_options: TxParams, private_key=None
):
    """
    Send the transaction with given transaction options
    Will either use an account of the node(default), or a local private key(if given) to sign the transaction.
    It will block until the transaction was successfully mined.

    Returns: The transaction receipt
    """

    tx_hash = send_transaction(
        web3=web3, transaction_options=transaction_options, private_key=private_key
    )
    return wait_for_successful_transaction_receipt(web3=web3, txid=tx_hash)


def send_function_call_transaction(
    function_call, *, web3: Web3, transaction_options: Dict = None, private_key=None
):
    """
    Creates, signs and sends a transaction from a function call (for example created with `contract.functions.foo()`.
    Will either use an account of the node(default), or a local private key(if given) to sign the transaction.
    It will not block until tx is sent

    Returns: The transaction hash
    """
    if transaction_options is None:
        transaction_options = {}

    if private_key is not None:
        signed_transaction = _build_and_sign_transaction(
            function_call,
            web3=web3,
            transaction_options=transaction_options,
            private_key=private_key,
        )
        tx_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)

    else:
        _set_from_address(web3, transaction_options)
        fill_nonce(web3, transaction_options)
        tx_hash = function_call.transact(transaction_options)

    return tx_hash


def wait_for_successful_function_call(
    function_call, *, web3: Web3, transaction_options: Dict = None, private_key=None
):
    """
    Creates, signs and sends a transaction from a function call (for example created with `contract.functions.foo()`.
    Will either use an account of the node(default), or a local private key(if given) to sign the transaction.
    It will block until the transaction was successfully mined.

    Returns: The transaction receipt
    """
    tx_hash = send_function_call_transaction(
        function_call,
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )
    return wait_for_successful_transaction_receipt(web3, tx_hash)


def wait_for_successful_transaction_receipts(
    web3, tx_hashs: Iterable[HexBytes], timeout=300
):

    failed_tx_hashs = set()

    for tx_hash in tx_hashs:
        receipt = web3.eth.waitForTransactionReceipt(tx_hash, timeout=timeout)
        status = receipt.get("status", None)
        if status == 0:
            failed_tx_hashs.add(tx_hash)
        elif status == 1:
            continue
        else:
            raise ValueError(
                f"Unexpected value for status in the transaction receipt: {status}"
            )

    if len(failed_tx_hashs) != 0:
        raise TransactionsFailed(failed_tx_hashs)


def wait_for_successful_transaction_receipt(
    web3: Web3, txid: HexBytes, timeout=180
) -> TxReceipt:
    """See if transaction went through (Solidity code did not throw).
    :return: Transaction receipt
    """
    receipt = web3.eth.waitForTransactionReceipt(txid, timeout=timeout)
    status = receipt.get("status", None)
    if status == 0:
        raise TransactionFailed
    elif status == 1:
        return receipt
    else:
        raise ValueError(
            f"Unexpected value for status in the transaction receipt: {status}"
        )


def _build_and_sign_transaction(
    function_call, *, web3, transaction_options, private_key
):
    account = Account.from_key(private_key)

    if "from" in transaction_options and transaction_options["from"] != account.address:
        raise ValueError(
            "From can not be set in transaction_options if a private key is used"
        )
    transaction_options["from"] = account.address

    transaction = fill_nonce(web3, function_call.buildTransaction(transaction_options))

    return account.sign_transaction(transaction)


def build_transaction_options(*, gas, gas_price, nonce, value=None):

    transaction_options = {}

    if gas is not None:
        transaction_options["gas"] = gas
    if gas_price is not None:
        transaction_options["gasPrice"] = gas_price
    if nonce is not None:
        transaction_options["nonce"] = nonce
    if value is not None:
        transaction_options["value"] = value

    return transaction_options


def fill_nonce(web3, transaction_options):
    if "from" in transaction_options and "nonce" not in transaction_options:
        transaction_options["nonce"] = web3.eth.getTransactionCount(
            transaction_options["from"], block_identifier="pending"
        )
    return transaction_options


def _set_from_address(web3, transaction_options):
    """set the from address in the transaction options

    transact() will not fill the from field by asking the node
    we need to do that ourselves
    """
    if "from" not in transaction_options:
        transaction_options["from"] = web3.eth.defaultAccount or web3.eth.accounts[0]


def increase_transaction_options_nonce(transaction_options: Dict) -> None:
    """Increases the nonce inside of `transaction_options` by 1 if present.
    If there is no nonce in `transaction_options`, this function will not do anything
    """
    if "nonce" in transaction_options:
        transaction_options["nonce"] = transaction_options["nonce"] + 1
