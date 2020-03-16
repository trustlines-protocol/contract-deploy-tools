from eth_utils import is_hex

from deploy_tools.compile import build_initcode


def test_build_initcode_no_constructor(contract_assets):
    contract_interface = contract_assets["OtherContract"]
    initcode = build_initcode(contract_bytecode=contract_interface["bytecode"])

    assert is_hex(initcode)


def test_build_initcode_with_constructor(contract_assets):
    contract_interface = contract_assets["TestContract"]
    initcode = build_initcode(
        contract_bytecode=contract_interface["bytecode"],
        contract_abi=contract_interface["abi"],
        constructor_args=[123456],
    )

    assert is_hex(initcode)
