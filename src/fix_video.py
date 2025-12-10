from datetime import datetime

from tqdm import tqdm

from setup import __THIS_PATH__, ACTUAL_PATH, DESTINO, ORIGEM, REPORT_FFPROBE
from support import library, report, video_fix, video_info, video_list

TOTAL_FILES = 0


if __name__ == "__main__":
    print(f"Você está executando de: {ACTUAL_PATH}")
    print(f"O executável está em: {__THIS_PATH__}")

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

            video_fix.fix_video_using_ffmpeg(file, diretorio_destino)
            TOTAL_FILES += 1

print(f"\n✅✅ All done! ✅✅\n Total Files: {TOTAL_FILES}\n Finished at {datetime.now().isoformat()}\n\n")
