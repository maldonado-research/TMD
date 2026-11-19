"""Score Levy et al. (2015) public source CSVs, using only anonymous row positions."""
import argparse
from array import array
import csv
import hashlib
import json
from pathlib import Path


STUDIES = {
    "E1": ("90", "efc94566ce880bbfe8afda85c8643ca829a3124270632125689a819098bbb04d",
           [0, 16, 32, 40, 48, 64, 72, 80, 88, 96, 104, 112]),
    "E2": ("93", "f791ce0da354ff4dd516c46875b3367cd159e00fd8059344d4dec3680a21812f",
           [0, 8, 24, 40, 48, 56, 64, 72, 88, 96]),
}
SOURCE = ("https://static-content.springer.com/esm/art%3A10.1038%2Fnature14279/"
          "MediaObjects/41586_2015_BFnature14279_MOESM{}_ESM.csv")


def score(path, study):
    suffix, expected_hash, visits = STUDIES[study]
    with path.open("rb") as file:
        digest = hashlib.file_digest(file, "sha256").hexdigest()
    if digest != expected_hash:
        raise ValueError(f"{study} source SHA-256 mismatch for {path}")

    counts = [array("Q") for _ in range(3)]
    totals = [0] * len(visits)
    canonical = hashlib.sha256()
    baseline_hash = hashlib.sha256()
    with path.open(encoding="ascii", newline="") as file:
        reader = csv.reader(file)
        if next(reader) != [f"t={t}" for t in visits]:
            raise ValueError(f"{study} unexpected visit names")
        for row in reader:
            if not row:
                continue
            if len(row) != len(visits) or not all(s.isdecimal() for s in row):
                raise ValueError(f"{study} malformed count row on line {reader.line_num}")
            canonical.update((",".join(row) + "\n").encode("ascii"))
            baseline_hash.update((row[0] + "\n").encode("ascii"))
            for i, s in enumerate(row):
                totals[i] += int(s)
            for data, value in zip(counts, (row[0], row[1], row[-1])):
                data.append(int(value))
    baseline, early, final = counts
    if min(totals) == 0:
        raise ValueError(f"{study} has a zero-depth visit")
    zero, first = totals[:2]
    last = totals[-1]
    n = len(final)
    rules = {
        "baseline": (lambda i: baseline[i] > 0, lambda i: baseline[i]),
        "early": (lambda i: baseline[i] + early[i] > 0, lambda i: early[i]),
        "change": (lambda i: baseline[i] + early[i] > 0,
                   lambda i: 2 * early[i] * zero - baseline[i] * first),
    }

    def summary(i):
        return {"row_id_1_based": i + 1, "baseline_reads": baseline[i],
                "early_reads": early[i], "final_reads": final[i],
                "final_rank_min": 1 + sum(c > final[i] for c in final),
                "final_rank_max": sum(c >= final[i] for c in final)}

    win = max(final)
    final_ids = [i for i, f in enumerate(final) if f == win]
    predictions = {}
    for rule, (eligible, metric) in rules.items():
        top = None
        best = []
        eligible_count = 0
        for i in range(n):
            if not eligible(i):
                continue
            eligible_count += 1
            value = metric(i)
            if top is None or value > top:
                best = [i]
                top = value
            elif value == top:
                best.append(i)
        unique = len(best) == 1
        final_eligible = [eligible(i) for i in final_ids]
        predictions[rule] = {
            "eligible": eligible_count, "n_tied_for_prediction": len(best),
            "abstain": not unique,
            "strict_hit": unique and len(final_ids) == 1 and best == final_ids,
            "joint_first_with_unique_prediction": unique and best[0] in final_ids,
            "guessing_reference_numerator": int(len(final_ids) == 1 and all(final_eligible)),
            "guessing_reference_denominator": eligible_count,
            "prediction": summary(best[0]) if unique else None,
        }
    return {
        "study": study, "url": SOURCE.format(suffix), "source_sha256": digest,
        "source_bytes": path.stat().st_size, "rows": n, "generations": visits,
        "all_visit_read_depth": totals,
        "canonical_all_count_rows_sha256": canonical.hexdigest(),
        "canonical_baseline_column_sha256": baseline_hash.hexdigest(),
        "positive_rows_baseline_early_final": [sum(v > 0 for v in col) for col in counts],
        "zero_baseline_positive_early_rows": sum(not b and e > 0 for b, e in zip(baseline, early)),
        "first_positive_after_early_and_positive_final_rows": sum(
            not b and not e and f > 0 for b, e, f in zip(baseline, early, final)),
        "n_final_tied_for_first": len(final_ids),
        "final_leaders": [summary(i) for i in final_ids], "rules": predictions,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("E1", type=Path, help="Original Nature Source Data MOESM90 CSV")
    parser.add_argument("E2", type=Path, help="Original Nature Source Data MOESM93 CSV")
    args = parser.parse_args()
    results = [score(getattr(args, name), name) for name in STUDIES]
    a, b = results
    print(json.dumps({"series": results, "sources_have_identical_baseline_rows": (
        a["rows"] == b["rows"] and a["canonical_baseline_column_sha256"] ==
        b["canonical_baseline_column_sha256"])}, indent=2))
