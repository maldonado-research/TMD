"""Exact assignment ranges for two small historical, phenotype-selected rosters."""

import json
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUTES = "WAM"


def project(groups):
    """Each unit contributes one label from its allowed set. O means other."""
    labels = ROUTES + "O"
    base = [0] * len(labels)
    uncertain = []
    for allowed, count in groups.items():
        if not allowed or len(set(allowed)) != len(allowed) or set(allowed) - set(labels):
            raise ValueError("Invalid allowed labels")
        if type(count) is not int or count < 0:
            raise ValueError("Invalid group count")
        indices = [labels.index(label) for label in allowed]
        if len(indices) == 1:
            base[indices[0]] += count
        else:
            uncertain.extend([indices] * count)

    tables = {tuple(base)}
    for choices in uncertain:
        next_tables = set()
        for table in tables:
            for i in choices:
                updated = list(table)
                updated[i] += 1
                next_tables.add(tuple(updated))
        tables = next_tables

    def endpoints(values):
        return [min(values), max(values)]

    totals = {label: endpoints([t[i] for t in tables]) for i, label in enumerate(labels)}
    differences = {}
    for i, j in combinations(range(3), 2):
        differences[f"{labels[i]}-{labels[j]}"] = endpoints([t[i] - t[j] for t in tables])
    orders = []
    for i, j, k in permutations(range(3)):
        if any(t[i] > t[j] > t[k] for t in tables):
            orders.append(f"{labels[i]}>{labels[j]}>{labels[k]}")
    return {
        "totals": totals,
        "differences": differences,
        "strict_orders": sorted(orders),
        "ties_possible": any(len(set(t[:3])) < 3 for t in tables),
        "distinct_count_tables": len(tables),
    }


def analyze():
    historical = json.loads((HERE / "historical_receipt.json").read_bytes())
    modern = json.loads((HERE / "matela_receipt.json").read_bytes())
    groups = modern["focal_class_union_across_archived_wrinkly_clones_in_each_parent"]
    if sum(groups.values()) != modern["represented_wrinkly_parents"]:
        raise ValueError("Parent support counts are inconsistent")
    extended = Counter(groups)
    extended["WAMO"] += 1
    return {
        "unit": "one retained archived label per represented parent",
        "historical_ledger_sha256": historical["source_sha256"],
        "historical_26": project(historical["allowed_classes"]),
        "matela_50": project(groups),
        "matela_51_hypothetical_one_unrestricted_extra": project(extended),
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2))
