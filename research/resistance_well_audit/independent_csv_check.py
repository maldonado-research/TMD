"""Original standard-library audit; never executes repository analysis code."""
import collections
import csv
import json
from pathlib import Path
import re

root = Path(__file__).parent
universe = {r + str(c) for r in "BCDEFGHIJK" for c in range(2, 8)}
assays, rejected, duplicates = {}, [], []
for path in sorted(root.glob("1ul_individual_*.csv")):
    rows = list(csv.reader(path.open()))
    for line, cells in enumerate(rows[1:], 2):
        if len(cells) != len(rows[0]):
            rejected.append({"file": path.name, "line": line, "fields": len(cells), "expected": len(rows[0])})
            continue
        row = dict(zip(rows[0], cells))
        treatment = row.get("antibiotic") or ("none" if "none" in path.name else "rifampicin+nalidixic acid")
        key = (treatment, int(row["volume"]), int(row["day"]), int(row["pmutS"]), row["medium"])
        value = row["wells"]
        tokens = value[1:] if value.startswith("-") else value
        if value == "ALL":
            wells = universe
        elif value == "0":
            wells = set()
        elif re.fullmatch(r"[B-K][2-7](;[B-K][2-7])*", tokens):
            wells = set(tokens.split(";"))
            if len(wells) != len(tokens.split(";")):
                raise ValueError((path, line, "duplicate token"))
            if value.startswith("-"):
                wells = universe - wells
        else:
            raise ValueError((path, line, "invalid syntax"))
        if key in assays:
            duplicates.append(key)
        assays[key] = wells

mismatches, missing, unpaired = [], [], []
comparisons = 0
for path in sorted(root.glob("1ul_aggregate_*.csv")):
    rows = list(csv.DictReader(path.open()))
    frequencies = sorted(list(rows[0])[5:], key=float)
    for row in rows:
        for rank, frequency in zip((0, 10, 25, 50), frequencies):
            medium = {"MH": "MH", "Rif": "rif", "Nal": "nal", "Nal + Rif": "nal+rif"}[row["resistance"]]
            key = (row["antibiotic"], int(row["volume"]), int(row["day"]), rank, medium)
            if key not in assays:
                unpaired.append(key)
            elif row[frequency] == "NA":
                missing.append(key)
            else:
                comparisons += 1
                actual, expected = len(assays[key]), int(row[frequency])
                if actual != expected:
                    mismatches.append({"key": key, "individual_count": actual, "aggregate_count": expected})

endpoints = []
for treatment in sorted({key[0] for key in assays}):
    for rank in (0, 10, 25, 50):
        keys = [(treatment, 1, 6, rank, medium) for medium in ("MH", "rif", "nal", "nal+rif")]
        result = {"treatment": treatment, "nominal_mutator_percent": rank, "logical_wells": 60, "complete": all(key in assays for key in keys)}
        if result["complete"]:
            counts, patterns = collections.Counter(), collections.Counter()
            for well in universe:
                bits = [int(well in assays[key]) for key in keys]
                state = "double" if bits[3] else "mixed" if bits[1] and bits[2] else "rif" if bits[1] else "nal" if bits[2] else "no_resistance"
                counts[state] += 1
                patterns["".join(map(str, bits))] += 1
            result.update(counts=dict(counts), assay_patterns=dict(patterns))
        endpoints.append(result)
output = dict(valid_assay_rows=len(assays), rejected_rows=rejected, duplicate_keys=duplicates, comparable_cells=comparisons, mismatch_count=len(mismatches), mismatches=mismatches, aggregate_missing=missing, unpaired=unpaired, endpoints=endpoints, state_rule="combination positive => double; otherwise both single positive => mixed; otherwise single positive => that resistance; otherwise no_resistance; MH all-negative preserved separately in assay_patterns")
print(json.dumps(output, indent=2))
