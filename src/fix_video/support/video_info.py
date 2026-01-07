import json
import re
import subprocess
from pathlib import Path

from ..setup import REGULAR_IGNORE, SPEED_IGNORE


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
        "-i",
        str(filepath.as_posix()),
    ]

    try:
        result = subprocess.run(command, capture_output=True, check=True)
        stdout = result.stdout.decode("utf-8")
        info = json.loads(stdout)
        info = info | {
            "path": "/".join(filepath.parts[-4:]),
            "size_mb": f"{filepath.stat().st_size/1024**2:.2f} Mb",
        }
        return info

    except FileNotFoundError:
        raise RuntimeError("ffprobe não encontrado. Instale o FFmpeg no sistema.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao executar ffprobe: {e.stderr}")
    except json.JSONDecodeError:
        raise RuntimeError("ffprobe retornou uma saída inválida (não é JSON).")
    except Exception as e:
        raise RuntimeError(f"Erro inesperado ao obter informações do vídeo: {str(e)}")


def video_should_be_processed(
    info: dict, filename: str, speed_ignore=SPEED_IGNORE, regular_ignore=REGULAR_IGNORE
) -> bool:
    """
    Verifica se o vídeo deve ser processado com base nas tags e padrões de nome de arquivo.

    Args:
        info (dict): Informações do vídeo obtidas do ffprobe
        filename (str): Nome do arquivo de vídeo
        speed_ignore (str): Padrão regex para ignorar vídeos já acelerados
        regular_ignore (str): Padrão regex para ignorar vídeos já processados

    Returns:
        bool: True se o vídeo deve ser processado, False caso contrário
    """

    tag_check = info.get("format", {}).get("tags", {}).get("genre", "")

    if (
        "Processado" in tag_check
        or "Processed" in tag_check
        or re.search(speed_ignore, filename, re.IGNORECASE)
        or re.search(regular_ignore, filename, re.IGNORECASE)
    ):
        return False

    return True
