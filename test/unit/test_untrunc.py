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
            {"fileout": "./test/movie_test/VID_20211211_181906.mp4_fixed.mp4"},
        ],
        # ["--mode", "compress", "-nr", "-br", "0.5", "C:/dev/fix_video/origem"],
        # ["--mode", "fIx", "-nr", "C:/dev/fix_video/origem"],
        # ["--mode", "fIx", "C:/dev/fix_video/origem"],
        # ["--mode", "compress", "-nr", "C:/dev/fix_video/origem"],
        # ["--mode", "compress", "-nr", "-br", "0.25", "C:/dev/fix_video/origem"],
        # ["--mode", "up", "-nr", "-r", "2", "C:/dev/fix_video/origem"],
        # ["--mode", "up", "-nr", "-r", "2", "-br", "0.5", "C:/dev/fix_video/origem"],
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
