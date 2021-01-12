==========
Change Log
==========
`0.9.0`_ (2020-01-13)
-------------------------------
* Changed: Move transaction sending related functions from `deploy.py` to `transact.py`:
  `send_function_call_transaction`, `send_transaction`, `build_transaction_options`,
  `increase_transaction_options_nonce`, and `wait_for_successful_transaction_receipt`.
* Changed: Repurposed `send_function_call_transaction` to no longer wait for the success of the sent transaction
* Added: `wait_for_successful_function_call` that sends a function call and wait for its success
* Changed: Repurposed `send_transaction` to no longer wait for the success of the sent transaction
* Added: `wait_for_successful_transaction` that sends a transaction and wait for its success
* Added: `wait_for_successful_transaction_receipts` to wait for a list of transaction ids to be successful

`0.8.0`_ (2020-10-08)
-------------------------------
* Update web3 dependency to 5.7.0
* Add option `--expose-rpc=port` for pytest plugin to expose the rpc of the test chain on localhost:port.

`0.7.2`_ (2020-03-11)
-------------------------------
* Limit web3 dependency to <5.2 because of incompatibility.

`0.7.1`_ (2020-01-24)
-------------------------------
* Prefer web3.eth.defaultAccount for signing transactions

`0.7.0`_ (2019-11-04)
-------------------------------
* Add a send eth command to send eth on the command line

`0.6.1`_ (2019-10-14)
-------------------------------
* Set the ``from`` address field of a ``eth_sendTransaction`` RPC to the unlocked account of the Ethereum node

`0.6.0`_ (2019-09-26)
-------------------------------
* Change default evm target version of cli command ``compile`` to ``petersburg`` to match with the default of ``compile.compile_project`` (BREAKING)

`0.5.3`_ (2019-09-25)
-------------------------------
* Add ``build_initcode`` function that gives the initcode from a contract abi, bytecode, and constructor args

`0.5.2`_ (2019-09-20)
-------------------------------
* Add  ``initcode`` command that gives the initcode for a contract
* Improve parsing of function / constructor arguments from command line inputs

`0.5.1`_ (2019-08-19)
-------------------------------
* Add the  ``--optimize-runs`` option to the ``compile`` command

`0.5.0`_ (2019-08-15)
-------------------------------
* Change ``--optimize`` to a toggle option with default ``True``
* Enable optimization per default for contract compile functions
* Allow password to be empty for decrypting a keystore

`0.4.4`_ (2019-08-13)
-------------------------------
* Allow options to be configured via environment variables
  (e.g. ``KEYSTORE``, ``JSONRPC``)
* Add the ``generate-keystore`` command
* Add the ``--compiled-contracts`` option to the ``deploy`` command

`0.4.3`_ (2019-07-03)
-------------------------------
* Add call command to execute a function call to a smart contract

`0.4.2`_ (2019-06-26)
-------------------------------
* Add transact command to send a function call transaction to a smart contract

`0.4.1`_ (2019-06-21)
-------------------------------
* Add function to validate addresses as a callback for click

`0.4.0`_ (2019-06-05)
-------------------------------
* The minimum required web3 version is now 5.0.0b2
* contract-deploy-tools can now target a specific EVM version

`0.3.0`_ (2019-05-21)
-------------------------------
* Use -O instead of -o to enable optimization
* Print used version of solc in pytest plugin
* Add more options to deploy a contract (nonce, gas price, gas, signing key)
* Do not fail anymore if all gas has been used, but rely completely on the status field
* Add workaround for wrong fields in result of getTransactionReceipt in parity
* Add a contract deploy command
* Add option -o to specify output file
* Add options to minimize the output file
* Pin the target evm version to byzantium

`0.2.1`_ (2019-01-22)
-------------------------------
* Fix the dependencies

`0.2.0`_ (2019-01-22)
-------------------------------
* Add a pytest plugin that can be used when running tests

`0.1.1`_ (2019-01-18)
-------------------------------
* Fix missing bytecode in compiled contracts

`0.1.0`_ (2019-01-18)
-------------------------------
* Add a compile tool to compile contracts from the command line




.. _0.1.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.0.1...0.1.0
.. _0.1.1: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.1.0...0.1.1
.. _0.2.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.1.1...0.2.0
.. _0.2.1: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.2.0...0.2.1
.. _0.3.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.2.1...0.3.0
.. _0.4.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.3.0...0.4.0
.. _0.4.1: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.4.0...0.4.1
.. _0.4.2: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.4.1...0.4.2
.. _0.4.3: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.4.2...0.4.3
.. _0.4.4: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.4.3...0.4.4
.. _0.5.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.4.4...0.5.0
.. _0.5.1: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.5.0...0.5.1
.. _0.5.2: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.5.1...0.5.2
.. _0.5.3: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.5.2...0.5.3
.. _0.6.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.5.3...0.6.0
.. _0.6.1: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.6.0...0.6.1
.. _0.7.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.6.1...0.7.0
.. _0.7.1: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.7.0...0.7.1
.. _0.7.2: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.7.1...0.7.2
.. _0.8.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.7.2...0.8.0
.. _0.9.0: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.8.0...0.9.0
