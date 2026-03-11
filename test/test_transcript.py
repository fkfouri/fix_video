import pytest
from click.testing import CliRunner

from src.transcript.main import main


def test_main_help_option():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Transcript - A tool to generate transcripts from audio and video files" in result.output


def test_main_no_source_option():
    runner = CliRunner()
    result = runner.invoke(main, ["."])
    assert result.exit_code == 0


# C:\dev\Video\test.MP4


@pytest.mark.parametrize(
    "args",
    [
        ["C:/dev/Video/test.MP4"],
    ],
)
def test_transcript(args):
    runner = CliRunner()
    result = runner.invoke(main, args)
    print(result.exit_code)  # -> 2
    print(result.exception)  # -> SystemExit: 2
    print(result.output)  # -> Mensagem de erro do Click

    assert result.exit_code == 0
