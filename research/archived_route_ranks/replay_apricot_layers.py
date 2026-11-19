"""Count published fruit-layer and paired leaf calls in Goel et al., Tables S1/S3/S4."""

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path

from openpyxl import load_workbook


SHA256 = "9cc9ea73b92f335e24670f9b75d2b923feaa120a3467546211d8a879a75046b5"
LAYERS = {
    frozenset({"L1"}): "L1_exclusive",
    frozenset({"L2"}): "L2_exclusive",
    frozenset({"L1", "L2"}): "both_fruit_layers",
    frozenset(): "leaf_only",
}


def records(book, sheet):
    rows = iter(book[sheet].values)
    next(rows)  # Worksheet caption.
    header = next(rows)
    return (dict(zip(header, row)) for row in rows)


def event(row):
    return row["Chromosome"], row["Position"], row["Alternate allele"]


def tally(counts):
    return {layer: {"leaf_listed": counts[layer, True],
                    "no_leaf_listing": counts[layer, False]}
            for layer in LAYERS.values()}


def summarize(events, excluded, branches):
    event_counts = Counter()
    branch_counts = {branch: Counter() for branch in branches}
    coordinates = set()
    for key, tissues_by_branch in events.items():
        if key in excluded:
            continue
        coordinates.add(key[:2])
        tissues = set.union(*tissues_by_branch.values())
        # Freeze the event's classification across all fruit branches.
        layer = LAYERS[frozenset(tissues - {"leaf"})]
        event_counts[layer, "leaf" in tissues] += 1
        for branch, local in tissues_by_branch.items():
            branch_counts[branch][layer, "leaf" in local] += 1

    branch_rows = []
    paired_direction_count = 0
    for branch, counts in branch_counts.items():
        l1_leaf = counts["L1_exclusive", True]
        l2_leaf = counts["L2_exclusive", True]
        l1_fruit = l1_leaf + counts["L1_exclusive", False]
        l2_fruit = l2_leaf + counts["L2_exclusive", False]
        branch_rows.append([branch, l1_fruit, l2_fruit, l1_leaf, l2_leaf])
        paired_direction_count += (l1_fruit > l2_fruit and l1_leaf < l2_leaf)
    return {
        "distinct_events": event_counts.total(),
        "distinct_coordinates": len(coordinates),
        "events_by_layer": tally(event_counts),
        "event_branch_pairs_by_layer": tally(sum(branch_counts.values(), Counter())),
        "exclusive_event_branch_counts": branch_rows,
        "branches_with_more_L1_in_fruit_and_more_L2_with_leaf_calls": paired_direction_count,
    }


def replay(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Workbook SHA-256 differs from archived Additional file 2 v1")
    book = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    try:
        samples = [(r["Branch"], r["Layer"].upper())
                   for r in records(book, "table S1 sequencing_stats")]
        branches = sorted({b for b, _ in samples})
        expected = {(b, t) for b in branches for t in ("L1", "L2", "LEAF")}
        if len(branches) != 7 or len(samples) != len(expected) or set(samples) != expected:
            raise ValueError("S1 does not describe seven complete fruit/leaf trios")

        events = defaultdict(lambda: defaultdict(set))
        organ_labels = defaultdict(set)
        flagged = set()
        for row in records(book, "table S3 somatic mutations"):
            key, branch, tissue = event(row), row["Branch"], row["Tissue"]
            local = events[key][branch]
            if (branch, tissue.upper()) not in expected or tissue in local:
                raise ValueError("Unexpected or duplicate S3 event/branch/tissue")
            local.add(tissue)
            organ_labels[key].add(row["Organ"])
            if row["Low confidence"] == "Y":
                flagged.add(key)
        s4 = list(records(book, "table S4 Allele_frequency"))
        labels = {event(row): row["Organ"] for row in s4}
    finally:
        book.close()

    if len(labels) != len(s4) or labels.keys() != events.keys():
        raise ValueError("Distinct event roster differs between S3 and S4")
    for key, observations in events.items():
        fruit = {b for b, t in observations.items() if t - {"leaf"}}
        leaf = {b for b, t in observations.items() if "leaf" in t}
        label = ("shared" if leaf else "fruit") if fruit else "leaf"
        if labels[key] != label or organ_labels[key] != {label}:
            raise ValueError("Organ label differs from the organ calls in S3")
        if fruit and not leaf.issubset(fruit):
            raise ValueError("Leaf and fruit call need a different branch pairing rule")
    return {
        "article_doi": "10.1186/s13059-024-03337-0",
        "workbook_doi": "10.6084/m9.figshare.26368540.v1",
        "workbook_sha256": SHA256,
        "S3_low_confidence_events": len(flagged),
        "branch_columns": ["branch", "fruit_L1_exclusive", "fruit_L2_exclusive",
                           "leaf_listed_L1_exclusive", "leaf_listed_L2_exclusive"],
        "all_listed": summarize(events, set(), branches),
        "excluding_S3_low_confidence": summarize(events, flagged, branches),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    print(json.dumps(replay(parser.parse_args().workbook), indent=2))
