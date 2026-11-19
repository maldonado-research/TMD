"""Count DHQ1 sites and their leaf occurrences using Wang et al.'s branch labels."""
import argparse
import csv
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
import re


# Printed shoot labels in the physical sampling diagram (Wang et al., Fig. 4).
# The base leaf B1-L1, for example, lies directly on the main axis named B1.
FIGURE_LABELS = {
    "B1": {"B1", "B1-1", *(f"B1-{i}" for i in range(3, 17))},
    "B2": {"B2", *(f"B2-{i}" for i in range(1, 17))},
    "B3": {"B3", *(f"B3-{i}" for i in range(1, 6))},
    "B4": {"B4-1", "B4-2", "B4-3", *(f"B4-1-{i}" for i in range(1, 5))},
}


def read_tsv(path):
    with path.open(newline="", encoding="utf8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def three_marker_example(leaves, variants, diagram):
    # Figure 4 labels 1, 2, 3 are uniquely matched within B1 by carrier counts.
    counts = (27, 14, 8)
    columns = []
    for count in counts:
        matches = [set(row["listed_leaves"].split(";")) for row in variants
                   if len(row["listed_leaves"].split(";")) == count
                   and set(row["listed_leaves"].split(";")) <= leaves]
        if len(matches) != 1:
            raise ValueError(f"Expected one B1 carrier column of size {count}")
        columns.append(matches[0])
    calls = {leaf: "".join("1" if leaf in c else "0" for c in columns) for leaf in leaves}
    patterns = Counter(calls.values())
    observed_by_position = defaultdict(list)
    for leaf, state in calls.items():
        observed_by_position[leaf.removeprefix("DHQ1_").rsplit("-L", 1)[0]].append(state)
    drawn = {row["location"]: sorted(row["patterns_drawn_on_leaves"].split(";")) for row in diagram}
    if len(drawn) != len(diagram) or drawn != {key: sorted(v) for key, v in observed_by_position.items()}:
        raise ValueError("The source membership table and Figure 4 B1 patterns disagree")
    candidates = ["".join(p) for p in product("01", repeat=3)]
    best = 3 * len(leaves) + 1
    minimizing_families = []
    # Enumerate all 255 nonempty pattern families. A family can occur on a
    # perfect irreversible tree if the carrier sets of its columns are laminar.
    for size in range(1, len(candidates) + 1):
        for family in combinations(candidates, size):
            c = [{row for row in family if row[i] == "1"} for i in range(3)]
            if any(a & b and a - b and b - a for a, b in combinations(c, 2)):
                continue
            edits = sum(n * min(sum(x != y for x, y in zip(obs, new))
                                for new in family) for obs, n in patterns.items())
            if edits < best:
                best, minimizing_families = edits, []
            if edits == best:
                minimizing_families.append(list(family))
    return {"figure_4_mutation_labels_in_order": [1, 2, 3], "sampled_leaves": len(leaves),
            "figure_locations_with_agreeing_drawn_leaf_patterns": len(drawn),
            "column_totals": list(counts), "observed_pattern_counts": dict(sorted(patterns.items())),
            "crossing_pairs": sum(bool(a & b and a - b and b - a) for a, b in combinations(columns, 2)),
            "minimum_entry_changes_to_laminar": best, "minimizing_pattern_families": minimizing_families}


def historical_figure_pair(labels, variants, diagram):
    # Match each of Figure 4's marker labels by the number of listed carriers
    # at every B1 location. The two icons at a location are unordered.
    b1 = {leaf: position for leaf, position in labels.items() if position.split("-")[0] == "B1"}
    drawn = {r["location"]: sorted(r["figure_markers_4_2"].split(";")) for r in diagram}
    named = (("M71", "Pp01", 2130859, "SNV:A>C"), ("M101", "Pp04", 21561355, "SNV:G>A"))
    columns = []
    for i, (name, chrom, pos, change) in enumerate(named):
        diagram_counts = Counter({location: sum(s[i] == "1" for s in patterns)
                                  for location, patterns in drawn.items()})
        matches = []
        for row in variants:
            carriers = set(row["listed_leaves"].split(";"))
            if carriers <= b1.keys() and Counter(b1[leaf] for leaf in carriers) == diagram_counts:
                matches.append((row, carriers))
        if len(matches) != 1:
            raise ValueError(f"Diagram does not uniquely identify the proposed site for {name}")
        row, carriers = matches[0]
        if (row["chromosome"], int(row["position"]), row["change"]) != (chrom, pos, change):
            raise ValueError(f"Historical {name} marker identity differs")
        columns.append(carriers)
    by_location = defaultdict(list)
    all_calls = Counter()
    for leaf, position in labels.items():
        pattern = "".join("1" if leaf in c else "0" for c in columns)
        all_calls[pattern] += 1
        if leaf in b1:
            by_location[position].append(pattern)
    if {p: sorted(v) for p, v in by_location.items()} != drawn:
        raise ValueError("Historical marker co-occurrence differs from the original figure")
    return {"figure_marker_order": [4, 2], "later_marker_order": ["M71", "M101"],
            "matching_B1_locations": len(drawn), "B1_1_printed_two_marker_patterns": drawn["B1-1"],
            "B1_leaf_counts_by_pattern": dict(sorted(Counter(s for v in drawn.values() for s in v).items())),
            "all_75_leaf_counts_by_pattern": dict(sorted(all_calls.items()))}


def grouped_burden(roster, variants, diagram):
    branch_labels = {label: branch for branch, labels in FIGURE_LABELS.items() for label in labels}
    labels = {}
    for row in roster:
        sample = row["sample_id"]
        match = re.fullmatch(r"DHQ1_(B[1-4](?:-\d+)*)-L[12]", sample)
        if not match or match[1] not in branch_labels or sample in labels:
            raise ValueError(f"Unmatched or duplicate sample: {sample}")
        labels[sample] = match[1]
    if set(labels.values()) != set(branch_labels):
        raise ValueError("Expected the full Figure 4 location inventory")
    branch_sites = Counter()
    histograms = defaultdict(Counter)
    seen = set()
    two_leaf_one_position = []
    multibranch = 0
    for row in variants:
        key = (row["chromosome"], int(row["position"]))
        leaves = row["listed_leaves"].split(";")
        if key in seen or len(set(leaves)) != len(leaves) or not all(leaf in labels for leaf in leaves):
            raise ValueError(f"Invalid locus or leaf list at {key}")
        seen.add(key)
        positions = {labels[leaf] for leaf in leaves}
        branches = {branch_labels[pos] for pos in positions}
        if len(branches) > 1:
            multibranch += 1
        branch_sites.update(branches)
        group = "multiple_locations" if len(positions) > 1 else "one_location"
        histograms[group][len(leaves)] += 1
        if len(positions) == 1 and len(leaves) > 1:
            two_leaf_one_position.append({"locus": list(key), "location": next(iter(positions)), "leaves": len(leaves)})
    totals = {}
    for group in ("multiple_locations", "one_location"):
        hist = histograms[group]
        distinct = sum(hist.values())
        occurrences = sum(freq * count for freq, count in hist.items())
        totals[group] = {"distinct_sites": distinct, "site_leaf_occurrences": occurrences,
                         "occurrences_per_sample": str(Fraction(occurrences, len(labels))),
                         "additional_occurrences_beyond_first": occurrences - distinct,
                         "sites_by_number_of_carrier_leaves": dict(sorted(hist.items()))}
    spanning, within = totals["multiple_locations"], totals["one_location"]
    gap = within["distinct_sites"] - spanning["distinct_sites"]
    slope = spanning["additional_occurrences_beyond_first"] - within["additional_occurrences_beyond_first"]
    equality = str(Fraction(gap, slope)) if slope else None
    return {
        "sequenced_leaf_count": len(labels), "distinct_figure_locations": len(branch_labels),
        "sampled_leaves_by_main_branch": dict(sorted(Counter(branch_labels[pos] for pos in labels.values()).items())),
        "sites_detected_per_main_branch": dict(sorted(branch_sites.items())),
        "sites_listed_across_main_branches": multibranch, "groups": totals,
        "multiple_leaves_at_one_location": sorted(two_leaf_one_position, key=lambda r:r["locus"]),
        "additional_carrier_weight_at_equal_group_totals": equality,
        "historical_two_marker_figure_match": historical_figure_pair(labels, variants, diagram),
        "main_branch_B1_three_marker_check": three_marker_example(
            {leaf for leaf, position in labels.items() if branch_labels[position] == "B1"}, variants, diagram),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carriers", type=Path)
    parser.add_argument("roster", type=Path)
    parser.add_argument("--figure-rows", type=Path, default=Path(__file__).with_name("figure4_b1_patterns.tsv"))
    args = parser.parse_args()
    print(json.dumps(grouped_burden(read_tsv(args.roster), read_tsv(args.carriers), read_tsv(args.figure_rows)), indent=2))
