"""Sharp count differences for the phenotype-selected Howells wrinkly endpoints."""
import json
from itertools import combinations_with_replacement
from pathlib import Path

from research.archived_route_ranks.audit import project

HERE = Path(__file__).resolve().parent


def complete(cohort):
    counts = cohort["clones_by_phenotype_and_recorded_family"]["wrinkly"]
    if set(counts) != {"W", "A", "M", "unmatched"} or sum(counts.values()) != cohort["parents"]:
        raise ValueError("Expected one singly annotated or unmatched wrinkly record per parent.")
    groups = {label: counts[label] for label in "WAM"}
    groups["WAMO"] = counts["unmatched"]
    result = project(groups)

    # Record each distinct allocation of the unmatched slots that recovers the earlier order.
    allocations = []
    for labels in combinations_with_replacement("WAMO", counts["unmatched"]):
        w, a, m = [counts[k] + labels.count(k) for k in "WAM"]
        if w > a > m:
            allocations.append({k: labels.count(k) for k in "WAMO"})
    return {"parents": cohort["parents"], **result, "unmatched_allocations_for_W_gt_A_gt_M": allocations}


def analyze(receipt):
    cohorts = {**receipt["arms"], "pooled": receipt["paired_roster_totals"]}
    for k, total in cohorts["pooled"]["clones_by_phenotype_and_recorded_family"]["wrinkly"].items():
        if total != sum(c["clones_by_phenotype_and_recorded_family"]["wrinkly"][k]
                        for c in receipt["arms"].values()):
            raise ValueError("Pooled wrinkly counts disagree with the two contexts.")
    return {name: complete(c) for name, c in cohorts.items()}


if __name__ == "__main__":
    receipt = json.loads((HERE / "howells_receipt.json").read_bytes())
    print(json.dumps(analyze(receipt), indent=2))
