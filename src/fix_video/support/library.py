from click import Path

from ..setup import CUSTOM_METADATA


def build_metadata_args(what="") -> list:
    """Converte o dicionário CUSTOM_METADATA em argumentos do FFmpeg"""
    args = []
    genre = "Processed"
    for key, value in CUSTOM_METADATA.items():
        if key not in ["genre"]:  # genre será adicionado separadamente
            args.extend(["-metadata", f"{key}={value}"])

    args.extend(["-metadata", f"genre={genre} {what}".strip()])
    return args


def define_destination_directory(original_file: Path, origem: Path, destino: Path) -> Path:
    """Define o diretório de destino mantendo a estrutura de pastas relativa."""
    _root_reference_size_ = len(origem.parts)

    if len(original_file.parts) == _root_reference_size_ + 1:
        diretorio_destino = destino
    else:
        diretorio_destino = destino / Path(*original_file.parts[_root_reference_size_:-1])

    diretorio_destino.mkdir(parents=True, exist_ok=True)
    return diretorio_destino
