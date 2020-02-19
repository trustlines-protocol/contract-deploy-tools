import eth_utils
import pytest
from eth_utils import is_address

from deploy_tools.compile import compile_project
from deploy_tools.deploy import (
    TransactionFailed,
    deploy_compiled_contract,
    send_function_call_transaction,
    send_transaction,
)
from deploy_tools.plugin import get_contracts_folder


@pytest.fixture()
def test_contract(deploy_contract):
    return deploy_contract("TestContract", constructor_args=(4,))


@pytest.fixture()
def contract_assets_st_petersburg(pytestconfig):
    contracts_path = get_contracts_folder(pytestconfig)
    evm_version = "petersburg"
    return compile_project(
        contracts_path=contracts_path, optimize=True, evm_version=evm_version
    )


def test_deploy_from_private_key(web3, contract_assets, account_keys):
    contract_interface = contract_assets["TestContract"]
    contract = deploy_compiled_contract(
        abi=contract_interface["abi"],
        bytecode=contract_interface["bytecode"],
        web3=web3,
        constructor_args=(1,),
        private_key=account_keys[1],
    )

    assert is_address(contract.address)


def test_deploy(web3, contract_assets):
    contract_interface = contract_assets["TestContract"]
    contract = deploy_compiled_contract(
        abi=contract_interface["abi"],
        bytecode=contract_interface["bytecode"],
        web3=web3,
        constructor_args=(1,),
    )

    assert is_address(contract.address)


def test_deploy_st_petersburg(web3, contract_assets_st_petersburg):
    contract_interface = contract_assets_st_petersburg["TestContract"]
    contract = deploy_compiled_contract(
        abi=contract_interface["abi"],
        bytecode=contract_interface["bytecode"],
        web3=web3,
        constructor_args=(1,),
    )

    assert is_address(contract.address)


def test_send_contract_call(test_contract, web3):

    function_call = test_contract.functions.set(200)

    receipt = send_function_call_transaction(function_call, web3=web3)

    assert receipt["status"]
    assert test_contract.functions.state().call() == 200


def test_send_contract_call_from_private_key(test_contract, web3, account_keys):

    function_call = test_contract.functions.set(200)

    receipt = send_function_call_transaction(
        function_call, web3=web3, private_key=account_keys[2]
    )

    assert receipt["status"]
    assert test_contract.functions.state().call() == 200


def test_send_contract_call_with_transaction_options(test_contract, web3, account_keys):

    function_call = test_contract.functions.set(200)

    transaction_options = {"gas": 199999, "gasPrice": 99}

    receipt = send_function_call_transaction(
        function_call,
        web3=web3,
        transaction_options=transaction_options,
        private_key=account_keys[2],
    )

    transaction = web3.eth.getTransaction(receipt.transactionHash)

    for key, value in transaction_options.items():
        assert transaction[key] == value


def test_send_contract_call_set_nonce(test_contract, web3, account_keys):

    function_call = test_contract.functions.set(200)
    nonce = 1  # right nonce should be 0

    # This should just test, that the nonce is set
    # Apparently eth_tester raises a validation error if the nonce to high
    with pytest.raises(eth_utils.ValidationError):
        send_function_call_transaction(
            function_call,
            transaction_options={"nonce": nonce},
            web3=web3,
            private_key=account_keys[2],
        )


def test_wait_for_successful_tx_receipt(test_contract, web3, account_keys):
    """
    Test that `wait_for_successful_tx_receipt` will catch that this transaction fails and raise an error
    """
    function_call = test_contract.functions.failingFunction()

    with pytest.raises(TransactionFailed):
        # We have to assign gas to make sure eth_tester will not check for transaction success
        # and leave this job to deploy_tool
        send_function_call_transaction(
            function_call,
            transaction_options={"gas": 123456},
            web3=web3,
            private_key=account_keys[2],
        )


@pytest.mark.parametrize("use_private_key", [True, False])
def test_send_eth_default_account(web3, accounts, account_keys, use_private_key):
    pre_balance_0 = web3.eth.getBalance(accounts[0])
    pre_balance_1 = web3.eth.getBalance(accounts[1])
    value = 123
    transaction_option = {"value": value, "to": accounts[1], "gasPrice": 0}
    send_transaction(
        web3=web3,
        transaction_options=transaction_option,
        private_key=account_keys[0] if use_private_key else None,
    )

    post_balance_0 = web3.eth.getBalance(accounts[0])
    post_balance_1 = web3.eth.getBalance(accounts[1])

    assert post_balance_0 - pre_balance_0 == -value
    assert post_balance_1 - pre_balance_1 == value
