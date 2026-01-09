from pathlib import Path

import pytest
from click.testing import CliRunner

from src.fix_video.main import main


@pytest.mark.parametrize(
    "args, output",
    [
        [
            [
                "--mode",
                "fix",
                "-nr",
                "-ref",
                "./test/movie_test/VID_20211209_104553.mp4",
                "./test/movie_test/VID_20211211_181906.mp4",
            ],
            {"fileout": "./test/movie_test/VID_20211211_181906.fix.mp4"},
        ],
    ],
    ids=[
        "simple fix",
    ],
)
def test_fix_untrunc_file(GET_MOVIE_INFO, args, output):
    # Arrange
    original_file = Path(args[-1])
    original_file_info = GET_MOVIE_INFO(original_file)

    # Act
    runner = CliRunner()
    result = runner.invoke(main, args)
    print(result.exit_code)  # -> 2

    # Post-Act
    output_file = Path(output["fileout"])
    output_file_info = GET_MOVIE_INFO(output_file)
    out = output_file_info.get("format")

    assert len(original_file_info) == 0
    assert len(output_file_info) > 0 and len(out) > 0

    # Cleanup
    if output_file.exists():
        output_file.unlink()


@pytest.mark.parametrize(
    "args",
    [
        [
            "--mode",
            "fix",
            "-nr",
            "-ref",
            "./test/movie_test/VID_20211209_104553.mp4",
            "./test/movie_test/",
        ],
    ],
    ids=[
        "simple fix",
    ],
)
def test_fix_untrunc_path(args):
    # Arrange
    _original_path = Path(args[-1])

    # Act
    runner = CliRunner()
    result = runner.invoke(main, args)
    print(result.exit_code)  # -> 2
