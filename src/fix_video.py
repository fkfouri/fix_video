import os
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import time

from tqdm import tqdm

__THIS_PATH__ = (
    Path(os.path.dirname(sys.executable)) if getattr(sys, "frozen", False) else Path(os.path.dirname(__file__))
)

ORIGEM = Path("/mnt/c/Users/fkfouri/Downloads")
ORIGEM = Path("/mnt/c/Users/fkfouri/OneDrive/Imagens/Screenpresso")
DESTINO = Path("/mnt/c/dev/fix_video/origem")
DESTINO = Path("/mnt/c/dev/fix_video/destino")
REPORT = __THIS_PATH__ / "__compress_report_ffmpeg.json"
REMOVE = True
FIX_TYPE = "compress"
FIX_FLAG = ".fix.up"
IGNORE = r".fix\.mp4$"
SPEED_IGNORE = r".fix\.up\.mp4$"

SPEED_UP = [
    "-vf",
    "setpts=PTS/1.75",
    "-af",
    "atempo=1.75",
]


if not DESTINO.exists():
    DESTINO.mkdir(parents=True, exist_ok=True)


def append_json_line(new_item):
    with open(REPORT, "a", encoding="utf-8") as f:
        f.write(json.dumps(new_item, ensure_ascii=False))
        f.write("\n")


def fix_video_using_ffmpeg(f, output_dir):
    # new_name = F
    out_f = os.path.join(output_dir, os.path.basename(f))
    fixed_types = {
        "error": ["ffmpeg", "-err_detect", "ignore_err", "-i", f, "-c", "copy", out_f],
        "compress": ["ffmpeg", "-i", f, "-r", "24", "-b:v", "400k", "-b:a", "128k", "-ar", "44100", "-y", out_f],
        }
    # ffmpeg -err_detect ignore_err -i video.mkv -c copy video_fixed.mkv
    exit_code = subprocess.call(fixed_types[FIX_TYPE])
    print(f"\n🟢🟢 fixed video:{f}, output: {out_f}, exist_code: {exit_code}🟢🟢\n\n")
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


