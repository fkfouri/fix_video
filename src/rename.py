import os
import re
import sys
from pathlib import Path

from tqdm import tqdm

__THIS_PATH__ = (
    Path(os.path.dirname(sys.executable)) if getattr(sys, "frozen", False) else Path(os.path.dirname(__file__))
)

ORIGEM = Path(r"C:\Users\FA3QQ8I\dev\captures")
DESTINO = Path(r"C:\Users\FA3QQ8I\dev\captures_fixed")
FIX_TYPE = "compress"
FIX_Flag = ".fix"
IGNORE = r".fix\.mp4$"

for file in tqdm(DESTINO.glob("**/*.mp4")):
    if file.is_file() and not re.search(IGNORE, file.name):
        new_name = file.with_name(f"{file.stem}{FIX_Flag}{file.suffix}")
        file.rename(new_name)
        file = file
