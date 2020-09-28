import pytest


@pytest.fixture()
def contract(deploy_contract):
    return deploy_contract("TestContract", constructor_args=(4,))


def test_call(contract):
    assert contract.functions.testFunction(3).call() == 7


def test_chain_web3_synchrone(web3, chain):
    """Test that the chain fixture and web3 are connected to the same chain"""
    # Uses `chain` to mine a block and verify that web3 observes a new block
    block_number_before = web3.eth.blockNumber
    chain.mine_block()
    block_number_after = web3.eth.blockNumber
    assert block_number_after - block_number_before == 1


def test_chain_snapshot(web3, chain):
    """Test that reverting a snapshot via the `chain` fixture will affect the chain connected via web3"""
    block_number_before = web3.eth.blockNumber
    snapshot = chain.take_snapshot()
    chain.mine_block()
    chain.revert_to_snapshot(snapshot)
    block_number_after = web3.eth.blockNumber
    assert block_number_after == block_number_before
