"""Match the Figure 4 diagram to S1/S2 preserving sampled locations and all entries."""
import argparse
from collections import Counter, defaultdict
import csv
from itertools import combinations, permutations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_rows(path):
    with path.open(encoding="utf8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def read_figure(path):
    location = {}
    columns = defaultdict(set)
    for row in read_rows(path):
        name = row["location"]
        for index, text in enumerate(row["marker_lists_on_drawn_leaf_icons"].split(";"), start=1):
            key = f"{name}#{index}"
            if key in location:
                raise ValueError(f"Duplicate drawing location: {name}")
            location[key] = name
            markers = [int(x) for x in text.split(",")]
            if len(markers) != len(set(markers)):
                raise ValueError(f"Repeated figure marker on one leaf icon at {name}")
            for marker in markers:
                columns[marker].add(key)
    if set(columns) != set(range(1, 49)):
        raise ValueError("Expected the 48 distinct marker labels from Figure 4")
    return location, columns


def read_catalogue(variants, roster):
    location = {}
    for row in read_rows(roster):
        leaf = row["sample_id"]
        name, sep, suffix = leaf.removeprefix("DHQ1_").rpartition("-L")
        if not sep or suffix not in {"1", "2"} or leaf in location:
            raise ValueError(f"Ambiguous leaf: {leaf}")
        location[leaf] = name
    columns = {}
    for row in read_rows(variants):
        marker = (row["chromosome"], int(row["position"]))
        leaves = row["listed_leaves"].split(";")
        if marker in columns or len(leaves) != len(set(leaves)) or not set(leaves) <= location.keys():
            raise ValueError(f"Invalid catalogue record at {marker}")
        columns[marker] = set(leaves)
    return location, columns


def signatures(locations, columns):
    """A leaf signature is preserved by every location-preserving incidence match."""
    leaf_profiles = {leaf: [] for leaf in locations}
    for carrier_leaves in columns.values():
        profile = tuple(sorted(locations[leaf] for leaf in carrier_leaves))
        for leaf in carrier_leaves:
            leaf_profiles[leaf].append(profile)
    return {leaf: tuple(sorted(profiles)) for leaf, profiles in leaf_profiles.items()}


def compatible_rows(left_loc, left, right_loc, right):
    if Counter(left_loc.values()) != Counter(right_loc.values()) or len(left) != len(right):
        raise ValueError("Different location or marker inventories")
    left_sig, right_sig = signatures(left_loc, left), signatures(right_loc, right)
    options = []
    for loc in sorted(set(left_loc.values())):
        icons = sorted(key for key, name in left_loc.items() if name == loc)
        samples = sorted(key for key, name in right_loc.items() if name == loc)
        possible = [dict(zip(icons, order)) for order in permutations(samples)
                    if all(left_sig[a] == right_sig[b] for a, b in zip(icons, order))]
        if not possible:
            raise ValueError(f"No possible row match at {loc}")
        options.append(possible)
    return sorted(options, key=len)


def find_mapping(options, left, right):
    """Search location-level assignments, checking the complete column multiset on each prefix."""
    def extend(depth, row_map):
        if depth == len(options):
            return row_map
        for option in options[depth]:
            joined = {**row_map, **option}
            mapped_rows = set(joined.values())
            observed = Counter(frozenset(joined[leaf] for leaf in group if leaf in joined)
                               for group in left.values())
            expected = Counter(frozenset(group & mapped_rows) for group in right.values())
            if observed == expected:
                match = extend(depth + 1, joined)
                if match is not None:
                    return match
        return None

    row_map = extend(0, {})
    if row_map is None:
        raise ValueError("No full location-preserving match")
    return row_map


def relations(columns):
    classes = Counter()
    conflicts = []
    for i, j in combinations(sorted(columns), 2):
        s, t = columns[i], columns[j]
        if s == t:
            relation = "equal"
        elif not s & t:
            relation = "disjoint"
        elif s <= t or t <= s:
            relation = "strictly_nested"
        else:
            relation = "crossing"
            conflicts.append([i, j])
        classes[relation] += 1
    return dict(sorted(classes.items())), conflicts


def verify(figure, carriers, roster):
    left_loc, left = read_figure(figure)
    right_loc, right = read_catalogue(carriers, roster)
    options = compatible_rows(left_loc, left, right_loc, right)
    rows = find_mapping(options, left, right)
    right_by_column = defaultdict(list)
    for site, group in sorted(right.items()):
        right_by_column[frozenset(group)].append(site)
    checked = 0
    for marker in sorted(left):
        group = frozenset(rows[leaf] for leaf in left[marker])
        site = right_by_column[group].pop()
        if any((leaf in left[marker]) != (rows[leaf] in right[site]) for leaf in left_loc):
            raise ValueError("Certificate failed")
        checked += len(rows)
    if any(right_by_column.values()):
        raise ValueError("Unmatched catalogue columns")
    lc, crossings = relations(left)
    rc, _ = relations(right)
    if lc != rc:
        raise ValueError("Mismatched pair relations")
    return {"diagram_markers": len(left), "diagram_leaf_icons": len(rows), "locations": len(options),
            "diagram_positive_memberships": sum(map(len, left.values())),
            "binary_entries_matched_under_single_bijection": checked,
            "figure_marker_relations": lc, "crossing_pairs_of_figure_labels": crossings,
            "locations_with_multiple_signature_compatible_icon_orders": sum(len(opts)>1 for opts in options),
            "unique_named_row_or_marker_alignment_required": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carriers", type=Path)
    parser.add_argument("roster", type=Path)
    parser.add_argument("--figure", type=Path, default=HERE / "figure4_leaf_icons.tsv")
    args = parser.parse_args()
    print(json.dumps(verify(args.figure, args.carriers, args.roster), indent=2))
