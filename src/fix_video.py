import os
import subprocess
import sys
import re
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

def get_video_info(filepath: str) -> dict:
    """
    Executa ffprobe e retorna todas as informações do arquivo de vídeo em formato JSON (dict).
    
    Args:
        filepath (str): Caminho completo do arquivo MP4 (ou qualquer formato suportado pelo FFmpeg)
    
    Returns:
        dict: Dados completos do arquivo (streams + format)
    
    Raises:
        FileNotFoundError: Se o arquivo não existir
        RuntimeError: Se o ffprobe não estiver instalado ou falhar
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    
    # Comando ffprobe mais completo e organizado
    command = [
        "ffprobe",
        "-v", "quiet",                  # Remove logs desnecessários
        "-print_format", "json",        # Saída em JSON
        "-show_format",                 # Informações do container (duração, tamanho, bitrate...)
        "-show_streams",                # Informações de cada stream (vídeo, áudio, legendas...)
        "-show_chapters",               # Opcional: capítulos (se houver)
        str(filepath)
    ]
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    
    except FileNotFoundError:
        raise RuntimeError("ffprobe não encontrado. Instale o FFmpeg no sistema.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao executar ffprobe: {e.stderr}")
    except json.JSONDecodeError:
        raise RuntimeError("ffprobe retornou uma saída inválida (não é JSON).")



def fix_video_using_ffmpeg(original_file: Path, output_dir):
    new_name = f"{original_file.stem.replace(".fix","")}{FIX_FLAG}{original_file.suffix}"
    out_f = output_dir / new_name
    fixed_types = {
        "error": ["ffmpeg", "-err_detect", "ignore_err", "-i", str(original_file), "-c", "copy", str(out_f)],
        "compress": ["ffmpeg", "-i", str(original_file), "-r", "24", "-b:v", "400k", "-b:a", "128k", "-ar", "44100", "-y"] +SPEED_UP + [str(out_f)],
    }

    start_time = datetime.now().isoformat()
    start = time.time()

    exit_code = subprocess.call(fixed_types[FIX_TYPE])
    print(f"\n🟢🟢 fixed video:{original_file}, output: {out_f}, exist_code: {exit_code}🟢🟢\n\n")
    out_f = Path(out_f)

    finish_time = datetime.now().isoformat()    
    finised = time.time()

    delta = finised - start
    minutes, seconds = divmod(delta, 60)
    processing_time = f"{minutes:02d}:{seconds:02d}"

    report = {
        "original":"/".join(original_file.parts[-4:]),
        "original_size": f"{original_file.stat().st_size/1024**2:.2f} Mb",
    }
    report = report | {
        "final":"/".join(out_f.parts[-4:]),
        "final_size": f"{out_f.stat().st_size/1024**2:.2f} Mb",
    } 
    report = report | {
        "start_time": start_time,
        "finish_time": finish_time,
        "processing_time": f"{processing_time} - MM:SS", #processing_time, 
    }
    append_json_line(report)
    if REMOVE:
        original_file.unlink() 



def is_video_file(f):
    return f.lower().endswith(((".mp4", ".mkv")))


def fix_videos(_input_dir, output_dir):
    for f in os.listdir(_input_dir):
        if os.path.isdir(f):
            fix_videos(os.path.join(_input_dir, f), output_dir)
        if not is_video_file(f):
            continue
        fix_video_using_ffmpeg(os.path.join(_input_dir, f), output_dir)


if __name__ == "__main__":
    _root_ref = len(ORIGEM.parts)

    for file in tqdm(ORIGEM.glob("**/*.mp4")):

        if file.is_file() and not re.search(IGNORE, file):
            if len(file.parts) == _root_ref + 1:
                destino_sub = DESTINO
            else:
                destino_sub = DESTINO / Path(*file.parts[_root_ref:-1])

            destino_sub.mkdir(parents=True, exist_ok=True)
            
            fix_video_using_ffmpeg(file, DESTINO)

print(f"\n\n✅✅ All done! ✅✅\n\n Finished at {datetime.now().isoformat()}\n\n")
