import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

__THIS_PATH__ = (
    Path(os.path.dirname(sys.executable)) if getattr(sys, "frozen", False) else Path(os.path.dirname(__file__))
)

ACTUAL_PATH = Path.cwd()


# ORIGEM = Path("/mnt/c/Users/fkfouri/Downloads")
# ORIGEM = Path("/mnt/c/Users/fkfouri/OneDrive/Imagens/Screenpresso")
ORIGEM = Path("/mnt/c/dev/fix_video/origem")
# DESTINO = Path("/mnt/c/dev/fix_video/destino")
DESTINO = Path("/mnt/c/dev/fix_video/origem")

REPORT = __THIS_PATH__ / "__compress_report_ffmpeg.json"
REMOVE = True
FIX_TYPE = "compress"
FIX_FLAG = ".fix.up"
IGNORE = r".fix\.mp4$"
SPEED_IGNORE = r".fix\.up\.mp4$"
TOTAL_FILES = 0

# METADADOS que serão adicionados em TODOS os vídeos processados
CUSTOM_METADATA = {
    "year": datetime.now().year,
    "date": datetime.now().strftime("%Y-%m-%d"),
    "comment": "Acelerado 1.75× com FFmpeg (setpts + atempo)",
    "description": "Vídeo corrigido e otimizado automaticamente",
    "genre": "Processado 1.75x",
    "copyright": f"© {datetime.now().year} FKFouri",
    "velocidade": "1.75x",  # tag personalizada
    "processado_com": "Python + FFmpeg",
}

SPEED_UP = [
    "-vf",
    "setpts=PTS/1.75",
    "-af",
    "atempo=1.75",
]


if not DESTINO.exists():
    DESTINO.mkdir(parents=True, exist_ok=True)


def append_json_line(new_item):
    global TOTAL_FILES
    with open(REPORT, "a", encoding="utf-8") as f:
        f.write(json.dumps(new_item, ensure_ascii=False))
        f.write("\n")
        TOTAL_FILES += 1


def get_video_info(filepath: Path) -> dict:
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

    if not filepath.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    # Comando ffprobe mais completo e organizado
    command = [
        "ffprobe",
        "-v",
        "quiet",  # Remove logs desnecessários
        "-print_format",
        "json",  # Saída em JSON
        "-show_format",  # Informações do container (duração, tamanho, bitrate...)
        "-show_streams",  # Informações de cada stream (vídeo, áudio, legendas...)
        "-show_chapters",  # Opcional: capítulos (se houver)
        str(filepath),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    except FileNotFoundError:
        raise RuntimeError("ffprobe não encontrado. Instale o FFmpeg no sistema.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao executar ffprobe: {e.stderr}")
    except json.JSONDecodeError:
        raise RuntimeError("ffprobe retornou uma saída inválida (não é JSON).")


def build_metadata_args() -> list:
    """Converte o dicionário CUSTOM_METADATA em argumentos do FFmpeg"""
    args = []
    for key, value in CUSTOM_METADATA.items():
        args.extend(["-metadata", f"{key}={value}"])
    return args


def fix_video_using_ffmpeg(original_file: Path, output_dir):
    clean_name = original_file.stem.replace(".fix", "")
    new_name = f"{clean_name}{FIX_FLAG}{original_file.suffix}"
    out_f = output_dir / new_name

    base_cmd = ["ffmpeg", "-y"]  # -y = sobrescreve sem perguntar

    if FIX_TYPE == "error":
        # Apenas correção de erros → stream copy (sem reencodar)
        cmd = (
            base_cmd
            + [
                "-err_detect",
                "ignore_err",
                "-i",
                str(original_file),
                "-c",
                "copy",  # sem reencodar
            ]
            + build_metadata_args()
            + [str(out_f)]
        )

    elif FIX_TYPE == "compress":
        # Reencoda com compressão + aceleração + metadados
        cmd = (
            base_cmd
            + [
                "-i",
                str(original_file),
                "-r",
                "24",  # força 24 fps
                "-b:v",
                "400k",
                "-b:a",
                "128k",
                "-ar",
                "44100",
            ]
            + SPEED_UP
            + build_metadata_args()
            + [str(out_f)]
        )
    elif FIX_TYPE == "convert":
        ...
        # Converte MOV (ou qualquer) → .mpeg (H.264/AAC)
        # cmd += ["-i", str(infile)]
        # cmd += ["-c:v", "libx264", "-crf", "23", "-preset", "medium"]
        # cmd += ["-c:a", "aac", "-b:a", "128k", "-vf", "format=yuv420p"]
        # cmd += get_metadata() + [str(outfile)]

    else:
        raise ValueError("FIX_TYPE deve ser 'error' ou 'compress'")

    start_time_iso = datetime.now().isoformat()
    start = time.time()

    exit_code = subprocess.call(cmd)
    print(f"\n🟢🟢 fixed video:{original_file}, output: {out_f}, exist_code: {exit_code}🟢🟢\n\n")
    out_f = Path(out_f)

    finish_time_iso = datetime.now().isoformat()
    finised = time.time()

    delta = finised - start
    minutes, seconds = divmod(delta, 60)
    processing_time = f"{int(minutes):02d}:{int(seconds):02d}"

    report = {
        "original": "/".join(original_file.parts[-4:]),
        "original_size_mb": f"{original_file.stat().st_size / 1024**2:.2f}",
        "final": "/".join(out_f.parts[-4:]),
        "final_size_mb": f"{out_f.stat().st_size / 1024**2:.2f}",
        "start_time": start_time_iso,
        "finish_time": finish_time_iso,
        "processing_time": f"{processing_time} (MM:SS)",
        "fix_type": FIX_TYPE,
        "speed_applied": "1.75x" if FIX_TYPE == "compress" else "none",
        "metadata_added": "yes",
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
    print(f"Você está executando de: {ACTUAL_PATH}\n")
    print(f"O executável está em:{__THIS_PATH__}\n")

    for file in tqdm(ORIGEM.glob("**/*.mp4")):
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
                or re.search(IGNORE, file.name, re.IGNORECASE)
            ):
                print(f"⏭️ ⏭️  Skipping already processed file: {file} ⏭️ ⏭️ ")
                continue

            with open(__THIS_PATH__ / "__file_info.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(_info, ensure_ascii=False))
                f.write("\n")
                TOTAL_FILES += 1

            _root_ref = len(ORIGEM.parts)

            if len(file.parts) == _root_ref + 1:
                diretorio_destino = DESTINO
            else:
                diretorio_destino = DESTINO / Path(*file.parts[_root_ref:-1])

            diretorio_destino.mkdir(parents=True, exist_ok=True)

            fix_video_using_ffmpeg(file, diretorio_destino)

print(f"\n\n✅✅ All done! ✅✅\n Total Files: {TOTAL_FILES}\n Finished at {datetime.now().isoformat()}\n\n")
