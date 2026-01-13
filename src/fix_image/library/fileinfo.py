import re
from datetime import datetime
from pathlib import Path

from ..setup import DATE_STANDARD


def get_early_time(file_path: Path):
    """
    Retorna as datas de criação e modificação de um arquivo.
    """
    stat_info = file_path.stat()
    date_from_name = get_date_from_filename(file_path)
    if date_from_name is None:
        date_from_name = datetime.now()
    creation_time = datetime.fromtimestamp(stat_info.st_birthtime)
    modification_time = datetime.fromtimestamp(stat_info.st_mtime)
    access_time = datetime.fromtimestamp(stat_info.st_atime)

    # Encontra a data mais antiga
    min_date = min(creation_time, modification_time, access_time, date_from_name)
    return min_date.strftime(DATE_STANDARD)


def has_date_in_filename(file_path: Path) -> bool:
    return bool(get_date_from_filename(file_path))


def get_date_from_filename(file_path: Path):
    """
    Tenta extrair uma data do nome do arquivo no formato YYYYMMDD.
    Retorna None se não encontrar.
    """
    name = file_path.stem
    # yyyy-mm-dd
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", name)
    if match:
        try:
            data = datetime.strptime(match.group(0), "%Y-%m-%d")
            return data
        except ValueError:
            pass

    # yyyymmdd
    match = re.search(r"(\d{8})", name)
    if match:
        try:
            data = datetime.strptime(match.group(0), "%Y%m%d")
            return data
        except ValueError:
            pass

    # dd-mm-yy
    match = re.search(r"(\d{2})-(\d{2})-(\d{2})", name)
    if match:
        try:
            data = datetime.strptime(match.group(0), "%d-%m-%y")
            return data
        except ValueError:
            pass

    return None
