import json
import re
from os import path
from pathlib import Path
from typing import Optional, Sequence

import click
from eth_utils import encode_hex
from web3 import Account, EthereumTesterProvider, Web3
from web3._utils.abi import get_abi_input_types, get_constructor_abi

from .compile import (
    DEFAULT_EVM_VERSION,
    UnknownContractException,
    build_initcode,
    compile_project,
    filter_contracts,
)
from .deploy import decrypt_private_key, deploy_compiled_contract
from .files import (
    InvalidAddressException,
    ensure_path_for_file_exists,
    load_json_asset,
    validate_and_format_address,
    write_minified_json_asset,
    write_pretty_json_asset,
)
from .transact import (
    build_transaction_options,
    wait_for_successful_function_call,
    wait_for_successful_transaction,
)

# we need test_provider and test_json_rpc for running the tests in test_cli
# they need to persist between multiple calls to runner.invoke and are
# therefore initialized on the module level.
test_provider = EthereumTesterProvider()
test_json_rpc = Web3(test_provider)

CONTRACTS_DIR_DEFAULT = "contracts"
KEYSTORE_FILE_SAVE_DEFAULT = "keystore.json"


def validate_address(ctx, param, value):
    try:
        return validate_and_format_address(value)
    except InvalidAddressException as e:
        raise click.BadParameter(
            f"The address parameter is not recognized to be an address: {value}"
        ) from e


jsonrpc_option = click.option(
    "--jsonrpc",
    help="JsonRPC URL of the ethereum client",
    default="http://127.0.0.1:8545",
    show_default=True,
    metavar="URL",
    envvar="JSONRPC",
)
keystore_option = click.option(
    "--keystore",
    help="Path to the encrypted keystore",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    envvar="KEYSTORE",
)
gas_option = click.option(
    "--gas",
    help="Gas of the transaction to be sent",
    type=int,
    default=None,
    envvar="GAS",
)
gas_price_option = click.option(
    "--gas-price",
    help="Gas price of the transaction to be sent",
    type=int,
    default=None,
    envvar="GAS_PRICE",
)
nonce_option = click.option(
    "--nonce", help="Nonce of the first transaction to be sent", type=int, default=None
)
auto_nonce_option = click.option(
    "--auto-nonce",
    help="automatically determine the nonce of first transaction to be sent",
    default=False,
    is_flag=True,
    envvar="AUTO_NONCE",
)
contracts_dir_option = click.option(
    "--contracts-dir",
    "-d",
    help=f"Directory of the contracts sources [default: {CONTRACTS_DIR_DEFAULT}]",
    type=click.Path(file_okay=False, exists=True),
    envvar="CONTRACTS_DIR",
)
optimize_option = click.option(
    "--optimize/--no-optimize",
    default=True,
    show_default=True,
    help="Toggles the solidity optimizer",
    envvar="OPTIMIZE",
)
optimize_runs_option = click.option(
    "--optimize-runs",
    default=500,
    type=int,
    show_default=True,
    help="Number of contract runs to optimize for when compiling contracts",
    envvar="OPTIMIZE_RUNS",
)
evm_version_option = click.option(
    "--evm-version",
    type=str,
    help="The evm target version, one of: "
    "petersburg, constantinople, byzantium, spuriousDragon, tangerineWhistle, or homestead",
    default=DEFAULT_EVM_VERSION,
    show_default=True,
    envvar="EVM_VERSION",
)
compiled_contracts_path_option = click.option(
    "--compiled-contracts",
    "compiled_contracts_path",
    help="Path to the compiled contracts json file",
    type=click.Path(file_okay=True, exists=True),
    envvar="COMPILED_CONTRACTS",
)
contract_address_option = click.option(
    "--contract-address",
    help="The address of the deployed contract, '0x' prefixed string",
    type=str,
    required=True,
    callback=validate_address,
)
keystore_file_save_option = click.option(
    "--keystore-path",
    help="Path where to store the keystore file",
    type=click.Path(resolve_path=True),
    default=KEYSTORE_FILE_SAVE_DEFAULT,
    show_default=True,
)
private_key_option = click.option(
    "--private-key",
    help="Private key in hex string representation",
    type=str,
    default=None,
)
value_option = click.option(
    "--value",
    help="Value parameter for a transaction as the amount of Wei to send with",
    type=int,
    default=None,
)


@click.group()
def main():
    pass


@main.command(short_help="Compile all contracts")
@contracts_dir_option
@optimize_option
@optimize_runs_option
@evm_version_option
@click.option(
    "--only-abi",
    default=False,
    help="Only include the abi of the contracts",
    is_flag=True,
)
@click.option(
    "--minimize",
    default=False,
    help="Minimizes the output file by removing unnecessary whitespaces",
    is_flag=True,
)
@click.option(
    "--contract-names",
    default=None,
    help="Comma separated list of contract names to include in the output, default is to include all contracts",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True, exists=False),
    help="Name of the output file",
    show_default=True,
    default="build/contracts.json",
)
def compile(
    contracts_dir,
    optimize,
    optimize_runs,
    evm_version,
    only_abi,
    minimize,
    contract_names,
    output,
):
    if contract_names is not None:
        contract_names = contract_names.split(",")

    ensure_path_for_file_exists(output)

    if contracts_dir is None:
        contracts_dir = CONTRACTS_DIR_DEFAULT
    verify_contracts_dir_exists(contracts_dir)

    try:
        compiled_contracts = filter_contracts(
            contract_names,
            compile_project(
                contracts_dir,
                optimize=optimize,
                optimize_runs=optimize_runs,
                only_abi=only_abi,
                evm_version=evm_version,
            ),
        )
    except UnknownContractException as e:
        raise click.BadOptionUsage(
            "contract-names", f"Could not find contract: {e.args[0]}"
        )
    if minimize:
        write_minified_json_asset(compiled_contracts, output)
    else:
        write_pretty_json_asset(compiled_contracts, output)


@main.command(short_help="Deploys a contract")
@click.argument("contract-name", type=str)
@click.argument("args", nargs=-1, type=str)
@gas_option
@gas_price_option
@nonce_option
@auto_nonce_option
@keystore_option
@jsonrpc_option
@contracts_dir_option
@optimize_option
@evm_version_option
@compiled_contracts_path_option
def deploy(
    contract_name: str,
    args: Sequence[str],
    gas: int,
    gas_price: int,
    nonce: int,
    auto_nonce: bool,
    keystore: str,
    jsonrpc: str,
    contracts_dir,
    optimize,
    evm_version,
    compiled_contracts_path: str,
):
    """
    Deploys a contract

    Deploys a contract with the name CONTRACT_NAME and the constructor arguments ARGS.
    If the constructor takes array as arguments, they should be provided without brackets separated by commas.
    For example int[] could be 123,456,789
    """
    web3 = connect_to_json_rpc(jsonrpc)
    private_key = retrieve_private_key(keystore)

    nonce = get_nonce(
        web3=web3, nonce=nonce, auto_nonce=auto_nonce, private_key=private_key
    )
    transaction_options = build_transaction_options(
        gas=gas, gas_price=gas_price, nonce=nonce
    )

    compiled_contracts = get_compiled_contracts(
        contracts_dir=contracts_dir,
        optimize=optimize,
        evm_version=evm_version,
        compiled_contracts_path=compiled_contracts_path,
    )

    if contract_name not in compiled_contracts:
        raise click.BadArgumentUsage(f"Contract {contract_name} was not found.")

    abi = compiled_contracts[contract_name]["abi"]
    bytecode = compiled_contracts[contract_name]["bytecode"]

    contract = deploy_compiled_contract(
        abi=abi,
        bytecode=bytecode,
        constructor_args=parse_args_to_matching_types_for_constructor(args, abi),
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )

    click.echo(contract.address)


@main.command(
    short_help="Gives the initcode for a contract, could be used for inclusion in a chain spec as a pre-compile"
)
@click.argument("contract-name", type=str)
@click.argument("args", nargs=-1, type=str)
@contracts_dir_option
@optimize_option
@evm_version_option
@compiled_contracts_path_option
def initcode(
    contract_name: str,
    args: Sequence[str],
    contracts_dir,
    optimize,
    evm_version,
    compiled_contracts_path: str,
):
    """
    Does not deploy a contract but returns the initcode that should be included in the chain spec to have the contract
    as a pre-compiled contract.

    Returns the initcode of a contract with the name CONTRACT_NAME and the constructor arguments ARGS.
    If the constructor takes array as arguments, they should be provided without brackets separated by commas.
    For example int[] could be 123,456,789
    """

    compiled_contracts = get_compiled_contracts(
        contracts_dir=contracts_dir,
        optimize=optimize,
        evm_version=evm_version,
        compiled_contracts_path=compiled_contracts_path,
    )

    if contract_name not in compiled_contracts:
        raise click.BadArgumentUsage(f"Contract {contract_name} was not found.")

    abi = compiled_contracts[contract_name]["abi"]
    bytecode = compiled_contracts[contract_name]["bytecode"]

    arguments = parse_args_to_matching_types_for_constructor(args, abi)
    initcode = build_initcode(
        contract_abi=abi, contract_bytecode=bytecode, constructor_args=arguments
    )

    click.echo(initcode)


@main.command(short_help="Sends a transaction to a contract function")
@click.argument("contract-name", type=str)
@click.argument("function-name", type=str)
@click.argument("args", nargs=-1, type=str)
@gas_option
@gas_price_option
@nonce_option
@auto_nonce_option
@keystore_option
@jsonrpc_option
@contracts_dir_option
@compiled_contracts_path_option
@contract_address_option
@value_option
def transact(
    contract_name: str,
    function_name: str,
    args: Sequence[str],
    gas: int,
    gas_price: int,
    nonce: int,
    auto_nonce: bool,
    keystore: str,
    jsonrpc: str,
    contracts_dir,
    compiled_contracts_path,
    contract_address,
    value: Optional[int],
):
    """
    Send a transaction to a contract CONTRACT_NAME calling function FUNCTION_NAME with arguments ARGS.

    If the function takes array as arguments, they should be provided without brackets separated by commas.
    For example int[] could be 123,456,789
    """
    web3 = connect_to_json_rpc(jsonrpc)
    private_key = retrieve_private_key(keystore)

    nonce = get_nonce(
        web3=web3, nonce=nonce, auto_nonce=auto_nonce, private_key=private_key
    )
    transaction_options = build_transaction_options(
        gas=gas, gas_price=gas_price, nonce=nonce, value=value
    )

    compiled_contracts = get_compiled_contracts(
        contracts_dir=contracts_dir, compiled_contracts_path=compiled_contracts_path
    )

    if contract_name not in compiled_contracts:
        raise click.BadArgumentUsage(f"Contract {contract_name} was not found.")

    contract_abi = compiled_contracts[contract_name]["abi"]
    contract = web3.eth.contract(abi=contract_abi, address=contract_address)
    function_abi = get_contract_matching_function(contract_abi, function_name, args)
    parsed_arguments = parse_args_to_matching_types_for_function(args, function_abi)
    function_call = contract.functions[function_name](*parsed_arguments)

    receipt = wait_for_successful_function_call(
        function_call,
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )

    click.echo(encode_hex(receipt.transactionHash))


@main.command(short_help="Calls a contract function.")
@click.argument("contract-name", type=str)
@click.argument("function-name", type=str)
@click.argument("args", nargs=-1, type=str)
@jsonrpc_option
@contracts_dir_option
@compiled_contracts_path_option
@contract_address_option
def call(
    contract_name: str,
    function_name: str,
    args: Sequence[str],
    jsonrpc: str,
    contracts_dir,
    contract_address,
    compiled_contracts_path,
):
    """
    Calls to a contract CONTRACT_NAME calling function FUNCTION_NAME with arguments ARGS.

    If the function takes array as arguments, they should be provided without brackets separated by commas.
    For example int[] could be 123,456,789
    """
    web3 = connect_to_json_rpc(jsonrpc)

    compiled_contracts = get_compiled_contracts(
        contracts_dir=contracts_dir, compiled_contracts_path=compiled_contracts_path
    )

    if contract_name not in compiled_contracts:
        raise click.BadArgumentUsage(f"Contract {contract_name} was not found.")

    contract_abi = compiled_contracts[contract_name]["abi"]
    contract = web3.eth.contract(abi=contract_abi, address=contract_address)
    function_abi = get_contract_matching_function(contract_abi, function_name, args)
    parsed_arguments = parse_args_to_matching_types_for_function(args, function_abi)
    result = contract.functions[function_name](*parsed_arguments).call()

    click.echo(result)


@main.command(
    short_help="Generates an encrypted keystore file. Creates a new account if no private key is provided."
)
@keystore_file_save_option
@private_key_option
def generate_keystore(keystore_path: str, private_key: str):
    if path.exists(keystore_path):
        raise click.BadOptionUsage(  # type: ignore
            "--keystore-file", f"The file {keystore_path} does already exist!"
        )

    if private_key:
        account = Account.from_key(private_key)
    else:
        account = Account.create()

    password = click.prompt(
        "Please enter the password to encrypt the keystore",
        type=str,
        hide_input=True,
        confirmation_prompt=True,
    )
    keystore = account.encrypt(password=password)

    with open(keystore_path, "w") as file:
        file.write(json.dumps(keystore))
        file.close()

    click.echo(f"Stored keystore for {account.address} at {keystore_path}")


@main.command(short_help="Send ether to the given address.")
@click.argument("value", type=int)
@click.argument("address", type=str)
@jsonrpc_option
@gas_option
@gas_price_option
@nonce_option
@auto_nonce_option
@keystore_option
def send_eth(
    gas: int,
    gas_price: int,
    nonce: int,
    auto_nonce: bool,
    keystore: str,
    jsonrpc: str,
    address: str,
    value: int,
):
    """
    Send a transaction with VALUE wei to address ADDRESS
    """
    web3 = connect_to_json_rpc(jsonrpc)
    private_key = retrieve_private_key(keystore)

    nonce = get_nonce(
        web3=web3, nonce=nonce, auto_nonce=auto_nonce, private_key=private_key
    )
    transaction_options = build_transaction_options(
        gas=gas, gas_price=gas_price, nonce=nonce, value=value
    )

    transaction_options["to"] = address

    receipt = wait_for_successful_transaction(
        web3=web3, transaction_options=transaction_options, private_key=private_key
    )

    click.echo(encode_hex(receipt["transactionHash"]))


def get_compiled_contracts(
    *,
    contracts_dir,
    optimize=False,
    evm_version=DEFAULT_EVM_VERSION,
    compiled_contracts_path,
):
    if contracts_dir is not None and compiled_contracts_path is not None:
        raise click.BadOptionUsage(
            "--contracts-dir, --compiled-contracts",
            "Both --contracts-dir and --compiled-contracts were specified. Please only use one of the two.",
        )
    if compiled_contracts_path is not None:
        return load_json_asset(compiled_contracts_path)
    else:
        if contracts_dir is None:
            contracts_dir = CONTRACTS_DIR_DEFAULT
        verify_contracts_dir_exists(contracts_dir)
        return compile_project(
            contracts_dir, optimize=optimize, evm_version=evm_version
        )


def verify_contracts_dir_exists(contracts_dir):
    if not Path(contracts_dir).is_dir():
        raise click.BadOptionUsage(
            "--contracts-dir", f'Contract directory not found: "{contracts_dir}"'
        )


def connect_to_json_rpc(jsonrpc) -> Web3:
    if jsonrpc == "test":
        web3 = test_json_rpc
    else:
        web3 = Web3(Web3.HTTPProvider(jsonrpc, request_kwargs={"timeout": 180}))
    return web3


def retrieve_private_key(keystore_path):
    """
    return the private key corresponding to keystore or none if keystore is none
    """

    private_key = None

    if keystore_path is not None:
        password = click.prompt(
            "Please enter the password to decrypt the keystore",
            type=str,
            hide_input=True,
            default="",  # allow empty password
        )
        private_key = decrypt_private_key(keystore_path, password)

    return private_key


def get_nonce(*, web3: Web3, nonce: int, auto_nonce: bool, private_key: bytes):
    """get the nonce to be used as specified via command line options

     we do some option checking in this function. It would be better to do this
     before doing any real work, but we would need another function then.
    """
    if auto_nonce and not private_key:
        raise click.UsageError("--auto-nonce requires --keystore argument")
    if nonce is not None and auto_nonce:
        raise click.UsageError(
            "--nonce and --auto-nonce cannot be used at the same time"
        )

    if auto_nonce:
        return web3.eth.getTransactionCount(
            Account.from_key(private_key).address, block_identifier="pending"
        )
    else:
        return nonce


def get_contract_matching_function(contract_abi, function_name, args):
    candidates = [
        abi
        for abi in contract_abi
        if abi["type"] == "function"
        and abi["name"] == function_name
        and len(abi["inputs"]) == len(args)
    ]

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        raise ValueError("Found no function matching the name and input length.")
    elif len(candidates) > 1:
        raise ValueError("Found multiple function matching name and input length.")


def parse_args_to_matching_types_for_constructor(args, contract_abi):
    """Parses a list of commandline arguments to the abi matching python types"""
    constructor_abi = get_constructor_abi(contract_abi)
    if constructor_abi:
        return parse_args_to_matching_types_for_function(args, constructor_abi)
    return []


def parse_args_to_matching_types_for_function(args, function_abi):
    types = get_abi_input_types(function_abi)
    return [parse_arg_to_matching_type(arg, type) for arg, type in zip(args, types)]


def parse_arg_to_matching_type(arg, type: str):
    int_pattern = "^u?int(\\d){0,3}$"
    int_array_pattern = "^u?int(\\d){0,3}\\[\\]$"
    bool_pattern = "^bool$"
    bool_array_pattern = "^bool\\[\\]$"
    address_pattern = "^address$"
    address_array_pattern = "^address\\[\\]$"
    bytes_pattern = "^bytes\\d{0,2}$"
    string_pattern = "^string$"
    """Parses a commandline argument to the abi matching python type"""
    if re.match(int_pattern, type):
        return int(arg)
    if re.match(int_array_pattern, type):
        return [int(_arg) for _arg in arg.split(",")]
    if re.match(bool_pattern, type):
        if arg.lower() == "true":
            return True
        if arg.lower() == "false":
            return False
        raise ValueError(f"Expected true or false, but got {arg}")
    if re.match(bool_array_pattern, type):
        return [parse_arg_to_matching_type(_arg, "bool") for _arg in arg.split(",")]
    if re.match(address_pattern, type):
        return Web3.toChecksumAddress(arg)
    if re.match(address_array_pattern, type):
        return [Web3.toChecksumAddress(_arg) for _arg in arg.split(",")]
    if re.match(bytes_pattern, type) or re.match(string_pattern, type):
        return arg
    raise ValueError(f"Cannot handle parameter of type {type} yet.")
