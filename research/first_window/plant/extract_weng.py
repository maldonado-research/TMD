"""Extract line-level counts from the native Weng et al. (2019) Figshare supplements."""
import argparse
import csv
import hashlib
import io
import re
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

CLASSES = ("C>A", "C>G", "C>T", "T>A", "T>C", "T>G")
COMPLEMENT = str.maketrans("ACGT", "TGCA")
ZIP_SHA = "cb2a229257b26013348e9447a19fe2220a6e920b11c30f05430a7ac524ac9ca4"
PDF_SHA = "b1e24da381e9787aa4c87545e1176257ff0e1dd321cd78583c798788983cb79c"
# The printed table omits the closing parenthesis of the shared SNM count for line 111.
TABLE_ROW = re.compile(
    r"^\s*(\d+)(\*?)\s+(\d+)\s*\((\d+)\)\s+(\d+)\s*\((\d+)\)?"
    r"\s+[\d.]+\s+[\d.]+\s+(\d+)\s+[\d.E+-]+\s+[\d.E+-]+\s*$",
    re.MULTILINE,
)


def native_rows(archive, name):
    with archive.open(f"Mutation_list/{name}_mutations.csv") as source:
        return list(csv.DictReader(io.TextIOWrapper(source, encoding="utf-8-sig")))


def read_table(pdf):
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    table_text = text.split("Supplementary Table S1.", 1)[1].split("Supplementary Table S2.", 1)[0]
    table = {}
    for key, star, _, shared_indel, total_snm, shared_snm, accessible in TABLE_ROW.findall(table_text):
        line = int(key)
        if line in table or bool(star) != (int(shared_snm) == 0 and int(shared_indel) == 0):
            raise ValueError(f"Inconsistent table row for line {line}")
        table[line] = (bool(star), int(total_snm) - int(shared_snm), int(accessible))
    if len(table) != 107 or sum(row[0] for row in table.values()) != 48:
        raise ValueError("Table S1 roster or designated subset does not match publication")
    return table


def extract(archive_path, pdf):
    for path, expected in ((archive_path, ZIP_SHA), (pdf, PDF_SHA)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Native file checksum mismatch: {path.name}")
    table = read_table(pdf)
    with zipfile.ZipFile(archive_path) as archive:
        private_rows = native_rows(archive, "Unique")
        shared_rows = native_rows(archive, "Shared")

    counts = defaultdict(Counter)
    statuses = defaultdict(Counter)
    seen = set()
    for row in private_rows:
        if row["Type"] != "SNM":
            continue
        line = int(row["MA_Line"])
        ref, alt = row["REF"], row["ALT"]
        site = (line, row["CHROM"], row["POS"])
        if site in seen:
            raise ValueError(f"Duplicated private SNM in line {line}")
        seen.add(site)
        if ref in ("A", "G"):
            ref, alt = ref.translate(COMPLEMENT), alt.translate(COMPLEMENT)
        category = f"{ref}>{alt}"
        if category not in CLASSES:
            raise ValueError(f"Unclassified private SNM in line {line}")
        status = row["PCR_validation"]
        if status not in ("", "validated", "bad amplification", "rejected"):
            raise ValueError(f"Unknown validation flag in line {line}")
        statuses[line][status] += 1
        if status != "rejected":
            counts[line][category] += 1

    named = set()
    macros = Counter()
    for row in shared_rows:
        if not row["TYPE"]:
            continue
        for column in ("MA_Line1", "MA_Line2", "MA_Line3", "MA_Line4"):
            label = row[column]
            if label.isdecimal():
                named.add(int(label))
            elif label:
                macros[label] += 1
    if macros != {"shared_by_15_lines": 1, "shared_by_56_lines": 1}:
        raise ValueError("Unexpected shared-row labels")
    if set(counts) != set(table) or len(seen) != 1694:
        raise ValueError("Private SNM roster or total mismatch")
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(("line", "table_s1_starred", "named_in_shared_csv", "accessible_sites",
                     "rejected_snm", "inconclusive_snm", *CLASSES))
    for line, (starred, raw_private, accessible) in sorted(table.items()):
        status = statuses[line]
        if status.total() != raw_private:
            raise ValueError(f"Private SNM total disagrees with Table S1 for line {line}")
        writer.writerow((line, int(starred), int(line in named), accessible, status["rejected"],
                         status["bad amplification"], *(counts[line][c] for c in CLASSES)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file_s1", type=Path)
    parser.add_argument("supplement_pdf", type=Path)
    args = parser.parse_args()
    extract(args.file_s1, args.supplement_pdf)
