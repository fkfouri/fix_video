#!/usr/bin/env python3.6
import os
import subprocess
import sys
from pathlib import Path

from tqdm import tqdm

__THIS_PATH__ = (
    Path(os.path.dirname(sys.executable)) if getattr(sys, "frozen", False) else Path(os.path.dirname(__file__))
)

ORIGEM = Path("/mnt/c/dev/fix_video/origem")
DESTINO = Path("/mnt/c/dev/fix_video/destino")

if not DESTINO.exists():
    DESTINO.mkdir(parents=True, exist_ok=True)


def fix_video_using_ffmpeg(f, output_dir):
    out_f = os.path.join(output_dir, os.path.basename(f))
    # ffmpeg -err_detect ignore_err -i video.mkv -c copy video_fixed.mkv
    exit_code = subprocess.call(["ffmpeg", "-err_detect", "ignore_err", "-i", f, "-c", "copy", out_f])
    print(f"🟢🟢 fixed video:{f}, output: {out_f}, exist_code: {exit_code}🟢🟢\n\n\n\n")
    f.unlink()


def is_video_file(f):
    return f.lower().endswith(((".mp4", ".mkv")))


def fix_videos(_input_dir, output_dir):
    for f in os.listdir(_input_dir):
        if os.path.isdir(f):
            fix_videos(os.path.join(_input_dir, f), output_dir)
        if not is_video_file(f):
            continue
        fix_video_using_ffmpeg(os.path.join(_input_dir, f), output_dir)


for file in tqdm(ORIGEM.glob("**/*.mp4")):
    if file.is_file():
        fix_video_using_ffmpeg(file, DESTINO)

# def start(input_dir, output_dir):

# if __name__ == '__main__':
#     if len(sys.argv) < 2:
#         print('Usage: video-errors-fixer.py <input-dir> <output-dir>')
#         sys.exit(1)
#     input_dir = sys.argv[1]
#     output_dir = sys.argv[2]
#     if input_dir is output_dir:
#         print(f'both input and output dir are the same: {input_dir}')
#         sys.exit(1)
#     if not os.path.isdir(input_dir):
#         print(f'input dir is not a directory: {input_dir}')
#         sys.exit(1)
#     if not os.path.isdir(output_dir):
#         print(f'output dir is not a directory: {output_dir}')
#         sys.exit(1)

#     fix_videos(input_dir, output_dir)
