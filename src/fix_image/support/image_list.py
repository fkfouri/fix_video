from pathlib import Path

from ..setup import PADROES


def list_image_in_directory(source: Path) -> list:
    """Lista todos os arquivos de imagem em um diretório com base em padrões fornecidos."""

    if source.is_file():
        return [source]

    identified_files = []
    for padrao in PADROES:
        identified_files.extend(source.glob(f"**/{padrao}"))

    return [f for f in identified_files if "_fixed" not in f.stem.lower()]
