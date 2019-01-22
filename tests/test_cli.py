import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from deploy_tools.cli import main


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def go_to_root_dir():
    current_path = os.getcwd()
    os.chdir(Path(__file__).parent.parent)
    yield
    os.chdir(current_path)


@pytest.mark.usefixtures('go_to_root_dir')
def test_default_compile(runner):
    result = runner.invoke(main, 'compile -d testcontracts')
    assert result.exit_code == 0
