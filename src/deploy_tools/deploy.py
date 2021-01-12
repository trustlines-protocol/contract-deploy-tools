import json
from typing import Dict

import pkg_resources
from eth_keyfile import extract_key_from_keyfile
from web3 import Web3
from web3.contract import Contract

from deploy_tools.transact import wait_for_successful_function_call


def deploy_compiled_contract(
    *,
    abi,
    bytecode,
    web3: Web3,
    constructor_args=(),
    transaction_options: Dict = None,
    private_key=None,
) -> Contract:
    """
    Deploys a compiled contract either using an account of the node, or a local private key
    It will block until the transaction was successfully mined.

    Returns: The deployed contract as a web3 contract

    """
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    constuctor_call = contract.constructor(*constructor_args)

    receipt = wait_for_successful_function_call(
        constuctor_call,
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )

    address = receipt["contractAddress"]
    return contract(address)


def load_contracts_json(package_name, filename="contracts.json") -> Dict:
    resource_package = package_name
    json_string = pkg_resources.resource_string(resource_package, filename)
    return json.loads(json_string)


def decrypt_private_key(keystore_path: str, password: str) -> bytes:
    return extract_key_from_keyfile(keystore_path, password.encode("utf-8"))
