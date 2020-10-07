"""Pytest plugins"""
import io
import os
import shutil
import socket
import subprocess
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler

import eth_tester
import pytest
from eth_tester_rpc.server import get_application
from eth_tester_rpc.utils.compat_threading import make_server, spawn
from web3 import Web3
from web3.contract import Contract
from web3.providers.eth_tester import EthereumTesterProvider

from deploy_tools import compile_project, deploy_compiled_contract
from deploy_tools.compile import DEFAULT_EVM_VERSION

CONTRACTS_FOLDER_OPTION = "--contracts-dir"
CONTRACTS_FOLDER_OPTION_HELP = "Folder which contains the project smart contracts"
EVM_VERSION_OPTION = "--evm-version"
EVM_VERSION_OPTION_HELP = (
    "The evm target version one of: "
    "petersburg, constantinople, byzantium, spuriousDragon, tangerineWhistle, or homestead"
)
EXPOSE_RPC_OPTION = "--expose-rpc"
EXPOSE_RPC_OPTION_HELP = (
    "Ports on which you want to expose the web3 rpc of the test chain."
)


def pytest_addoption(parser):
    parser.addoption(CONTRACTS_FOLDER_OPTION, help=CONTRACTS_FOLDER_OPTION_HELP)
    parser.addini(CONTRACTS_FOLDER_OPTION, CONTRACTS_FOLDER_OPTION_HELP)
    parser.addoption(
        EVM_VERSION_OPTION, help=EVM_VERSION_OPTION_HELP, default=DEFAULT_EVM_VERSION
    )
    parser.addini(
        EVM_VERSION_OPTION, EVM_VERSION_OPTION_HELP, default=DEFAULT_EVM_VERSION
    )
    parser.addoption(EXPOSE_RPC_OPTION, help=EXPOSE_RPC_OPTION_HELP)
    parser.addini(EXPOSE_RPC_OPTION, EXPOSE_RPC_OPTION_HELP, default=None)


def get_contracts_folder(pytestconfig):
    if pytestconfig.getoption(CONTRACTS_FOLDER_OPTION, default=None):
        return pytestconfig.getoption(CONTRACTS_FOLDER_OPTION)
    return Path(pytestconfig.rootdir) / "contracts"


def get_evm_version(pytestconfig):
    return pytestconfig.getoption(EVM_VERSION_OPTION)


@pytest.fixture(scope="session", autouse=True)
def remove_click_options_environment_variables():
    """Remove the environment variables used by click options in the CLI.
    Otherwise they will interfere with the tests.
    """
    for env_var in list(os.environ.keys()):
        if env_var.startswith(
            (
                "JSONRPC",
                "KEYSTORE",
                "GAS",
                "GAS_PRICE",
                "AUTO_NONCE",
                "CONTRACTS_DIR",
                "OPTIMIZE",
                "EVM_VERSION",
                "COMPILED_CONTRACTS",
            )
        ):
            del os.environ[env_var]


@pytest.fixture(scope="session")
def contract_assets(pytestconfig):
    """
    Returns the compilation assets (dict containing the content of `contracts.json`) of all compiled contracts
    To change the directory of the contracts, use the pytest option --contracts-dir
    To change the target evm version, use the pytest option --evm-version
    """
    contracts_path = get_contracts_folder(pytestconfig)
    evm_version = get_evm_version(pytestconfig)
    return compile_project(
        contracts_path=contracts_path, optimize=True, evm_version=evm_version
    )


@pytest.fixture(scope="session")
def deploy_contract(web3, contract_assets):
    """Fixture to deploy a contract on the current chain

       Usage: `deploy_contract('contract_identifier', constructor_args=(1,2,3))`
    """

    def deploy_contract_function(
        contract_identifier: str, *, constructor_args=()
    ) -> Contract:
        return deploy_compiled_contract(
            abi=contract_assets[contract_identifier]["abi"],
            bytecode=contract_assets[contract_identifier]["bytecode"],
            web3=web3,
            constructor_args=constructor_args,
        )

    return deploy_contract_function


class NullIO(StringIO):
    def write(self, txt):
        pass


def silent_stdout(fn):
    """Decorator to silence functions so that they will not print anything."""

    def silent_fn(*args, **kwargs):
        with redirect_stdout(NullIO()):
            return fn(*args, **kwargs)

    return silent_fn


@pytest.fixture(scope="session")
def chain(pytestconfig):
    """
    The running ethereum tester chain
    Can be used as to manipulate the chain, e.g. chain.mine_block()
    see https://github.com/ethereum/eth-tester for more
    """
    expose_port = pytestconfig.getoption(EXPOSE_RPC_OPTION)
    if expose_port:
        if is_port_in_use(expose_port):
            raise EnvironmentError(
                f"The port {expose_port} is already in use on the machine."
            )
        # redirect stdout because otherwise the application prints every request and result
        # Get the eth-tester-rpc application
        application = get_application()
        rpc = application.rpc_methods

        # Remove the printing of every rpc replies to avoid flooding the tests outputs
        application = silent_stdout(application)
        application.rpc_methods = rpc

        # Start the server so that we can use rpc on http://localhost:expose_port
        # Silence the logging of every request from the handler to avoid flooding tests outputs
        class NoLoggingRequestHandler(WSGIRequestHandler):
            def log_request(self, code="-", size="-"):
                pass

        server = make_server(
            "localhost",
            int(expose_port),
            application,
            handler_class=NoLoggingRequestHandler,
        )
        spawn(server.serve_forever)

        # yield the eth_tester chain
        yield application.rpc_methods.client
    else:
        yield eth_tester.EthereumTester(eth_tester.PyEVMBackend())

    if pytestconfig.getoption(EXPOSE_RPC_OPTION):
        try:
            server.stop()
        except AttributeError:
            server.shutdown()


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", int(port))) == 0


@pytest.fixture(scope="session")
def web3(chain):
    """
    Web3 object connected to the ethereum tester chain
    """
    return Web3(EthereumTesterProvider(chain))


@pytest.fixture(scope="session", autouse=True)
def set_default_account(web3):
    """Sets the web3 default account to the first account of `accounts`"""
    web3.eth.defaultAccount = web3.eth.accounts[0]


@pytest.fixture(scope="session")
def default_account(web3):
    """Returns the default account which is used to deploy contracts"""
    return web3.eth.defaultAccount


@pytest.fixture(scope="session")
def accounts(web3):
    """
    Some ethereum accounts on the test chain with some ETH
    """
    return web3.eth.accounts


@pytest.fixture(scope="session")
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


def _find_solc(msgs):
    solc = shutil.which("solc")
    if solc:
        msgs.write("solc: {}\n".format(solc))
    else:
        msgs.write("solc: <NOT FOUND>\n")
    return solc


def _get_solc_version(msgs):
    try:
        process = subprocess.Popen(["solc", "--version"], stdout=subprocess.PIPE)
    except Exception as err:
        msgs.write("solidity version: <ERROR {}>".format(err))
        return

    out, _ = process.communicate()

    lines = out.decode("utf-8").splitlines()
    for line in lines:
        if line.startswith("Version: "):
            msgs.write("solidity version: {}\n".format(line[len("Version: ") :]))
            break
    else:
        msgs.write("solidity version: <UNKNOWN>")


def pytest_report_header(config):
    msgs = io.StringIO()
    solc = _find_solc(msgs)

    if solc:
        _get_solc_version(msgs)

    return msgs.getvalue()
