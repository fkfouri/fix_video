from pathlib import Path


def build_metadata_args(what="", metadata={}) -> list:
    """Converte o dicionário CUSTOM_METADATA em argumentos do FFmpeg"""
    args = []
    for key, value in metadata.items():
        if key not in ["genre"]:  # genre será adicionado separadamente
            args.extend(["-metadata", f"{key}={value}"])

    args.extend(["-metadata", f"genre={what}".strip()])
    return args


def define_destination_directory(original_file: Path, origem: Path, destino: Path) -> Path:
    """Define o diretório de destino mantendo a estrutura de pastas relativa."""
    _root_reference_size_ = len(origem.parts)

    if destino.is_file():
        destino_base = destino.parent
    else:
        destino_base = destino

    #     raise ValueError("Destino não pode ser um arquivo quando se define diretório de destino para vídeos.")

    if len(original_file.parts) == _root_reference_size_ + 1:
        diretorio_destino = destino_base
    else:
        diretorio_destino = destino_base / Path(*original_file.parts[_root_reference_size_:-1])

    diretorio_destino.mkdir(parents=True, exist_ok=True)
    return diretorio_destino


def bytes_to_kbytes(size_in_bytes: int) -> str:
    """
    Converte qualquer tamanho em bytes para string em kilobytes (k),
    com até 1 casa decimal quando necessário.
    Ex: 400000 → '400k'
    """
    if size_in_bytes < 0:
        raise ValueError("Tamanho não pode ser negativo")

    # Converte para kilobytes (1 kB = 1000 bytes, padrão mais comum em ferramentas como ffprobe)
    kb = size_in_bytes / 1000.0

    # Se for número inteiro, remove o .0
    if kb == int(kb):
        return f"{int(kb)}k"
    else:
        # Arredonda para 1 casa decimal (ex: 1234.56 → 1.2k? Não, mantém precisão razoável)
        # Mas para valores grandes, 1 casa é suficiente
        return f"{round(kb, 1)}k"
