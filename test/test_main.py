
import pytest
from click.testing import CliRunner

from src.fix_video.main import main


def test_main_help_option():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "SOURCE is the path to the file or directory to be processed" in result.output


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
        ["--mode", "compress", "-nr", "C:/dev/fix_video/origem"],
        ["--mode", "compress", "-nr", "-br", "0.5", "C:/dev/fix_video/origem"],
        ["--mode", "compress", "-nr", "-br", "0.25", "C:/dev/fix_video/origem"],
        ["--mode", "up", "-nr", "-r", "2", "C:/dev/fix_video/origem"],
        ["--mode", "up", "-nr", "-r", "2", "-br", "0.5", "C:/dev/fix_video/origem"],
    ],
)
def test_main_source_and_option(args):
    runner = CliRunner()
    result = runner.invoke(main, args)
    print(result.exit_code)  # -> 2
    print(result.exception)  # -> SystemExit: 2
    print(result.output)  # -> Mensagem de erro do Click

    assert result.exit_code == 0
