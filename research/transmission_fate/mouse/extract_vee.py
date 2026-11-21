"""Emit deidentified parental VEE candidates from Lindsay et al. Supplementary Table 3."""

import argparse
import csv
import hashlib
import re
import subprocess
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

PDF_SHA256 = "c9a6d54c936e93c3c6202b40a294cfef4fc1fc17eb17a10505f5d6435061f27c"
HEADER = (
    "site_id", "pedigree", "parent", "validation", "assayed_offspring", "carrier_offspring",
    "reported_transmission_fraction", "reported_offspring_vaf", "parental_vaf",
)


def extract(pdf):
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != PDF_SHA256:
        raise ValueError("Expected Lindsay et al. Supplementary Information PDF (MOESM1)")
    text = subprocess.check_output(
        ["pdftotext", "-layout", "-f", "6", "-l", "7", str(pdf), "-"], encoding="utf-8"
    )
    table_page, caption_page = text.split("\f")[:2]
    if "Supplementary Table 3: Quantification of VEE mutations to the germline" not in caption_page:
        raise ValueError("Supplementary Table 3 caption missing")
    rows = []
    identities = set()
    for line in table_page.splitlines():
        if not re.match(r"^\s*\d+", line):
            continue
        chrom, pos, ref, alt, pedigree, parent, status, assayed, carriers, rate, child_vaf, vaf = line.split()
        identity = (pedigree, chrom, pos, ref, alt)
        if identity in identities:
            raise ValueError("Duplicate Table 3 site")
        identities.add(identity)
        if status not in {"PASS", "FAIL"} or parent not in {"Father", "Mother"}:
            raise ValueError("Unexpected status or parental label")
        values = (assayed, carriers, rate, child_vaf, vaf)
        if "NA" in values:
            if status != "FAIL" or set(values) != {"NA"}:
                raise ValueError("Unexpected pattern of missing fields")
        else:
            if not 0 <= int(carriers) <= int(assayed) or int(assayed) == 0:
                raise ValueError("Invalid offspring counts")
            if not all(0 <= Decimal(value) <= 1 for value in (rate, child_vaf, vaf)):
                raise ValueError("Expected proportions")
            # The source rounds its transmission fractions to two decimals.
            if abs(Decimal(carriers) / Decimal(assayed) - Decimal(rate)) > Decimal("0.005"):
                raise ValueError("Reported transmission fraction inconsistent with counts")
        rows.append((f"V{len(rows) + 1:02d}", pedigree, parent, status, *values))
    if Counter(row[3] for row in rows) != {"PASS": 26, "FAIL": 14}:
        raise ValueError("Unexpected Table 3 validation tally")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("supplementary_pdf", type=Path)
    arguments = parser.parse_args()
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(HEADER)
    writer.writerows(extract(arguments.supplementary_pdf))
