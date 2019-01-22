"""Pytest plugins"""
from pathlib import Path

import pytest
import eth_tester
from web3.contract import Contract
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider


from deploy_tools import compile_project, deploy_compiled_contract


CONTRACTS_FOLDER_OPTION = "--contracts-dir"
CONTRACTS_FOLDER_OPTION_HELP = "Folder which contains the project smart contracts"


def pytest_addoption(parser):
    parser.addoption(CONTRACTS_FOLDER_OPTION, help=CONTRACTS_FOLDER_OPTION_HELP)
    parser.addini(CONTRACTS_FOLDER_OPTION, CONTRACTS_FOLDER_OPTION_HELP)


def get_contracts_folder(pytestconfig):
    if pytestconfig.getoption(CONTRACTS_FOLDER_OPTION, default=None):
        return pytestconfig.getoption(CONTRACTS_FOLDER_OPTION)
    return Path(pytestconfig.rootdir) / 'contracts'


@pytest.fixture(scope='session')
def contract_assets(pytestconfig):
    """
    Returns the compilation assets (dict containing the content of `contracts.json`) of all compiled contracts
    To change the directory of the contracts use the pytest option --contracts-dir
    """
    contracts_path = get_contracts_folder(pytestconfig)
    return compile_project(contracts_path=contracts_path, optimize=True)


@pytest.fixture(scope='session')
def deploy_contract(web3, contract_assets):
    """Fixture to deploy a contract on the current chain

       Usage: `deploy_contract('contract_identifier', constructor_args=(1,2,3))`
    """

    def deploy_contract_function(contract_identifier: str, *, constructor_args=()) -> Contract:
        return deploy_compiled_contract(
            abi=contract_assets[contract_identifier]['abi'],
            bytecode=contract_assets[contract_identifier]['bytecode'],
            web3=web3,
            constructor_args=constructor_args
        )

    return deploy_contract_function


@pytest.fixture(scope='session')
def chain():
    """
    The running ethereum tester chain
    """
    return eth_tester.EthereumTester(eth_tester.PyEVMBackend())


@pytest.fixture(scope='session')
def web3(chain):
    """
    Web3 object connected to the ethereum tester chain
    """
    return Web3(EthereumTesterProvider(chain))


@pytest.fixture(scope='session', autouse=True)
def set_default_account(web3):
    """Sets the web3 default account to the first account of `accounts`"""
    web3.eth.defaultAccount = web3.eth.accounts[0]


@pytest.fixture(scope='session')
def default_account(web3):
    """Returns the default account which is used to deploy contracts"""
    return web3.eth.defaultAccount


@pytest.fixture(scope='session')
def accounts(web3):
    """
    Some ethereum accounts on the test chain with some ETH
    """
    return web3.eth.accounts


@pytest.fixture(scope='session')
def account_keys(chain):
    """
    The private keys that correspond to the accounts of the `accounts` fixture
    """
    return chain.backend.account_keys


@pytest.fixture(autouse=True)
def chain_cleanup(chain):
    """Cleans up the state of the test chain after each test"""
    snapshot = chain.take_snapshot()
    yield
    chain.revert_to_snapshot(snapshot)
