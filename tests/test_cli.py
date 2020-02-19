import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner
from eth_keyfile import create_keyfile_json
from eth_utils import is_0x_prefixed, is_address, is_hex
from eth_utils.exceptions import ValidationError

from deploy_tools.cli import main, parse_arg_to_matching_type


@pytest.fixture()
def keystores(tmp_path, account_keys, key_password):
    """paths to keystore files"""
    paths = []
    for i, private_key in enumerate(account_keys[:2]):
        file_path = tmp_path / f"keyfile-{i}.json"
        file_path.write_text(
            json.dumps(
                create_keyfile_json(
                    private_key.to_bytes(), key_password.encode("utf-8")
                )
            )
        )
        paths.append(file_path)

    return paths


@pytest.fixture()
def test_contract_name():
    return "TestContract"


@pytest.fixture()
def test_contract_address(runner, test_contract_name):
    result = runner.invoke(
        main, f"deploy {test_contract_name} -d testcontracts --jsonrpc test 4"
    )
    assert result.exit_code == 0
    contract_address = result.output[:-1]
    assert is_address(contract_address)
    return contract_address


@pytest.fixture()
def output_file(tmp_path):
    return tmp_path / "test.json"


@pytest.fixture()
def keystore_file_path(tmp_path, keystores, key_password):
    """path to keystore of account[1]"""
    return keystores[1]


@pytest.fixture()
def key_password():
    """password used for the keystores"""
    return "test_password"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def go_to_root_dir():
    current_path = os.getcwd()
    os.chdir(Path(__file__).parent.parent)
    yield
    os.chdir(current_path)


@pytest.fixture()
def compiled_contracts_path(go_to_root_dir, runner):
    compiled_contracts_path = "build/contracts.json"
    result = runner.invoke(
        main, f"compile -d testcontracts -o {compiled_contracts_path}"
    )
    assert result.exit_code == 0

    with open(compiled_contracts_path) as f:
        contract_assets = json.load(f)
        assert "TestContract" in contract_assets

    return compiled_contracts_path


@pytest.fixture()
def keystore_file_save_path(tmpdir):
    return tmpdir.join("test_keystore.json")


@pytest.fixture()
def private_key(account_keys):
    return account_keys[0]


@pytest.mark.usefixtures("go_to_root_dir")
def test_default_compile(runner):
    result = runner.invoke(main, "compile -d testcontracts")
    assert result.exit_code == 0

    with open("build/contracts.json") as f:
        contract_assets = json.load(f)
        assert "TestContract" in contract_assets


@pytest.mark.usefixtures("go_to_root_dir")
def test_minimize_compile(runner):
    result = runner.invoke(main, "compile -d testcontracts --minimize")
    assert result.exit_code == 0

    with open("build/contracts.json") as f:
        contract_assets = json.load(f)
        assert "TestContract" in contract_assets


@pytest.mark.usefixtures("go_to_root_dir")
def test_contract_names_compile(runner):
    result = runner.invoke(
        main, "compile -d testcontracts --contract-names OtherContract"
    )
    assert result.exit_code == 0

    with open("build/contracts.json") as f:
        contract_assets = json.load(f)
        assert "TestContract" not in contract_assets
        assert "OtherContract" in contract_assets


@pytest.mark.usefixtures("go_to_root_dir")
def test_contract_output_file(runner, output_file):
    result = runner.invoke(main, f"compile -d testcontracts -o {output_file}")
    assert result.exit_code == 0

    with output_file.open() as f:
        contract_assets = json.load(f)
        assert "TestContract" in contract_assets


@pytest.mark.usefixtures("go_to_root_dir")
def test_unknown_contract_names_compile(runner):
    result = runner.invoke(
        main, "compile -d testcontracts --contract-names TestContracto"
    )
    assert result.exit_code == 2


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_simple_contract(runner):
    result = runner.invoke(main, "deploy OtherContract -d testcontracts --jsonrpc test")
    assert result.exit_code == 0
    assert is_address(result.output[:-1])


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_no_contracts_directory(runner):
    result = runner.invoke(main, "deploy OtherContract --jsonrpc test")
    assert result.exit_code == 2
    assert 'Contract directory not found: "contracts"' in result.output[:-1]


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_contracts_dir_and_compiled_contracts(runner, compiled_contracts_path):
    result = runner.invoke(
        main,
        f"deploy OtherContract -d testcontracts --compiled-contracts"
        f" {compiled_contracts_path} --jsonrpc test",
    )
    assert result.exit_code == 2
    assert (
        "Both --contracts-dir and --compiled-contracts were specified. Please only use one of the two"
        in result.output[:-1]
    )


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_simple_contract_from_compiled_contracts(
    runner, compiled_contracts_path
):
    result = runner.invoke(
        main,
        f"deploy OtherContract --compiled-contracts {compiled_contracts_path} --jsonrpc test",
    )
    assert result.exit_code == 0
    assert is_address(result.output[:-1])


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_contract_with_arguments(runner):
    result = runner.invoke(
        main,
        "deploy -d testcontracts --jsonrpc test -- ManyArgumentsContract "
        + "0 -1 -2 true 0x00D6Cc1BA9cf89BD2e58009741f4F7325BAdc0ED 0x00",
    )
    assert result.exit_code == 0
    assert is_address(result.output[:-1])


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_transaction_parameters(runner):
    result = runner.invoke(
        main,
        "deploy OtherContract -d testcontracts --jsonrpc test "
        + "--gas 200000 --gas-price 20 --nonce 0",
    )
    assert result.exit_code == 0
    assert is_address(result.output[:-1])


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_transaction_parameters_wrong_gas(runner):
    result = runner.invoke(
        main,
        "deploy OtherContract -d testcontracts --jsonrpc test "
        + "--gas 100 --gas-price 20 --nonce 0",
    )
    assert result.exit_code == 1


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_transaction_parameters_wrong_gas_price(runner):
    result = runner.invoke(
        main,
        "deploy OtherContract -d testcontracts --jsonrpc test "
        + "--gas 200000 --gas-price -1 --nonce 0",
    )
    assert result.exit_code == 1


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_keystore(runner, keystore_file_path, key_password):
    result = runner.invoke(
        main,
        f"deploy OtherContract -d testcontracts --jsonrpc test --keystore {keystore_file_path}",
        input=key_password,
    )
    assert result.exit_code == 0


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_keystore_wrong_nonce(runner, keystore_file_path, key_password):
    result = runner.invoke(
        main,
        f"deploy OtherContract -d testcontracts --jsonrpc test --nonce 100 --keystore {keystore_file_path}",
        input=key_password,
    )
    assert result.exit_code == 1


@pytest.mark.usefixtures("go_to_root_dir")
def test_initcode_simple_contract(runner):
    result = runner.invoke(main, f"initcode OtherContract -d testcontracts")
    print(result.output)
    assert result.exit_code == 0

    transaction_hash = result.output.splitlines()[-1]

    assert is_hex(transaction_hash)
    assert is_0x_prefixed(transaction_hash)


@pytest.mark.usefixtures("go_to_root_dir")
def test_initcode_with_constructor_argument(runner, key_password):
    result = runner.invoke(
        main, f"initcode TestContract 123456 -d testcontracts", input=key_password
    )
    assert result.exit_code == 0

    transaction_hash = result.output.splitlines()[-1]

    assert is_hex(transaction_hash)
    assert is_0x_prefixed(transaction_hash)


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_to_contract(
    runner, test_contract_address, test_contract_name
):
    result = runner.invoke(
        main,
        (
            f"transact -d testcontracts --jsonrpc test --contract-address {test_contract_address} "
            f"-- {test_contract_name} set 1"
        ),
    )

    assert result.exit_code == 0

    transaction_hash = result.output.splitlines()[-1]

    assert is_hex(transaction_hash)
    assert is_0x_prefixed(transaction_hash)


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_to_contract_from_compiled_contracts(
    runner, test_contract_address, test_contract_name, compiled_contracts_path
):
    result = runner.invoke(
        main,
        (
            f"transact --compiled-contracts {compiled_contracts_path} "
            f"--jsonrpc test --contract-address {test_contract_address} "
            f"-- {test_contract_name} set 1"
        ),
    )
    assert result.exit_code == 0

    transaction_hash = result.output.splitlines()[-1]

    assert is_hex(transaction_hash)
    assert is_0x_prefixed(transaction_hash)


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_with_value_parameter(
    runner, test_contract_address, test_contract_name
):
    # Change balance of a contract. Test the transaction value parameter by
    # a payable function on the test contract. Because of the setup with an
    # internal test RPC endpoint, it is not possible to directly check the
    # contracts balance. Therefore an additional contract function is provided
    # which can be called to retrieve the contracts balance.

    transaction_value = 1
    shared_command_string = (
        f"-d testcontracts --jsonrpc test --contract-address"
        f" {test_contract_address} -- {test_contract_name}"
    )

    result_initial_balance_call = runner.invoke(
        main, f"call {shared_command_string} getBalance"
    )
    assert result_initial_balance_call.exit_code == 0
    assert result_initial_balance_call.output.strip() == "0"

    result_pay_transaction = runner.invoke(
        main, f"transact --value {transaction_value} {shared_command_string} pay"
    )
    assert result_pay_transaction.exit_code == 0

    result_final_balance_call = runner.invoke(
        main, f"call {shared_command_string} getBalance"
    )
    assert result_final_balance_call.exit_code == 0
    assert result_final_balance_call.output.strip() == f"{transaction_value}"


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_to_contract_with_array_address_arguments(
    runner, compiled_contracts_path, test_contract_address, test_contract_name
):
    argument = f"{test_contract_address},{test_contract_address}"
    result = runner.invoke(
        main,
        (
            f"transact --compiled-contracts {compiled_contracts_path} "
            f"--jsonrpc test --contract-address {test_contract_address} "
            f"-- {test_contract_name} functionWithArrayArgument {argument}"
        ),
    )
    assert result.exit_code == 0

    transaction_hash = result.output.splitlines()[-1]

    assert is_hex(transaction_hash)
    assert is_0x_prefixed(transaction_hash)


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_to_contract_find_duplicated_function_by_argument_length(
    runner, test_contract_address, test_contract_name
):
    result = runner.invoke(
        main,
        (
            f"transact -d testcontracts --jsonrpc test --contract-address {test_contract_address} "
            f"-- {test_contract_name} duplicatedDifferentArgumentLength 1"
        ),
    )

    assert result.exit_code == 0

    transaction_hash = result.output.splitlines()[-1]

    assert is_hex(transaction_hash)
    assert is_0x_prefixed(transaction_hash)


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_to_contract_can_not_find_duplicated_function_same_argument_length(
    runner, test_contract_address, test_contract_name
):
    result = runner.invoke(
        main,
        (
            f"transact -d testcontracts --jsonrpc test --contract-address {test_contract_address} "
            f"-- {test_contract_name} duplicatedSameArgumentLength 1"
        ),
    )

    assert result.exit_code == 1
    assert type(result.exception) == ValueError


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_to_contract_non_existing_function(
    runner, test_contract_address, test_contract_name
):
    result = runner.invoke(
        main,
        (
            f"transact -d testcontracts --jsonrpc test --contract-address {test_contract_address} "
            f"-- {test_contract_name} unknown 1"
        ),
    )

    assert result.exit_code == 1
    assert type(result.exception) == ValueError


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_to_contract_wrong_address_format(runner, test_contract_name):
    result = runner.invoke(
        main,
        (
            f"transact -d testcontracts --jsonrpc test --contract-address "
            f"0x25D4760c08b4bf8e99c3658 -- {test_contract_name} set 1"
        ),
    )

    assert result.exit_code == 2


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_transaction_to_contract_insufficient_gas(
    runner, test_contract_address, test_contract_name
):
    result = runner.invoke(
        main,
        (
            f"transact -d testcontracts --jsonrpc test --contract-address {test_contract_address} "
            f"--gas 1 -- {test_contract_name} set 1"
        ),
    )

    assert result.exit_code == 1
    assert type(result.exception) == ValidationError


@pytest.mark.usefixtures("go_to_root_dir")
def test_call_contract_function(runner, test_contract_address, test_contract_name):
    result = runner.invoke(
        main,
        (
            f"call -d testcontracts --jsonrpc test --contract-address {test_contract_address} "
            f"-- {test_contract_name} state"
        ),
    )

    assert result.exit_code == 0
    assert result.output.strip() == "4"


@pytest.mark.usefixtures("go_to_root_dir")
def test_call_contract_function_from_compiled_contracts(
    runner, test_contract_address, test_contract_name, compiled_contracts_path
):
    result = runner.invoke(
        main,
        (
            f"call --compiled-contracts {compiled_contracts_path} --jsonrpc test"
            f" --contract-address {test_contract_address} "
            f"-- {test_contract_name} state"
        ),
    )

    assert result.exit_code == 0
    assert result.output.strip() == "4"


def test_generate_keystore_generate_new_private_key(
    runner, keystore_file_save_path, key_password
):
    assert not keystore_file_save_path.exists()

    result = runner.invoke(
        main,
        (f"generate-keystore --keystore-path {keystore_file_save_path}"),
        input=f"{key_password}\n{key_password}",
    )
    assert result.exit_code == 0
    assert keystore_file_save_path.exists()


def test_generate_keystore_fail_existing_file(
    runner, keystore_file_save_path, key_password
):
    keystore_file_save_path.ensure(File=True)

    assert keystore_file_save_path.exists()

    result = runner.invoke(
        main,
        (f"generate-keystore --keystore-path {keystore_file_save_path}"),
        input=f"{key_password}\n{key_password}",
    )
    assert result.exit_code == 2


def test_generate_keystore_from_private_key(
    runner, keystore_file_save_path, private_key, key_password
):
    result = runner.invoke(
        main,
        (
            f"generate-keystore --keystore-path {keystore_file_save_path} "
            f"--private-key {private_key.to_hex()}"
        ),
        input=f"{key_password}\n{key_password}",
    )

    assert result.exit_code == 0


@pytest.mark.parametrize(
    "arg, type, expected_return",
    [
        ("true", "bool", True),
        ("True", "bool", True),
        ("123456", "uint", 123456),
        ("123456", "int", 123456),
        ("8", "uint8", 8),
        ("8", "int8", 8),
        ("256", "uint16", 256),
        ("256", "int16", 256),
        ("123456", "uint256", 123456),
        ("123456", "int256", 123456),
        ("123456,123456", "uint[]", [123456, 123456]),
        ("123456,123456", "int[]", [123456, 123456]),
        ("8,8", "uint8[]", [8, 8]),
        ("8,8", "int8[]", [8, 8]),
        ("256,256", "uint16[]", [256, 256]),
        ("256,256", "int16[]", [256, 256]),
        ("123456,123456", "uint256[]", [123456, 123456]),
        ("123456,123456", "int256[]", [123456, 123456]),
        (
            "0xB9816fC57977D5A786E654c7CF76767be63b966e",
            "address",
            "0xB9816fC57977D5A786E654c7CF76767be63b966e",
        ),
        (
            "0xB9816fC57977D5A786E654c7CF76767be63b966e,0xB9816fC57977D5A786E654c7CF76767be63b966e",
            "address[]",
            [
                "0xB9816fC57977D5A786E654c7CF76767be63b966e",
                "0xB9816fC57977D5A786E654c7CF76767be63b966e",
            ],
        ),
        ("bobloblaw", "string", "bobloblaw"),
    ],
)
def test_parse_argument_to_matching_type(arg, type, expected_return):
    assert parse_arg_to_matching_type(arg, type) == expected_return


@pytest.mark.parametrize(
    "arg, type", [("bob1,bob2", "string[]"), ("[123,456],[123,456]", "int[][]")]
)
def test_parse_argument_not_supported_yet(arg, type):
    with pytest.raises(ValueError, match="Cannot handle parameter of type"):
        parse_arg_to_matching_type(arg, type)


@pytest.mark.usefixtures("go_to_root_dir")
def test_send_eth(runner, accounts):
    result = runner.invoke(main, (f"send-eth --jsonrpc test 123 {accounts[1]}"))

    assert result.exit_code == 0
