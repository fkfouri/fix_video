import re
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from setup import __THIS_PATH__, ACTUAL_PATH, DESTINO, ORIGEM, PADROES, REGULAR_IGNORE, REPORT_FFPROBE, SPEED_IGNORE
from support import fix_video_using_ffmpeg, get_video_info, insert_line_at_report

TOTAL_FILES = 0


if __name__ == "__main__":
    if not DESTINO.exists():
        DESTINO.mkdir(parents=True, exist_ok=True)

    print(f"Você está executando de: {ACTUAL_PATH}")
    print(f"O executável está em: {__THIS_PATH__}")

    videos = []
    for padrao in PADROES:
        videos.extend(ORIGEM.glob(f"**/{padrao}"))

    for file in tqdm(videos):
        info = ""
        if file.is_file():
            _info = get_video_info(file)
            _info = _info | {
                "path": "/".join(file.parts[-4:]),
                "size_mb": f"{file.stat().st_size/1024**2:.2f} Mb",
            }
            info = _info.get("format", {}).get("tags", {}).get("genre", "")

            if (
                "Processado" in info
                or "1.75x" in info
                or re.search(SPEED_IGNORE, file.name, re.IGNORECASE)
                or re.search(REGULAR_IGNORE, file.name, re.IGNORECASE)
            ):
                print(f"⏭️ ⏭️  Skipping already processed file: {file} ⏭️ ⏭️ ")
                continue

            insert_line_at_report(REPORT_FFPROBE, _info)

            _root_ref = len(ORIGEM.parts)

            if len(file.parts) == _root_ref + 1:
                diretorio_destino = DESTINO
            else:
                diretorio_destino = DESTINO / Path(*file.parts[_root_ref:-1])

            diretorio_destino.mkdir(parents=True, exist_ok=True)

            fix_video_using_ffmpeg(file, diretorio_destino)

print(f"\n✅✅ All done! ✅✅\n Total Files: {TOTAL_FILES}\n Finished at {datetime.now().isoformat()}\n\n")
