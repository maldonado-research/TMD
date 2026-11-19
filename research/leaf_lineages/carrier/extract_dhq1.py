"""Transcribe the DHQ1 rows from one Wang et al. S1 or S2 Data worksheet."""
import argparse
import csv
from decimal import Decimal
from pathlib import Path
import sys

WANG_S1 = ("Species", "Individual ID", "Tissue", "Sample ID", "Total Reads", "Clean Data (G)",
           "Clean Depth", "Mapped Depth (Mapping Quality ≥ 20)", "Genome (%) covered by reads ≥ 5")
WANG_S2 = ("Species", "Individual", "Chromosome", "Position", "Samples", "Mutation Type", "Predicted Effect")
OUTPUT = {"s1": ("sample_id", "mapped_depth", "genome_pct_depth_at_least_five"),
          "s2": ("chromosome", "position", "change", "listed_leaves")}


def read_rows(path):
    if path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            for sheet in book.worksheets:
                yield from sheet.values
        finally:
            book.close()
    else:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.startswith("|"):
                    yield [v.strip().replace(r"\_", "_") for v in line.strip().strip("|").split("|")]


def decimal_text(value):
    number = Decimal(str(value).strip())
    return format(number.normalize(), "f")


def extract(path, source):
    header = WANG_S1 if source == "s1" else WANG_S2
    observed_header = False
    output = []
    for row in read_rows(path):
        if tuple(row[:len(header)]) == header:
            observed_header = True
        if tuple(row[:2]) != ("Prunus persica", "DHQ1"):
            continue
        if not observed_header:
            raise ValueError("Source column labels differ or DHQ1 rows precede the expected header.")
        if source == "s1":
            if row[2] != "Leaf":
                raise ValueError("Unexpected tissue under DHQ1.")
            output.append((row[3], decimal_text(row[7]), decimal_text(row[8])))
        else:
            output.append((row[2], str(int(row[3])), row[5], row[4]))
    size = 75 if source == "s1" else 48
    if len(output) != size:
        raise ValueError(f"Expected {size} DHQ1 rows, found {len(output)}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=OUTPUT)
    parser.add_argument("table", type=Path, help="an original XLSX file or publisher table rendering in Markdown")
    args = parser.parse_args()
    rows = extract(args.table, args.source)
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(OUTPUT[args.source])
    writer.writerows(rows)
