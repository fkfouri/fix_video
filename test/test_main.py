import pytest
from click.testing import CliRunner

from src.main import main


def test_main_help_option():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "SOURCE é o arquivo ou diretório de entrada" in result.output


def test_main_no_source_option():
    runner = CliRunner()
    result = runner.invoke(main, ["."])
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "args",
    [
        ["--mode", "Y", "./origem"],
        ["--mode", "Y", "C:/dev/fix_video/origem"],
        ["--mode", "fIx1", "C:/dev/fix_video/origem"],
        ["--mode", "compress", "C:/dev/fix_video/origem"],
    ],
)
def test_main_source_and_option(args):
    runner = CliRunner()
    result = runner.invoke(main, args)
    print(result.exit_code)  # -> 2
    print(result.exception)  # -> SystemExit: 2
    print(result.output)  # -> Mensagem de erro do Click

    assert result.exit_code == 0
