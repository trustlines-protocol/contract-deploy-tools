==========
Change Log
==========
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
