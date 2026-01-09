from pathlib import Path

import pytest
from click.testing import CliRunner

from src.fix_video.main import main


@pytest.mark.parametrize(
    "args, output",
    [
        [
            ["--mode", "compress", "-nr", "./test/files/Big_Buck_Bunny_1080_10s_30MB.mp4"],
            {"fileout": "./test/files/Big_Buck_Bunny_1080_10s_30MB.fix.comp.mp4", "fator": 0.1},
        ],
        [
            ["--mode", "compress", "-nr", "-br", "2000", "./test/files/Big_Buck_Bunny_1080_10s_30MB.mp4"],
            {"fileout": "./test/files/Big_Buck_Bunny_1080_10s_30MB.fix.comp.mp4", "fator": 0.2},
        ],
        [
            ["--mode", "compress", "-nr", "-br", "8000", "./test/files/Big_Buck_Bunny_1080_10s_30MB.mp4"],
            {"fileout": "./test/files/Big_Buck_Bunny_1080_10s_30MB.fix.comp.mp4", "fator": 0.4},
        ],
        [
            ["--mode", "compress", "-nr", "-br", ".5", "./test/files/Big_Buck_Bunny_1080_10s_30MB.mp4"],
            {"fileout": "./test/files/Big_Buck_Bunny_1080_10s_30MB.fix.comp.mp4", "fator": 0.5},
        ],
        [
            ["--mode", "compress", "-nr", "-br", ".25", "./test/files/Big_Buck_Bunny_1080_10s_30MB.mp4"],
            {"fileout": "./test/files/Big_Buck_Bunny_1080_10s_30MB.fix.comp.mp4", "fator": 0.25},
        ],
        [
            ["--mode", "compress", "-nr", "-br", ".05", "./test/files/Big_Buck_Bunny_1080_10s_30MB.mp4"],
            {"fileout": "./test/files/Big_Buck_Bunny_1080_10s_30MB.fix.comp.mp4", "fator": 0.05},
        ],
        [
            ["--mode", "compress", "-nr", "-br", ".01", "./test/files/Big_Buck_Bunny_1080_10s_30MB.mp4"],
            {"fileout": "./test/files/Big_Buck_Bunny_1080_10s_30MB.fix.comp.mp4", "fator": 0.02},
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
        "big buck bunny",
        "big buck bunny 2000k",
        "big buck bunny 8000k",
        "big buck bunny 50%",
        "big buck bunny 75%",
        "big buck bunny 95%",
        "big buck bunny 99%",
    ],
)
def test_compress_file(GET_MOVIE_INFO, args, output):
    # Arrange
    runner = CliRunner()

    fator = output.get("fator", 1)

    original_file = Path(args[-1])
    original_file_info = GET_MOVIE_INFO(original_file)
    ini = original_file_info.get("format")

    # Act
    result = runner.invoke(main, args)
    print(result.exit_code)  # -> 2
    print(result.exception)  # -> SystemExit: 2
    print(result.output)  # -> Mensagem de erro do Click

    # Post-Act
    output_file = Path(output["fileout"])
    output_file_info = GET_MOVIE_INFO(output_file)
    out = output_file_info.get("format")

    # Assert
    assert result.exit_code == 0
    assert output_file.exists() is True
    assert output_file_info is not None
    assert int(out["size"]) < int(ini["size"])
    assert float(out["duration"]) // 1 == float(ini["duration"]) // 1
    assert int(out["bit_rate"]) < int(ini["bit_rate"])
    assert int(out["bit_rate"]) / int(ini["bit_rate"]) < fator  # menor que o original

    # Cleanup
    if output_file.exists():
        ...
        output_file.unlink()
