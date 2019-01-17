import click

from deploy_tools.files import write_compiled_contracts, ensure_path_exists
from .compile import compile_project


@click.group()
def main():
    pass


@main.command(short_help='Compile all contracts')
@click.option(
    '--source-dir',
    '-d',
    help='Directory of the sources',
    default='contracts',
    show_default=True,
    type=click.Path(file_okay=False, exists=True))
def compile(source_dir):
    compiled_contracts = compile_project(source_dir)

    ensure_path_exists('build')
    write_compiled_contracts(compiled_contracts, 'build/contracts.json')
