import json
import subprocess
from pathlib import Path


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
        str(filepath.as_posix()),
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
