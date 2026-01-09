import json
from pathlib import Path


def insert_line_at_report(file_report: Path, new_item):
    with open(file_report, "a", encoding="utf-8") as f:
        f.write(json.dumps(new_item, ensure_ascii=False))
        f.write("\n")
