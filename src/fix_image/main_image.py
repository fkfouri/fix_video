from datetime import datetime
from pathlib import Path

import click
from tqdm import tqdm

from . import __version__
from .setup import ACTUAL_PATH
from .support import fix_image, image_list

# from .support import library, report, video_fix, video_info, video_list

TOTAL_FILES = 0


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
@click.option(
    "-nr",
    "--no-remove",
    is_flag=True,
    help="No allow removal of original files after processing.",
)
def main(source, no_remove):
    """
    Fix image files with EXIF data.

    SOURCE is the path to the file or directory to be processed.
    """
    global TOTAL_FILES
    print(f"\n🚀🚀 Fix Image v{__version__} 🚀🚀")

    if source == ".":
        ORIGEM = ACTUAL_PATH
        DESTINO = ACTUAL_PATH
    else:
        ORIGEM = Path(source)
        DESTINO = Path(source)

    kwargs = {
        "remove_original": not no_remove,
    }

    print(f"Started at {datetime.now().isoformat()}\n in the source path: {ORIGEM}\n")

    files = image_list.list_image_in_directory(ORIGEM)

    for file in tqdm(files):
        if file.is_file():
            print(f"Processing file: {file}")
            try:
                fix_image(file, DESTINO, **kwargs)
                TOTAL_FILES += 1
            except Exception as e:
                print(f"❌❌ Error processing file {file}: {e} ❌❌")
