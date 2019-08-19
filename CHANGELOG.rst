==========
Change Log
==========

`unreleased`_
-------------------------------


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
.. _unreleased: https://github.com/trustlines-protocol/contract-deploy-tools/compare/0.5.1...master
