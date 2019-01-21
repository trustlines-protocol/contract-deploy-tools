"""Pytest plugins"""
from pathlib import Path

import pytest
import eth_tester
from web3.contract import Contract
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider


from deploy_tools import compile_project, deploy_compiled_contract


@pytest.fixture(scope='session')
def contract_assets(pytestconfig):
    contracts_path = Path(pytestconfig.rootdir) / 'contracts'
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
    return eth_tester.EthereumTester(eth_tester.PyEVMBackend())


@pytest.fixture(scope='session')
def web3(chain):
    return Web3(EthereumTesterProvider(chain))


@pytest.fixture(scope='session', autouse=True)
def set_default_account(web3):
    web3.eth.defaultAccount = web3.eth.accounts[0]


@pytest.fixture(scope='session')
def accounts(web3):
    return web3.eth.accounts


@pytest.fixture(scope='session')
def account_keys(chain):
    return chain.backend.account_keys


@pytest.fixture(autouse=True)
def chain_cleanup(chain):
    """Cleans up the state of the test chain after each test"""
    snapshot = chain.take_snapshot()
    yield
    chain.revert_to_snapshot(snapshot)
