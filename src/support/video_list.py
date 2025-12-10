from pathlib import Path

from setup import PADROES


def list_videos_in_directory(directory: Path) -> list:
    """Lista todos os arquivos de vídeo em um diretório com base em padrões fornecidos."""

    video_files = []
    for padrao in PADROES:
        video_files.extend(directory.glob(f"**/{padrao}"))

    return video_files


# def is_video_file(f):
#     return f.lower().endswith(((".mp4", ".mkv", ".mov")))


# def fix_videos(_input_dir, output_dir):
#     for f in os.listdir(_input_dir):
#         if os.path.isdir(f):
#             fix_videos(os.path.join(_input_dir, f), output_dir)
#         if not is_video_file(f):
#             continue
#         fix_video_using_ffmpeg(os.path.join(_input_dir, f), output_dir)
