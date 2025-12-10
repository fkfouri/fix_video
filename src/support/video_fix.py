import subprocess
from datetime import datetime
from pathlib import Path
from time import time

from setup import FIX_FLAG, FIX_TYPE, REMOVE, REPORT_COMPRESS, SPEED_UP

from .library import build_metadata_args
from .report import insert_line_at_report


def fix_video_using_ffmpeg(original_file: Path, output_dir):
    clean_name = original_file.stem.replace(".fix", "")
    new_name = f"{clean_name}{FIX_FLAG}{original_file.suffix}"
    out_f = output_dir / new_name

    base_cmd = ["ffmpeg", "-y"]  # -y = sobrescreve sem perguntar

    if FIX_TYPE == "error":
        # Apenas correção de erros → stream copy (sem reencodar)
        cmd = (
            base_cmd
            + [
                "-err_detect",
                "ignore_err",
                "-i",
                str(original_file),
                "-c",
                "copy",  # sem reencodar
            ]
            + build_metadata_args()
            + [str(out_f)]
        )

    elif FIX_TYPE == "compress":
        # Reencoda com compressão + aceleração + metadados
        cmd = (
            base_cmd
            + [
                "-i",
                str(original_file),
                "-r",
                "24",  # força 24 fps
                "-b:v",
                "400k",
                "-b:a",
                "128k",
                "-ar",
                "44100",
            ]
            + SPEED_UP
            + build_metadata_args()
            + [str(out_f)]
        )
    elif FIX_TYPE == "convert":
        ...
        # Converte MOV (ou qualquer) → .mpeg (H.264/AAC)
        # cmd += ["-i", str(infile)]
        # cmd += ["-c:v", "libx264", "-crf", "23", "-preset", "medium"]
        # cmd += ["-c:a", "aac", "-b:a", "128k", "-vf", "format=yuv420p"]
        # cmd += get_metadata() + [str(outfile)]

    else:
        raise ValueError("FIX_TYPE deve ser 'error' ou 'compress'")

    start_time_iso = datetime.now().isoformat()
    start = time.time()

    exit_code = subprocess.call(cmd)
    print(f"\n🟢🟢 fixed video:{original_file}, output: {out_f}, exist_code: {exit_code}🟢🟢\n\n")
    out_f = Path(out_f)

    finish_time_iso = datetime.now().isoformat()
    finised = time.time()

    delta = finised - start
    minutes, seconds = divmod(delta, 60)
    processing_time = f"{int(minutes):02d}:{int(seconds):02d}"

    report = {
        "original": "/".join(original_file.parts[-4:]),
        "original_size_mb": f"{original_file.stat().st_size / 1024**2:.2f}",
        "final": "/".join(out_f.parts[-4:]),
        "final_size_mb": f"{out_f.stat().st_size / 1024**2:.2f}",
        "start_time": start_time_iso,
        "finish_time": finish_time_iso,
        "processing_time": f"{processing_time} (MM:SS)",
        "fix_type": FIX_TYPE,
        "speed_applied": "1.75x" if FIX_TYPE == "compress" else "none",
        "metadata_added": "yes",
    }

    global TOTAL_FILES
    TOTAL_FILES += 1
    insert_line_at_report(REPORT_COMPRESS, report)
    if REMOVE:
        original_file.unlink()
