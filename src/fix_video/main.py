from datetime import datetime
from pathlib import Path

import click
from tqdm import tqdm

from . import __version__
from .library import library, report
from .setup import ACTUAL_PATH, REPORT_ERROR, REPORT_FFPROBE
from .support import video_fix, video_info, video_list

TOTAL_FILES = 0


@click.command(
    help=(
        f"Fix and optimize video files using FFmpeg. (v{__version__})\n\n"
        "SOURCE is the path to the file or directory to be processed."
    )
)
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
    "--reference_file",
    "-ref",
    type=click.Path(
        exists=True,  # deve existir
        file_okay=True,  # permite arquivos
        dir_okay=False,  # permite diretórios
        path_type=str,  # retorna como str (Python 3.6+ recomenda str em vez de Path)
    ),
    required=False,
    default=None,
    help="Reference para untrunc",
)
@click.option(
    "-sd",
    "--set-date",
    is_flag=True,
    default=False,
    help="Set the date of the image.",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["up", "fix", "compress"], case_sensitive=False),
    required=False,
    default="up",
    help="Choose the mode: up, fix or compress. Default is up.",
)
@click.option(
    "-nr",
    "--no-remove",
    is_flag=True,
    help="No allow removal of original files after processing.",
)
@click.option(
    "-r",
    "--rate",
    type=float,
    default=1.75,
    help='Valor de aceleração para o modo "up" (1.75x)',
)
@click.option(
    "-br",
    "--bit-rate",
    type=float,
    default=400,
    help='Taxa de bits alvo em kbps para o modo "compress" (400k)',
)
def main(source, mode, no_remove, rate, bit_rate, reference_file, set_date):
    global TOTAL_FILES
    print(f"\n🚀🚀 Fix Video v{__version__} 🚀🚀")

    if source == ".":
        ORIGEM = ACTUAL_PATH
        DESTINO = ACTUAL_PATH
    else:
        ORIGEM = Path(source)
        DESTINO = Path(source)

    _ref = None
    if reference_file is not None:
        _ref = Path(reference_file)

    kwargs = {
        "speed_factor": rate,
        "bit_rate": bit_rate,
        "remove_original": not no_remove,
        "reference_file": _ref,
        "set_date": set_date,
    }

    print(f"Started at {datetime.now().isoformat()}\nRunning in mode: {mode} at path: {ORIGEM}\n")

    video_files = video_list.list_videos_in_directory(ORIGEM)

    for file in tqdm(video_files):
        info = {}

        if file.is_file():
            if file == _ref:
                # Ignoring reference
                continue
            try:
                info = video_info.get_video_info(file)
                kwargs["info"] = info

                if video_info.video_should_be_processed(info, file.name) is False:
                    print(f"⏭️ ⏭️  Skipping already processed file: {file} ⏭️ ⏭️ ")
                    continue

                report.insert_line_at_report(REPORT_FFPROBE, info)
                diretorio_destino = library.define_destination_directory(file, ORIGEM, DESTINO)

                video_fix.fix_video_using_ffmpeg(file, diretorio_destino, mode=mode, **kwargs)
                TOTAL_FILES += 1
            except Exception as e:
                print(f"❌❌ Error processing file {file}: {e} ❌❌")
                report.insert_line_at_report(REPORT_ERROR, {"file": str(file), "error": str(e)})

    print(f"\n✅✅ All done! ✅✅\nTotal Files: {TOTAL_FILES}\nFinished at {datetime.now().isoformat()}")
    print(f"Run from path: {ACTUAL_PATH}\n\n")
