from setuptools import setup, find_packages

setup(
    name='contract-deploy-tools',
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    packages=find_packages(),
    install_requires=[
        'py-solc',
        'web3',
        'eth-utils',
        'click'
    ],
    entry_points="""
    [console_scripts]
    deploy-tools=deploy_tools.cli:main
    [pytest11]
    deploy-tools=deploy_tools.plugin
    """,
)
