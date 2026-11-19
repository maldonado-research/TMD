"""Reconstruct repeat overlap on original positives from reported integer percentages."""
import argparse
import csv
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
EXPECTED_SHA256 = "26377105d6d45de3f3864a3b7041bfa2c56dd4a3dc85a3035c4966132fd5d1c4"


def excess_points(p, q, union):
    # All inputs in percent. This is the joint fraction less the product of marginals, in points.
    return p + q - union - p * q / Decimal(100)


def overlap(row):
    p, q, union = (int(row[k]) for k in ("repeat_1_pct", "repeat_2_pct", "union_pct"))
    both = p + q - union
    if not (0 <= both <= min(p, q) <= max(p, q) <= union <= 100):
        raise ValueError("Printed percentages violate inclusion–exclusion.")
    return {
        "pair": row["repeat_pair"],
        "both_pct": both,
        "first_only_pct": union - q,
        "second_only_pct": union - p,
        "neither_pct": 100 - union,
        "gain_over_better_repeat_pp": union - max(p, q),
        "both_minus_marginal_product_pp": float(excess_points(p, q, union)),
        # Monotone increasing in p and q on [0,100] and decreasing in union.
        "lower_bound_gap_if_each_input_within_one_pp": float(excess_points(
            max(0, p - 1), max(0, q - 1), min(100, union + 1))),
    }


def replay(path):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Aggregate CSV digest differs from the source transcription.")
    rows = list(csv.DictReader(io.StringIO(data.decode())))
    leaf = [row for row in rows if row["category"] == "leaf-specific"]
    values = [overlap(row) for row in leaf]
    return {
        "source": "https://doi.org/10.1093/plcell/koag288",
        "supplement": "https://pmc.ncbi.nlm.nih.gov/articles/instance/13690466/bin/koag288_supplementary_data.pdf",
        "source_tables": ["S3", "S4", "S5"],
        "matched_percentages_csv_sha256": digest,
        "source_unit": "One historic tree, six technical repeat pairs at four labelled original locations.",
        "union_displayed_pct_by_category": {
            cat: [int(row["union_pct"]) for row in rows if row["category"] == cat]
            for cat in ("clonal", "mosaic", "leaf-specific")
        },
        "leaf_specific_equal_pair_mean_union_pct": round(mean(int(r["union_pct"]) for r in leaf), 4),
        "leaf_specific_from_displayed_percentages": values,
        "interpretation": "Fractions conditional on an original call. Counts and count-weighted totals "
                          "are unavailable in these percentage tables. Rounding sensitivity describes "
                          "uncertainty in the three displayed inputs."
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("aggregates", type=Path, nargs="?", default=HERE / "matched_percentages.csv")
    print(json.dumps(replay(parser.parse_args().aggregates), indent=2))
