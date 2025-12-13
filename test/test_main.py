import pytest
from click.testing import CliRunner

from src.fix_video.main import main


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
        ["--mode", "fIx", "-nr", "C:/dev/fix_video/origem"],
        ["--mode", "fIx", "C:/dev/fix_video/origem"],
        ["--mode", "compress", "C:/dev/fix_video/origem"],
        ["--mode", "compress", "C:/Users/fkfouri/Downloads/2017 - Aulas ITA/"],
    ],
)
def test_main_source_and_option(args):
    runner = CliRunner()
    result = runner.invoke(main, args)
    print(result.exit_code)  # -> 2
    print(result.exception)  # -> SystemExit: 2
    print(result.output)  # -> Mensagem de erro do Click

    assert result.exit_code == 0
