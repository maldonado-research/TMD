"""Enumerate optional training labels and diagnose single-pedigree contributions."""
import argparse
import csv
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

CLASSES = ("C>A", "C>G", "C>T", "T>A", "T>C", "T>G")
OPTIONS = ("omit", *CLASSES)


def read_rows(path):
    with path.open() as source:
        return list(csv.DictReader(source, delimiter="\t"))


def read_kennedy(root):
    rows = read_rows(root / "kennedy/kennedy_events.tsv")
    pending = [r for r in rows if r["substitution_class"] not in CLASSES]
    if [(r["event_id"], r["pedigree"], r["time_lower"], r["time_upper"]) for r in pending] != [
            ("V133", "F", "8", "9")]:
        raise ValueError("Unexpected unresolved Kennedy event")
    training = defaultdict(Counter)
    windows = {}
    for family in sorted({r["pedigree"] for r in rows}):
        eligible = [r for r in rows if r["pedigree"] == family and r["path"] != "G2"]
        cutoff = min(int(r["time_upper"]) for r in eligible)
        windows[family] = Counter(r["substitution_class"] for r in eligible
                                  if int(r["time_lower"]) <= cutoff)
    for r in rows:
        if r["substitution_class"] in CLASSES:
            training[r["pedigree"]][r["substitution_class"]] += 1
    return training, windows


def read_dowsett(root):
    rows = read_rows(root / "dowsett/dowsett_classes.tsv")
    pending = [(r["pedigree"], r["physical_division"], r["unclassified"]) for r in rows
               if int(r["unclassified"])]
    if pending != [("Y6", "9", "1")]:
        raise ValueError("Unexpected unresolved Dowsett entry")
    training = defaultdict(Counter)
    windows = {}
    for family in sorted({r["pedigree"] for r in rows}):
        divisions = [r for r in rows if r["pedigree"] == family]
        earliest = min((r for r in divisions if int(r["assigned_changes"])),
                       key=lambda r: int(r["physical_division"]))
        windows[family] = Counter({c: int(earliest[c]) for c in CLASSES if int(earliest[c])})
        for r in divisions:
            training[family].update({c: int(r[c]) for c in CLASSES})
    flagged = [r for r in rows if (r["pedigree"], r["physical_division"]) == ("Y1", "3")]
    if len(flagged) != 1 or int(flagged[0]["C>T"]) != 68:
        raise ValueError("Unexpected Y1 division 3 count")
    # Each scenario adds back either zero or one chosen label for this source record.
    training["Y1"]["C>T"] -= 1
    return training, windows


def evaluate(training, windows, changes):
    folds = {}
    for held, earliest in windows.items():
        if not earliest or not set(earliest) <= set(CLASSES):
            raise ValueError(f"Unclassified earliest set for {held}")
        counts = Counter({c: 1 for c in CLASSES})
        for family, recorded in training.items():
            if family != held:
                counts.update(recorded)
        for family, label in changes:
            if family != held and label != "omit":
                counts[label] += 1
        probabilities = {c: Fraction(counts[c], counts.total()) for c in CLASSES}
        # The summed six-class Brier loss of the uniform reference is 5/6 for every y.
        gains = {y: Fraction(5, 6) - sum((p - int(c == y)) ** 2 for c, p in probabilities.items())
                 for y in earliest}
        draw = sum(gains[y] * count for y, count in earliest.items()) / sum(earliest.values())
        folds[held] = {"lower": min(gains.values()), "upper": max(gains.values()), "random_draw": draw}
    if len(folds) != 7:
        raise ValueError("Expected seven primary pedigrees")
    return folds


def average(folds):
    return {key: sum(f[key] for f in folds) / len(folds) for key in ("lower", "upper", "random_draw")}


def audit(training, windows, affected, printed):
    scenarios = {}
    for labels in itertools.product(OPTIONS, repeat=len(affected)):
        folds = evaluate(training, windows, list(zip(affected, labels)))
        scenarios[labels] = average(list(folds.values()))
    baseline = evaluate(training, windows, list(zip(affected, printed)))
    ranges = {}
    for key in ("lower", "upper"):
        values = [s[key] for s in scenarios.values()]
        ranges[key] = [round(float(min(values)), 12), round(float(max(values)), 12)]
    summary = {"scenarios": len(scenarios), "printed_labels": list(printed),
               "printed_bounds": [round(float(scenarios[printed][k]), 12) for k in ("lower", "upper")],
               "range_of_endpoints": ranges}
    return summary, baseline


def main(root):
    kennedy, base = audit(*read_kennedy(root), ("F",), ("omit",))
    dowsett, _ = audit(*read_dowsett(root), ("Y6", "Y1"), ("omit", "C>T"))
    deleted = {}
    for held in base:
        remaining = [v for k, v in base.items() if k != held]
        deleted[held] = {k: round(float(v), 12) for k, v in average(remaining).items()}
    return {"kennedy_training_label": kennedy, "dowsett_training_labels_y6_then_y1": dowsett,
            "kennedy_delete_one_scored_family_fixed_forecasts": deleted}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    print(json.dumps(main(args.input_root), indent=2))
