import os
import sys
from pathlib import Path

__THIS_PATH__ = (
    Path(os.path.dirname(sys.executable)) if getattr(sys, "frozen", False) else Path(os.path.dirname(__file__))
)

ACTUAL_PATH = Path.cwd()
# REPORT_COMPRESS = ACTUAL_PATH / "__compress_report_ffmpeg.json"
# REPORT_FFPROBE = ACTUAL_PATH / "__ffprobe_report.json"
# REPORT_ERROR = ACTUAL_PATH / "__error_report.json"


# ACTUAL_PATH = Path("C:/dev/fix_video/origem")
ORIGEM = ACTUAL_PATH
DESTINO = ACTUAL_PATH
JPEG_QUALITY = 75
PNG_QUALITY = "70-85"
REMOVE = True

PADROES = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff", "*.webp"]
