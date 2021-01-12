import pytest
from eth_utils import is_address

from deploy_tools.compile import compile_project
from deploy_tools.deploy import deploy_compiled_contract
from deploy_tools.plugin import get_contracts_folder


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
