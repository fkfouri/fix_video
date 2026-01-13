import shutil
import subprocess
from pathlib import Path

from PIL import Image

from ..library import limpar_e_normalizar_nome_arquivo
from ..setup import JPEG_QUALITY, PNG_QUALITY, REMOVE


def fix_image(input_path: Path, output_dir: Path, **kwargs):
    """
    Compress image
    """
    clean_name = input_path.stem
    ext = input_path.suffix.lower()
    _set_date = kwargs.get("set_date", True)

    _out_name = []

    if _set_date:
        clean_name = limpar_e_normalizar_nome_arquivo(input_path)
        _out_name.append(clean_name)

        # if has_date_in_filename(input_path):
        #     clean_name = remover_data_do_arquivo(clean_name).strip()
        #     if len(clean_name) <= 0:
        #         clean_name = f"image_{kwargs.get('index'):04d}"

        # _out_name.append(clean_name)
        # _out_name.append(get_early_time(input_path))
    else:
        _out_name.append(clean_name)

    new_name = f"{"_".join(_out_name)}"
    output_path = output_dir / new_name

    remove_original = kwargs.get("remove_original", REMOVE)

    if ext in (".jpg", ".jpeg"):
        compress_jpeg(input_path, output_path)
    elif ext == ".png":
        compress_png(input_path, output_path)
    else:
        raise ValueError(f"Formato não suportado: {ext}")

    # cmd = [
    #     "magick",
    #     str(input_path),
    #     "-auto-orient",
    # ]

    # if input_path.suffix.lower() in [".jpg", ".jpeg"]:
    #     cmd += ["-quality", str(JPEG_QUALITY)]
    # elif input_path.suffix.lower() == ".png":
    #     cmd += ["-quality", str(PNG_QUALITY)]

    # cmd.append(str(output_path))

    # subprocess.run(cmd, check=True)

    if remove_original:
        input_path.unlink(missing_ok=True)


def has_binary(name: str) -> bool:
    # return False
    return shutil.which(name) is not None


def compress_jpeg(input_path: Path, output_path: Path):
    if has_binary("cjpeg-static"):
        subprocess.run(
            [
                "cjpeg-static",
                "-quality",
                str(JPEG_QUALITY),
                "-sample",
                "2x2",  # 4:2:0
                "-optimize",
                "-progressive",
                "-outfile",
                str(output_path),
                str(input_path),
            ],
            check=True,
        )
    else:
        img = Image.open(input_path)
        img.save(
            output_path,
            format="JPEG",
            optimize=True,
            quality=JPEG_QUALITY,
            progressive=True,
            subsampling=2,
            # subsampling="4:2:0"
        )


def compress_png(input_path: Path, output_path: Path):
    if has_binary("pngquant"):
        subprocess.run(
            ["pngquant", "--quality", PNG_QUALITY, "--output", str(output_path), "--force", str(input_path)], check=True
        )
    else:
        img = Image.open(input_path)
        img.save(output_path, optimize=True)
