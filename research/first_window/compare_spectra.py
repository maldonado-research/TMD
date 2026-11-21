"""Replay the equal-pedigree first-window forecast comparisons using only the included TSVs."""
import csv
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from math import fsum, log
from pathlib import Path

from score_bounds import score_unit, summarize_units

ROOT = Path(__file__).resolve().parent
CLASSES = ("C>A", "C>G", "C>T", "T>A", "T>C", "T>G")
TRANSITIONS = {"C>T", "T>C"}
UNKNOWN = "unknown"


@dataclass
class Window:
    family: str
    path: str
    low: int
    high: int
    counts: Counter


def rows(filename):
    with (ROOT / filename).open() as source:
        yield from csv.DictReader(source, delimiter="\t")


def read_studies():
    kennedy = []
    for row in rows("kennedy/kennedy_events.tsv"):
        kind = row["substitution_class"]
        if kind not in (*CLASSES, UNKNOWN):
            raise ValueError(f"Unrecognized Kennedy label {kind}")
        kennedy.append(Window(row["pedigree"], row["path"], int(row["time_lower"]),
                              int(row["time_upper"]), Counter({kind: 1})))
    dowsett = []
    for row in rows("dowsett/dowsett_classes.tsv"):
        counts = Counter({c: int(row[c]) for c in CLASSES})
        counts[UNKNOWN] = int(row["unclassified"])
        if sum(counts.values()) != int(row["assigned_changes"]):
            raise ValueError("Dowsett row does not reconcile")
        index = int(row["physical_division"])
        dowsett.append(Window(row["pedigree"], row["pedigree"], index, index, counts))
    return {"Kennedy": kennedy, "Dowsett": dowsett}


def spectrum(records):
    counts = Counter()
    for row in records:
        counts.update(row.counts)
    return counts


def probabilities(counts):
    total = sum(counts[c] + 1 for c in CLASSES)
    return {c: Fraction(counts[c] + 1, total) for c in CLASSES}


def collapse(mapping):
    return {"Ts": sum(mapping.get(c, 0) for c in TRANSITIONS),
            "Tv": sum(mapping.get(c, 0) for c in CLASSES if c not in TRANSITIONS)}


def compare(training, earliest, binary):
    p, q = probabilities(training), probabilities(Counter())
    frequencies = {c: earliest[c] for c in CLASSES}
    if binary:
        p, q, frequencies = collapse(p), collapse(q), collapse(frequencies)
    labels = [c for c, n in frequencies.items() if n or earliest[UNKNOWN]]
    outcomes = score_unit(labels, p, q)
    draw = None
    if not earliest[UNKNOWN]:
        n = sum(frequencies.values())
        draw = {
            "brier_gain": sum(Fraction(frequencies[c], n) * s.brier_gain for c, s in outcomes.items()),
            "log_gain_nats": fsum(frequencies[c] / n * log(s.likelihood_ratio)
                                  for c, s in outcomes.items()),
            "randomized_top_gain": sum(Fraction(frequencies[c], n) * s.randomized_top_gain
                                       for c, s in outcomes.items()),
        }
    return outcomes, draw


def analyze(target, records, training_source, exclude_family, paths, binary):
    paired, draws, folds = [], [], []
    for path in paths:
        on_path = [record for record in records if record.path == path]
        family, = {record.family for record in on_path}
        first_upper = min(r.high for r in on_path if sum(r.counts.values()))
        first = spectrum(r for r in on_path if r.low <= first_upper)
        train = spectrum(r for r in training_source if not exclude_family or r.family != family)
        scores, draw = compare(train, first, binary)
        paired.append(scores)
        if draw is not None:
            draws.append(draw)
        folds.append(dict(path=path, family=family, first_upper=first_upper,
                          first_counts=dict(first), compatible_types=list(scores),
                          training_counts=dict(train), paired_bounds=summarize_units([scores]),
                          random_recorded_snv=draw))
    mean_draw = {k: sum(d[k] for d in draws) / len(draws) for k in draws[0]} if draws else {}
    return dict(study=target, coding="Ts/Tv" if binary else "six types", folds=folds,
                first_class_identified=sum(len(s) == 1 for s in paired),
                paired_bounds=summarize_units(paired),
                random_recorded_snv={"units": len(draws), "mean": mean_draw})


def calculate():
    studies = read_studies()
    results = {}
    for name, records in studies.items():
        paths = sorted({r.path for r in records} - {"G2"})
        if len(paths) != 7 or len({r.family for r in records}) != 7:
            raise ValueError("Expected seven founders in each primary comparison")
        other = next(k for k in studies if k != name)
        for binary in (False, True):
            coding = "binary" if binary else "six"
            for training in (name, other):
                key = f"{training}_to_{name}_{coding}"
                results[key] = analyze(name, records, studies[training], training == name, paths, binary)
            if name == "Kennedy":
                results["Kennedy_G2_" + coding] = analyze(name, records, records, True, ["G2"], binary)
    return results


if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2, default=str, allow_nan=False))
