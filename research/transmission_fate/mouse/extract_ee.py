"""Extract the Lindsay mouse EE panel and the two first-litter WGS cohorts.

Give the source PDF and workbook paths, output directory, and optionally --prior
with the location of the published pedigree_timing/mouse source readers.
"""
import argparse
import csv
import subprocess
import sys
from collections import Counter
from pathlib import Path

FAMILIES = {"CBGP8": (8, 57), "GPCB2": (9, 77)}


def parse_table2(pdf):
    text = subprocess.check_output(
        ["pdftotext", "-layout", "-f", "4", "-l", "5", str(pdf), "-"], encoding="utf8"
    )
    assert "Supplementary Table 2: Early Embryonic DNMs in mice" in text
    rows = {}
    for line in text.splitlines():
        fields = line.split()
        if not fields or fields[0] not in FAMILIES:
            continue
        family, chrom, pos, ref, alt, parent, vaf, n_pos, n_tested, lineage, frequency = fields
        assert parent in {"Father", "Mother"}
        assert int(n_tested) == FAMILIES[family][1]
        key = family, chrom, pos, ref, alt
        assert key not in rows
        rows[key] = parent, vaf, int(n_pos), int(n_tested), lineage
    assert len(rows) == 17
    return rows


def write_table(path, fieldnames, rows):
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(fieldnames)
        writer.writerows(rows)


def build(pdf, workbook, outdir, prior):
    sys.path.insert(0, str(prior))
    from check_discovery_panel import discovery_roster
    from extract_mouse import SAMPLE, event_rows, native_rows

    wgs = discovery_roster(pdf)  # also verifies the complete native PDF's SHA-256
    table2 = parse_table2(pdf)
    ee = {}
    early = Counter()
    all_events = Counter()
    for event, size in event_rows(native_rows(workbook)):
        matches = [SAMPLE.fullmatch(label.strip()) for label in event[5].split(",")]
        assert all(matches)
        families = {m[1] for m in matches}
        assert len(families) == 1
        family = families.pop()
        if family not in FAMILIES:
            continue
        pups = {f"{m[1]}_{m[2]}{m[3]}" for m in matches}
        discovery = pups & wgs
        assert discovery
        late_litter, n_assayed = FAMILIES[family]
        litter_numbers = Counter(int(SAMPLE.fullmatch(p)[2]) for p in discovery)
        early_n = litter_numbers[1]
        late_n = litter_numbers[late_litter]
        assert len(discovery) == early_n + late_n
        all_events[family] += 1
        if early_n:
            early[family, size, int(event[8] != "0"), early_n, late_n] += 1
        key = family, event[0], event[1], event[3], event[4]
        if event[8] == "0":
            assert key not in table2
            continue
        assert key in table2 and key not in ee and size == 1
        parent, vaf, reported, total, lineage = table2[key]
        assert (parent, event[8]) in {("Father","Paternal"), ("Mother","Maternal")}
        assert lineage == event[10] and total == n_assayed
        assert len(discovery) <= min(len(pups), reported) <= max(len(pups), reported) <= total
        ee[key] = (family, parent, lineage, vaf, total, len(pups), reported, early_n, late_n)
    assert set(ee) == set(table2)
    assert all_events == {"CBGP8": 172, "GPCB2": 216}
    assert sum(early.values()) == 173
    outdir.mkdir(parents=True, exist_ok=True)
    sequence = Counter()
    final = []
    # Follow the authors' Table 2 row order, without distributing coordinates or individual IDs.
    for key in table2:
        row = ee[key]
        family = row[0]
        sequence[family] += 1
        final.append((f"{family}-EE{sequence[family]:02d}", *row))
    write_table(outdir / "ee.tsv",
                ["event", "family", "parent", "lineage", "parent_alt_percent",
                 "offspring_assayed", "workbook_carriers", "table2_carriers",
                 "early_wgs_carriers", "late_wgs_carriers"], final)
    write_table(outdir / "early_wgs.tsv",
                ["family", "bases_per_event", "parent_mosaic", "early_wgs_carriers",
                 "late_wgs_carriers", "events"],
                [(*key, n) for key,n in sorted(early.items())])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("workbook", type=Path)
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--prior", type=Path, default=Path(__file__).resolve().parents[2] / "pedigree_timing/mouse")
    a = ap.parse_args()
    build(a.pdf, a.workbook, a.outdir, a.prior)
