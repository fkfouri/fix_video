from pathlib import Path

import pytest

from src.fix_video.support.video_info import get_video_info


@pytest.fixture()
def GET_MOVIE_INFO():

    def get_movie_info(movie_path: Path) -> dict:

        if isinstance(movie_path, str):
            movie_path = Path(movie_path)

        if movie_path.exists() and movie_path.is_file():
            try:
                info = get_video_info(movie_path)
                return info
            except Exception:
                return {}

        return {}

    return get_movie_info
