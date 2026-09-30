"""Descriptive secondary analysis of Leehan & Nicholson 2021, Table 1.

No p values are computed: treatment randomization and exchangeability have not
been verified. Three published experimental blocks, not fabricated isolate IDs,
define held-out folds. Python standard library only.
"""
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE / "leehan2021_table1_by_block.csv"
CONTEXTS = ("LB", "SMMAsn")
ALPHA = 0.5


def joint(rows):
    result = Counter()
    for row in rows:
        result[row["context"], row["source_row"]] += row["count"]
    return result


def mi(table):
    total = sum(table.values())
    by_context, by_route = Counter(), Counter()
    for (context, route), n in table.items():
        by_context[context] += n
        by_route[route] += n
    return sum(n / total * math.log2(n * total / (by_context[c] * by_route[r]))
               for (c, r), n in table.items() if n)


def analyze(rows):
    table = joint(rows)
    routes = sorted({r["source_row"] for r in rows})
    total = sum(table.values())
    counts = {c: {r: table[c, r] for r in routes} for c in CONTEXTS}
    by_block, heldout = [], []
    for block in (1, 2, 3):
        test = [r for r in rows if r["experimental_block"] == block]
        test_table = joint(test)
        n_test = sum(test_table.values())
        by_block.append({"block": block, "n": n_test,
                         "context_totals": {c: sum(n for (cx, _), n in test_table.items() if cx == c)
                                             for c in CONTEXTS},
                         "context_route_mi_bits": mi(test_table)})
        train = joint([r for r in rows if r["experimental_block"] != block])
        train_by_route = Counter()
        train_by_context = Counter()
        for (c, r), n in train.items():
            train_by_route[r] += n
            train_by_context[c] += n
        n_train = sum(train.values())
        delta = 0.0
        for (c, r), n in test_table.items():
            p_context = (train[c, r] + ALPHA) / (train_by_context[c] + ALPHA * len(routes))
            p_pooled = (train_by_route[r] + ALPHA) / (n_train + ALPHA * len(routes))
            delta += n * math.log2(p_context / p_pooled)
        heldout.append({"heldout_block": block, "train_n": n_train, "test_n": n_test,
                        "context_minus_pooled_logscore_bits": delta,
                        "context_minus_pooled_bits_per_observation": delta / n_test})
    return {"n": total, "route_classes": len(routes),
            "context_totals": {c: sum(counts[c].values()) for c in CONTEXTS},
            "pooled_context_route_mi_bits": mi(table),
            "conditional_context_route_mi_given_block_bits": sum(b["n"] * b["context_route_mi_bits"] for b in by_block) / total,
            "counts": counts, "by_block": by_block, "heldout_experimental_blocks": heldout,
            "heldout_total_logscore_gain_bits": sum(f["context_minus_pooled_logscore_bits"] for f in heldout),
            "heldout_mean_gain_bits_per_observation": sum(f["context_minus_pooled_logscore_bits"] for f in heldout) / total}


def main():
    with INPUT.open(newline="") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        row["count"] = int(row["count"])
        row["experimental_block"] = int(row["experimental_block"])
        assert row["count"] >= 0
        assert row["context"] in CONTEXTS
        assert row["source_doi"] == "10.1128/AEM.01237-21"
    assert len(rows) == 96
    assert len({(r["experimental_block"], r["context"], r["source_row"]) for r in rows}) == 96
    points = [r for r in rows if r["source_row"] not in {"No mutation found", "Other"}]
    results = {"source": "https://journals.asm.org/doi/10.1128/aem.01237-21",
               "source_table": 1, "transcription_cells": 96,
               "csv_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
               "analysis_status": "exploratory descriptive secondary analysis; not a preregistered TMD validation",
               "smoothing_per_route_alpha": ALPHA,
               "all_sequenced_resistant_isolates": analyze(rows),
               "identified_point_substitutions": analyze(points)}
    assert results["all_sequenced_resistant_isolates"]["context_totals"] == {"LB": 59, "SMMAsn": 52}
    assert results["identified_point_substitutions"]["context_totals"] == {"LB": 53, "SMMAsn": 51}
    (HERE / "rpob_results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({key: {k: v for k, v in results[key].items() if k not in {"counts", "by_block", "heldout_experimental_blocks"}}
                      for key in ("all_sequenced_resistant_isolates", "identified_point_substitutions")}, indent=2))


if __name__ == "__main__":
    main()
