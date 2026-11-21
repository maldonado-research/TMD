"""Leave out a complete plant line and predict a random recorded private substitution."""
import csv
import json
import math
from pathlib import Path
from statistics import fmean

CLASSES = ("C>A", "C>G", "C>T", "T>A", "T>C", "T>G")
FOLDER = Path(__file__).resolve().parent


def modal_credit(probabilities):
    largest = max(probabilities)
    modes = [p == largest for p in probabilities]
    return [int(tied) / sum(modes) for tied in modes]


def fold_scores(test, model, baseline):
    frequencies = [count / sum(test) for count in test]
    model_loss = 1 + sum(p * p for p in model) - 2 * sum(p * f for p, f in zip(model, frequencies))
    baseline_loss = (1 + sum(q * q for q in baseline)
                     - 2 * sum(q * f for q, f in zip(baseline, frequencies)))
    log_gain = sum(f * math.log(p / q) for f, p, q in zip(frequencies, model, baseline))
    model_credit = modal_credit(model)
    reference_credit = modal_credit(baseline)
    hit_gain = sum(f * (x - y) for f, x, y in zip(frequencies, model_credit, reference_credit))
    return {"model_brier": model_loss, "reference_brier": baseline_loss,
            "brier_gain": baseline_loss - model_loss, "log_gain_nats": log_gain,
            "top_class_hit_gain": hit_gain}


def coarsen(values):
    transitions = values[2] + values[4]
    transversions = sum(values[i] for i in (0, 1, 3, 5))
    return [transitions, transversions]


def score(rows):
    samples = [[int(row[c]) for c in CLASSES] for row in rows]
    totals = list(map(sum, zip(*samples)))
    reference = [1/6] * 6
    folds = {"six_classes": [], "transition_transversion": []}
    for test in samples:
        training = [total - held for total, held in zip(totals, test)]
        model = [(count + 1) / (sum(training) + 6) for count in training]
        folds["six_classes"].append(fold_scores(test, model, reference))
        folds["transition_transversion"].append(
            fold_scores(coarsen(test), coarsen(model), coarsen(reference)))
    result = {"lines": len(rows), "private_snms": sum(totals), "class_counts": dict(zip(CLASSES, totals))}
    for label, results in folds.items():
        result[label] = {key: round(fmean(f[key] for f in results), 10) for key in results[0]}
        result[label]["lines_with_positive_brier_gain"] = sum(f["brier_gain"] > 0 for f in results)
    return result


def main():
    with (FOLDER / "line_counts.tsv").open() as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    starred = [row for row in rows if row["table_s1_starred"] == "1"]
    conservative = [row for row in starred if row["named_in_shared_csv"] == "0"]
    if (len(rows), len(starred), len(conservative)) != (107, 48, 44):
        raise ValueError("Unexpected line roster")
    result = {"primary_table_s1_starred": score(starred),
              "sensitivity_starred_without_explicit_shared_listing": score(conservative)}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
