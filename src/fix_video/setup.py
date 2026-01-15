import os
import sys
from datetime import datetime
from pathlib import Path

__THIS_PATH__ = (
    Path(os.path.dirname(sys.executable)) if getattr(sys, "frozen", False) else Path(os.path.dirname(__file__))
)

ACTUAL_PATH = Path.cwd()
REPORT_COMPRESS = ACTUAL_PATH / "__compress_report_ffmpeg.json"
REPORT_FFPROBE = ACTUAL_PATH / "__ffprobe_report.json"
REPORT_ERROR = ACTUAL_PATH / "__error_report.json"


# ACTUAL_PATH = Path("C:/dev/fix_video/origem")
ORIGEM = ACTUAL_PATH
DESTINO = ACTUAL_PATH
DATE_STANDARD = "%Y%m%d"

# # ORIGEM = Path("/mnt/c/Users/fkfouri/Downloads")
# # ORIGEM = Path("/mnt/c/Users/fkfouri/OneDrive/Imagens/Screenpresso")
# ORIGEM = Path("/mnt/c/dev/fix_video/origem")
# # DESTINO = Path("/mnt/c/dev/fix_video/destino")
# DESTINO = Path("/mnt/c/dev/fix_video/origem")


REMOVE = True
FIX_TYPE = "compress"
REGULAR_IGNORE = r".fix\.mp4$"
SPEED_IGNORE = r".fix\.up\.mp4$"
PADROES = ["*.mp4", "*.mov", "*.avi", "*.mkv", "*.webm", "*.m4v", ".3gp"]
BIT_RATE = 400  # kbps para compressão

# METADADOS que serão adicionados em TODOS os vídeos processados
# "Acelerado 1.75× com FFmpeg (setpts + atempo)",
CUSTOM_METADATA = {
    "year": datetime.now().year,
    "date": datetime.now().strftime("%Y-%m-%d"),
    "comment": "Fixed and optimized automatically",
    "description": "Fixed and optimized automatically",
    "genre": "Processed",
    "copyright": f"© {datetime.now().year} FKfouri",
    "velocidade": "1.75x",  # tag personalizada
    "processado_com": "Python + FFmpeg",
}


def FIX_FLAG(mode=None) -> str:
    if mode == "up":
        return ".fix.up"
    elif mode == "compress":
        return ".fix.comp"
    return ".fix"


def SPEED_UP(value=1.75) -> list:
    return [
        "-vf",
        f"setpts=PTS/{value}",
        "-af",
        f"atempo={value}",
    ]


# SPEED_UP = [
#     "-vf",
#     "setpts=PTS/1.75",
#     "-af",
#     "atempo=1.75",
# ]
