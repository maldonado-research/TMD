"""Compare sharing on the two large WGS-discovery panels with their full targeted carrier lists.

Requires Python 3.9+ and pdftotext from Poppler. The native main supplement (MOESM1)
and Supplementary Data 1 (MOESM5) are the only inputs.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

from extract_mouse import SHA256, event_rows, native_rows

PDF_SHA = "c9a6d54c936e93c3c6202b40a294cfef4fc1fc17eb17a10505f5d6435061f27c"
FAMILIES = ("CBGP8", "GPCB2")


def discovery_roster(pdf):
    if sha256(pdf.read_bytes()).hexdigest() != PDF_SHA:
        raise ValueError("Input differs from the original supplement")
    # The roster fills the second PDF page. Its caption on page 3 identifies Table 1.
    text = subprocess.check_output(["pdftotext", "-layout", "-f", "2", "-l", "3", str(pdf), "-"],
                                   encoding="utf-8")
    first, caption, *_ = text.split("\f")
    assert "Supplementary Table 1: Mouse DNM counts." in caption
    ids = re.findall(r"^\s*((?:CBGP|GPCB)\d+_\d+[a-z])\s+\d+\s+\d+", first, re.M)
    assert len(ids) == len(set(ids)) == 40
    groups = Counter(s.split("_")[0] for s in ids)
    assert len(groups) == 6 and all(groups[f] == 10 for f in FAMILIES)
    return set(ids)


def analyze(pdf, workbook):
    discovery = discovery_roster(pdf)
    datasets = {fam:Counter() for fam in FAMILIES}
    for row, bases in event_rows(native_rows(workbook)):
        pups = {name.strip().removesuffix("T") for name in row[5].split(",")}
        fam = next(iter(pups)).split("_")[0]
        assert all(p.split("_")[0] == fam for p in pups)
        if fam not in datasets:
            continue
        n_discovery = len(pups & discovery)
        assert n_discovery >= 1
        counts = datasets[fam]
        counts["events"] += 1
        counts["shared_in_discovery_subset"] += n_discovery >= 2
        counts["shared_in_full_targeted_panel"] += len(pups) >= 2
        new = n_discovery == 1 and len(pups) >= 2
        counts["additional_shared_events"] += new
        counts["additional_shared_events_with_no_parent_somatic_signal"] += new and row[8] == "0"
    return {"workbook_sha256": SHA256, "supplementary_pdf_sha256": PDF_SHA,
            "number_of_discovery_pups_across_six_pedigrees": len(discovery),
            "number_of_discovery_pups_in_the_two_large_pedigrees": 20,
            "two_large_pedigrees": dict(sum(datasets.values(), Counter())),
            "each_large_pedigree": {fam:dict(c) for fam,c in datasets.items()}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("supplementary_pdf", type=Path)
    ap.add_argument("supplementary_data_1", type=Path)
    args = ap.parse_args()
    print(json.dumps(analyze(args.supplementary_pdf, args.supplementary_data_1), indent=2))
