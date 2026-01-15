import subprocess
from datetime import datetime
from pathlib import Path
from time import time

from ..library import build_metadata_args, insert_line_at_report, limpar_e_normalizar_nome_arquivo
from ..setup import BIT_RATE, CUSTOM_METADATA, FIX_FLAG, FIX_TYPE, REMOVE, REPORT_COMPRESS, SPEED_UP


def fix_video_using_ffmpeg(input_dir: Path, output_dir, mode, **kwargs):
    """
    TODO: fazer a quantidade de quadros por segundo
    """
    clean_name = input_dir.stem.replace(".fix", "")
    ext = input_dir.suffix.lower()
    _set_date = kwargs.get("set_date", True)

    _out_name = []

    if _set_date:
        clean_name = limpar_e_normalizar_nome_arquivo(input_dir)

    _out_name.append(clean_name)
    _out_name.append(FIX_FLAG(mode))

    new_name = f"{"_".join(_out_name)}{ext}"

    # new_name = f"{clean_name}{FIX_FLAG(mode)}{ext}"

    untrunc_name = f"{clean_name}.mp4_fixed{ext}"
    untrunc_file = output_dir / untrunc_name
    untrunc_file.unlink(missing_ok=True)

    out_f = output_dir / new_name

    remove_original = kwargs.get("remove_original", REMOVE)
    speed_factor = kwargs.get("speed_factor", None)
    bit_rate = kwargs.get("bit_rate", BIT_RATE)
    info = kwargs.get("info", {})
    original_bit_rate = int(info.get("format", {}).get("bit_rate", 1)) // 1000

    base_cmd = ["ffmpeg", "-y"]  # -y = sobrescreve sem perguntar

    run_cmd = []

    if mode == "fix":

        if len(info) > 0:
            # Apenas correção de erros → stream copy (sem reencodar)
            cmd = (
                base_cmd
                + [
                    "-err_detect",
                    "ignore_err",
                    "-i",
                    str(input_dir),
                    "-c",
                    "copy",  # sem reencodar
                ]
                + build_metadata_args("Processed - Fixed", CUSTOM_METADATA)
                + [str(out_f)]
            )
            run_cmd.append(cmd)
        else:
            reference_file = kwargs.get("reference_file", None)

            cmd = [
                "untrunc",
                str(reference_file),
                str(input_dir),
            ]

            mode = "untrunc"
            run_cmd.append(cmd)

            # Reencoda e sincroniza áudio/vídeo
            # ffmpeg -fflags +genpts -i video_fixed.mp4 -map 0:v -map 0:a? -c:v libx264 -c:a aac video_sync.mp4
            # ffmpeg -fflags +genpts -i video_fixed.mp4 -map 0:v -map 0:a? -c:v copy -c:a copy video_sync.mp4
            # ffmpeg -itsoffset -0.8 -i video_fixed.mp4 -map 0:v -map 1:a -c copy video_sync.mp4

            cmd = (
                base_cmd
                + [
                    "-fflags",
                    "+genpts",
                    "-i",
                    str(untrunc_file),
                    "-map",
                    "0:v",
                    "-map",
                    "0:a?",
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                ]
                + build_metadata_args("Processed - Untrunced and fixed", CUSTOM_METADATA)
                + [str(out_f)]
            )
            run_cmd.append(cmd)

    elif mode in ["compress", "up"]:
        # Reencoda com compressão + aceleração + metadados
        speed_up = SPEED_UP(speed_factor) if mode == "up" else []
        new_bit_rate = get_video_bit_rate(bit_rate, original_bit_rate)

        if mode == "up":
            what = f"Processed - Acelerado {speed_factor}× com FFmpeg (setpts + atempo)"
        else:
            what = f"Processed - Compress from {original_bit_rate}k to {new_bit_rate}k"

        args = build_metadata_args(what=what, metadata=CUSTOM_METADATA)

        cmd = (
            base_cmd
            + [
                "-i",
                str(input_dir),
                # "-r",
                # "24",  # força 24 fps
                "-b:v",
                new_bit_rate,
                "-b:a",
                "128k",
                "-ar",
                "44100",
            ]
            + speed_up
            + args
            + [str(out_f)]
        )
        run_cmd.append(cmd)
    elif FIX_TYPE == "convert":
        ...
        # Converte MOV (ou qualquer) → .mpeg (H.264/AAC)
        # cmd += ["-i", str(infile)]
        # cmd += ["-c:v", "libx264", "-crf", "23", "-preset", "medium"]
        # cmd += ["-c:a", "aac", "-b:a", "128k", "-vf", "format=yuv420p"]
        # cmd += get_metadata() + [str(outfile)]
        # run_cmd.append(cmd)
    else:
        raise ValueError("FIX_TYPE deve ser 'error' ou 'compress'")

    start_time_iso = datetime.now().isoformat()
    start = time()

    for cmd in run_cmd:
        exit_code = subprocess.call(cmd)

    print(f"\n🟢🟢 fixed video:{input_dir}, output: {out_f}, exist_code: {exit_code}🟢🟢\n\n")
    out_f = Path(out_f)

    finish_time_iso = datetime.now().isoformat()
    finised = time()

    delta = finised - start
    minutes, seconds = divmod(delta, 60)
    processing_time = f"{int(minutes):02d}:{int(seconds):02d}"

    report = {
        "original": "/".join(input_dir.parts[-4:]),
        "original_size_mb": f"{input_dir.stat().st_size / 1024**2:.2f}",
        "final": "/".join(out_f.parts[-4:]),
        "final_size_mb": f"{out_f.stat().st_size / 1024**2:.2f}",
        "start_time": start_time_iso,
        "finish_time": finish_time_iso,
        "processing_time": f"{processing_time} (MM:SS)",
        "fix_type": mode,
        "speed_applied": "1.75x" if FIX_TYPE == "compress" else "none",
        "metadata_added": "yes",
        "cmd_executed": " ".join(cmd),
    }

    insert_line_at_report(REPORT_COMPRESS, report)

    if remove_original:
        input_dir.unlink(missing_ok=True)
    untrunc_file.unlink(missing_ok=True)


def get_video_bit_rate(bit_rate, original_bit_rate) -> str:
    """Retorna a taxa de bits do vídeo em kbps como string formatada para FFmpeg (ex: '400k')"""
    # bit_rate = info.get("format", {}).get("bit_rate", None)
    # if bit_rate is None:
    #     raise ValueError("Taxa de bits não encontrada nas informações do vídeo.")

    # kbps = int(bit_rate) // 1000
    # return f"{kbps}k"

    if bit_rate > 1:
        new_bit_rate = f"{int(bit_rate)}k"
    else:
        value = original_bit_rate * bit_rate // 1
        new_bit_rate = f"{int(value)}k"
    return new_bit_rate
