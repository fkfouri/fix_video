from pathlib import Path
import os

import click
import whisper

from . import __version__


@click.command()
@click.version_option(version=__version__, prog_name="fix_video")
@click.argument(
    "source",
    metavar="SOURCE",
    required=False,
    default=".",
    type=click.Path(
        exists=True,  # deve existir
        file_okay=True,  # permite arquivos
        dir_okay=True,  # permite diretórios
        # readable=True,        # opcional: deve ser legível
        path_type=str,  # retorna como str (Python 3.6+ recomenda str em vez de Path)
    ),
)
def main(source):
    """
    Transcript - A tool to generate transcripts from audio and video files.

    """
    # Carrega o modelo (base é rápido; opções: tiny, small, medium, large)
    # model = whisper.load_model("base")

    # C:\Users\<user>\.cache\whisper\base.pt
    model_path = Path(os.path.join(os.path.dirname(__file__), "base.pt"))
    if not model_path.exists():
        model = whisper.load_model("base")

    model = whisper.load_model(model_path)

    in_f = Path(source)
    if not in_f.is_file():
        print(f"❌ O caminho '{source}' não é um arquivo válido. Por favor, forneça um arquivo de áudio ou vídeo.")
        return

    out_f = Path(source).with_suffix(".txt")

    # Transcreve arquivo (ex: MPG ou MP3)
    result = model.transcribe(source, language="pt")  # 'pt' para português

    text = result["text"].strip()  # Remove espaços extras
    out_f.write_text(text, encoding="utf-8")

    print(text)  # Texto transcrito

    print(f"\n🚀🚀 Transcript Video v{__version__} 🚀🚀")
