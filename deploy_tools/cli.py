import click

from deploy_tools.files import write_compiled_contracts, ensure_path_exists
from .compile import compile_project


@click.group()
def main():
    pass


@main.command(short_help='Compile all contracts')
@click.option(
    '--contracts-dir',
    '-d',
    help='Directory of the contracts sources',
    default='contracts',
    show_default=True,
    type=click.Path(file_okay=False, exists=True))
@click.option(
    '--optimize',
    '-o',
    default=False,
    help='Turns on the solidity optimizer',
    is_flag=True)
def compile(contracts_dir, optimize):
    compiled_contracts = compile_project(contracts_dir, optimize=optimize)

    ensure_path_exists('build')
    write_compiled_contracts(compiled_contracts, 'build/contracts.json')
