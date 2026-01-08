from datetime import datetime
from pathlib import Path

import click
from tqdm import tqdm

from . import __version__
from .setup import ACTUAL_PATH, REPORT_ERROR, REPORT_FFPROBE
from .support import library, report, video_fix, video_info, video_list

TOTAL_FILES = 0


@click.command()
@click.version_option(version=__version__, prog_name="fix-video")
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
    help="Choose the mode: up, fix or compress. Default is up.",
)
@click.option(
    "-nr",
    "--no-remove",
    is_flag=True,
    help="No allow removal of original files after processing.",
)
def main(source, mode, no_remove):
    """
    Fix and optimize video files using FFmpeg.

    SOURCE is the path to the file or directory to be processed.
    """
    global TOTAL_FILES
    print(f"\n🚀🚀 Fix Video v{__version__} 🚀🚀")

    if source == ".":
        ORIGEM = ACTUAL_PATH
        DESTINO = ACTUAL_PATH
    else:
        ORIGEM = Path(source)
        DESTINO = Path(source)

    remove_original = not no_remove

    print(f"Started at {datetime.now().isoformat()}\nRunning in mode: {mode} at path: {ORIGEM}\n")

    video_files = video_list.list_videos_in_directory(ORIGEM)

    for file in tqdm(video_files):
        info = {}
        if file.is_file():
            try:
                info = video_info.get_video_info(file)

                if video_info.video_should_be_processed(info, file.name) is False:
                    print(f"⏭️ ⏭️  Skipping already processed file: {file} ⏭️ ⏭️ ")
                    continue

                report.insert_line_at_report(REPORT_FFPROBE, info)
                diretorio_destino = library.define_destination_directory(file, ORIGEM, DESTINO)

                video_fix.fix_video_using_ffmpeg(file, diretorio_destino, mode=mode, remove_original=remove_original)
                TOTAL_FILES += 1
            except Exception as e:
                print(f"❌❌ Error processing file {file}: {e} ❌❌")
                report.insert_line_at_report(REPORT_ERROR, {"file": str(file), "error": str(e)})

    print(f"\n✅✅ All done! ✅✅\nTotal Files: {TOTAL_FILES}\nFinished at {datetime.now().isoformat()}")
    print(f"Run from path: {ACTUAL_PATH}\n\n")
