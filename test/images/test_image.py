import pytest
from click.testing import CliRunner

from src.fix_image.main_image import main


def test_main_help_option():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "SOURCE is the path to the file or directory to be processed" in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["-nr", "./test/images_test"],
    ],
    ids=[
        "path",
    ],
)
def test_path(args):
    runner = CliRunner()
    result = runner.invoke(main, args)
    print(result.exit_code)  # -> 2
    print(result.exception)  # -> SystemExit: 2
    print(result.output)  # -> Mensagem de erro do Click

    assert result.exit_code == 0
