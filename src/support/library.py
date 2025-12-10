from setup import CUSTOM_METADATA


def build_metadata_args() -> list:
    """Converte o dicionário CUSTOM_METADATA em argumentos do FFmpeg"""
    args = []
    for key, value in CUSTOM_METADATA.items():
        args.extend(["-metadata", f"{key}={value}"])
    return args
