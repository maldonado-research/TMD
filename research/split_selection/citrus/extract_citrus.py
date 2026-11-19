"""Extract the location-matched percentages from a text rendering of Tables S3–S5."""
import argparse
import csv
from decimal import Decimal
from pathlib import Path
import re
import sys


PAIRS = ("6A1", "6A2", "6B1", "6B2", "7A1", "7B1")
CLASSES = ("clonal", "mosaic", "leaf-specific")
FIELDS = ("original_row", "repeat_pair", "category", "depth_1", "depth_2",
          "repeat_1_pct", "repeat_2_pct", "union_pct")


def read_tables(text):
    """Accept a layout-preserving PDF text export or a pipe-delimited table rendering."""
    depths = {}
    matrices = {}
    section = category = None
    for line in text.splitlines():
        line = line.strip().strip("|").strip().replace("**", "").replace("\\_", "_")
        line = " ".join(line.replace("|", " ").split())
        table = re.match(r"Table S([3456])\.", line)
        if table:
            section = int(table[1])
            category = None
            continue
        if section == 3:
            row = re.fullmatch(r"([12])_([67][AB][12]) [67] (?:apical|basal) [12] ([12]) (\d+\.\d+)", line)
            if row:
                repeat, pair, replicate, depth = row.groups()
                if repeat != replicate or (pair, repeat) in depths:
                    raise ValueError(f"Ambiguous depth row: {line}")
                depths[pair, repeat] = Decimal(depth)
        if section in (4, 5):
            if line.lower().rstrip(":") in CLASSES:
                category = line.lower().rstrip(":")
                continue
            values = line.split()
            if values and values[0] in ("6A", "6B", "7A", "7B") and category:
                numbers = [int(value) for value in values[1:]]
                key = section, category, values[0]
                if len(numbers) != {4: 12, 5: 6}[section] or key in matrices:
                    raise ValueError(f"Unexpected percent row: {line}")
                matrices[key] = numbers
    if len(depths) != 12 or len(matrices) != 24:
        raise ValueError("Expected 12 depth records and 24 complete matrix rows.")
    rows = []
    for i, pair in enumerate(PAIRS):
        group = pair[:2]
        for category in CLASSES:
            one, two = matrices[4, category, group][2*i:2*i+2]
            rows.append((group, pair, category, depths[pair, "1"], depths[pair, "2"],
                         one, two, matrices[5, category, group][i]))
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tables", type=Path)
    text = parser.parse_args().tables.read_text()
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(FIELDS)
    writer.writerows(read_tables(text))
