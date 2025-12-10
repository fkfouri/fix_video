from datetime import datetime
from pathlib import Path

import click
from tqdm import tqdm

from .setup import __THIS_PATH__, ACTUAL_PATH, REPORT_FFPROBE
from .support import library, report, video_fix, video_info, video_list

TOTAL_FILES = 0


@click.command()
@click.argument(
    "source",
    metavar="SOURCE",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=str),
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["up", "fix", "compress"], case_sensitive=False),
    required=False,
    default="up",
    help="Escolha o modo: up, fix ou compress. Default é up.",
)
def main(source, mode):
    """
    Caminho a ser processado.

    SOURCE é o arquivo ou diretório de entrada.
    """
    global TOTAL_FILES

    print(f"Você está executando de: {ACTUAL_PATH}")
    print(f"O executável está em: {__THIS_PATH__}")

    if source == ".":
        ORIGEM = ACTUAL_PATH
        DESTINO = ACTUAL_PATH
    else:
        ORIGEM = Path(source)
        DESTINO = Path(source)

    video_files = video_list.list_videos_in_directory(ORIGEM)

    for file in tqdm(video_files):
        info = {}
        if file.is_file():
            info = video_info.get_video_info(file)

            if video_info.video_should_be_processed(info, file.name) is False:
                print(f"⏭️ ⏭️  Skipping already processed file: {file} ⏭️ ⏭️ ")
                continue

            report.insert_line_at_report(REPORT_FFPROBE, info)
            diretorio_destino = library.define_destination_directory(file, ORIGEM, DESTINO)

            video_fix.fix_video_using_ffmpeg(file, diretorio_destino, mode=mode)
            TOTAL_FILES += 1


if __name__ == "__main__":
    main()

    print(f"\n✅✅ All done! ✅✅\n Total Files: {TOTAL_FILES}\n Finished at {datetime.now().isoformat()}\n\n")
