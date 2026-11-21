"""Rebuild WGS carrier-profile counts and anonymous Table 1 pup covariates."""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


FAMILIES = ("CBGP8", "GPCB2")


def extract(pdf, workbook, helpers):
    sys.path.insert(0, str(helpers))
    from check_discovery_panel import PDF_SHA, discovery_roster
    from extract_mouse import SHA256, event_rows, native_rows

    original_roster = discovery_roster(pdf)
    text = subprocess.check_output(["pdftotext", "-f", "2", "-l", "2", "-layout", str(pdf), "-"], text=True)
    roster = {}
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] in original_roster:
            pup = fields[0]
            family, code = pup.split("_")
            litter = int(re.fullmatch(r"(\d+)[a-z]", code).group(1))
            sex, coverage = fields[-3], int(fields[-1])
            if sex not in {"M", "F"} or pup in roster or coverage <= 0:
                raise ValueError("Unexpected Table 1 roster row")
            roster[pup] = dict(family=family, litter=litter, sex=sex, wgs_depth=coverage)
    if set(roster) != original_roster:
        raise ValueError("Table 1 covariates failed roster reconciliation")
    names = {f: sorted((p for p, row in roster.items() if row["family"] == f),
                       key=lambda p: (roster[p]["litter"], p)) for f in FAMILIES}
    patterns = {f: Counter() for f in FAMILIES}
    for row, _ in event_rows(native_rows(workbook)):
        recorded = {token.strip().removesuffix("T") for token in row[5].split(",")}
        family, = {p.split("_")[0] for p in recorded}
        if family not in patterns:
            continue
        pattern = "".join("1" if p in recorded else "0" for p in names[family])
        if "1" not in pattern:
            raise ValueError("Validated event lacks a recorded WGS carrier")
        patterns[family][pattern] += 1
    expected = {"CBGP8": 172, "GPCB2": 216}
    if any(sum(patterns[f].values()) != expected[f] or len(names[f]) != 10 for f in FAMILIES):
        raise ValueError("Event or WGS roster size differs from the audited source")
    return {
        "table1_pdf_sha256": PDF_SHA,
        "data1_xlsx_sha256": SHA256,
        "families": {f: {
            "pups_in_bit_order": [{k: v for k, v in roster[p].items() if k != "family"} for p in names[f]],
            "recorded_carrier_pattern_counts": dict(sorted(patterns[f].items())),
        } for f in FAMILIES},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("helpers", type=Path, help="path to research/pedigree_timing/mouse")
    args = parser.parse_args()
    print(json.dumps(extract(args.pdf, args.workbook, args.helpers), indent=2))
