"""Score the two Lindsay mouse panels. Binary Brier loss is averaged over offspring per site."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent


def read_rows(path):
    with path.open(encoding="utf8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def brier(probability, observed_fraction):
    if not 0 <= min(probability, observed_fraction) <= max(probability, observed_fraction) <= 1:
        raise ValueError("Invalid event probability or observed frequency")
    return probability * probability + observed_fraction * (1 - 2 * probability)


def summarize(sites, comparisons):
    forecasts = list(sites[0]["forecasts"])
    assert all(set(site["forecasts"]) == set(forecasts) for site in sites)
    observed = [F(site["carriers"], site["tested"]) for site in sites]
    losses = {rule: [brier(site["forecasts"][rule], r) for site, r in zip(sites, observed)]
              for rule in forecasts}
    gains = {}
    for rule, reference in comparisons:
        delta = [b - a for a, b in zip(losses[rule], losses[reference])]
        gains[f"{rule}_vs_{reference}"] = {
            "gain": mean(delta),
            "markers_favor_forecast": sum(x > 0 for x in delta),
            "markers_tied": sum(x == 0 for x in delta),
            "markers_favor_reference": sum(x < 0 for x in delta),
        }
    return {
        "markers": len(sites),
        "carrier_observations": sum(site["carriers"] for site in sites),
        "tested_observations": sum(site["tested"] for site in sites),
        "mean_observed": mean(observed),
        "mean_forecast": {rule: mean(site["forecasts"][rule] for site in sites) for rule in forecasts},
        "mean_loss": {rule: mean(values) for rule, values in losses.items()},
        "pairwise": gains,
    }


def balanced(by_family, contrasts):
    results = {f: summarize(sites, contrasts) for f, sites in sorted(by_family.items())}
    families = list(results.values())
    rules = list(families[0]["mean_forecast"])
    return {
        "families": results,
        "equal_family_mean": {
            "families": len(families),
            "mean_observed": mean(f["mean_observed"] for f in families),
            "mean_forecast": {r: mean(f["mean_forecast"][r] for f in families) for r in rules},
            "mean_loss": {r: mean(f["mean_loss"][r] for f in families) for r in rules},
            "pairwise": {c: {"gain": mean(f["pairwise"][c]["gain"] for f in families),
                              "markers_favor_forecast": sum(f["pairwise"][c]["markers_favor_forecast"] for f in families),
                              "markers_tied": sum(f["pairwise"][c]["markers_tied"] for f in families),
                              "markers_favor_reference": sum(f["pairwise"][c]["markers_favor_reference"] for f in families)}
                         for c in families[0]["pairwise"]},
        },
    }


def ee(rows, total_column):
    by_family = defaultdict(list)
    for row in rows:
        x = int(row["early_wgs_carriers"]) + int(row["late_wgs_carriers"])
        m = 10
        assert 1 <= x <= m
        parent = F(row["parent_alt_percent"]) / 100
        discovery = F(x, m)
        by_family[row["family"]].append({
            "carriers": int(row[total_column])-x,
            "tested": int(row["offspring_assayed"])-m,
            "forecasts": {"parent": parent, "wgs": discovery, "wgs_smoothed": F(2*x+1, 2*(m+1)),
                          "average": (parent + discovery)/2},
        })
    contrasts = [("parent", "wgs"), ("wgs_smoothed", "wgs"), ("average", "wgs"),
                 ("parent", "wgs_smoothed")]
    return balanced(by_family, contrasts)


def vee(rows, include_measured_failed):
    eligible = [r for r in rows if r["parental_vaf"] != "NA" and r["carrier_offspring"] != "NA"
                and r["assayed_offspring"] != "NA" and int(r["assayed_offspring"]) > 0
                and (r["validation"] == "PASS" or include_measured_failed)]
    # The inclusive descriptive analysis re-estimates its comparator from the same expanded roster.
    family_rates = defaultdict(list)
    for r in eligible:
        family_rates[r["pedigree"]].append(F(int(r["carrier_offspring"]), int(r["assayed_offspring"])))
    by_family = defaultdict(list)
    for family in family_rates:
        outside = mean(mean(rates) for f, rates in family_rates.items() if f != family)
        for r in eligible:
            if r["pedigree"] != family:
                continue
            by_family[family].append({
                "carriers": int(r["carrier_offspring"]), "tested": int(r["assayed_offspring"]),
                "forecasts": {"parent": F(r["parental_vaf"]), "other_families": outside},
            })
    result = balanced(by_family, [("parent", "other_families")])
    if not include_measured_failed:
        # This post-score identity uses test-family outcomes and only diagnoses the eligible contrast.
        diagnostic = {}
        for family, group in result["families"].items():
            r = group["mean_observed"]
            q = group["mean_forecast"]["other_families"]
            oracle_loss = r * (1-r)
            penalty = (q-r)**2
            parent_vs_oracle = oracle_loss - group["mean_loss"]["parent"]
            assert parent_vs_oracle + penalty == group["pairwise"]["parent_vs_other_families"]["gain"]
            diagnostic[family] = {"observed_family_mean": r, "oracle_constant_brier": oracle_loss,
                                  "other_family_constant_excess_loss": penalty,
                                  "parent_vs_oracle_gain": parent_vs_oracle}
        result["exploratory_oracle_decomposition"] = {
            "families": diagnostic,
            "equal_family_mean": {key: mean(f[key] for f in diagnostic.values())
                                  for key in next(iter(diagnostic.values()))},
        }
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=ROOT)
    args = ap.parse_args()
    rows = read_rows(args.input / "ee.tsv")
    result = {"offspring_ascertained": {"primary_table2": ee(rows, "table2_carriers"),
                                        "workbook_sensitivity": ee(rows, "workbook_carriers")}}
    other = read_rows(args.input / "vee.tsv")
    roster = Counter()
    for row in other:
        key = f"{row['validation']}_"
        if row["carrier_offspring"] == "NA":
            key += "missing"
        else:
            key += "positive" if int(row["carrier_offspring"]) else "zero"
        roster[key] += 1
    result["parent_ascertained"] = {"attempted": dict(sorted(roster.items())), "confirmed": vee(other, False),
                                   "including_measured_failed": vee(other, True)}
    print(json.dumps(result, indent=2, default=lambda x: round(float(x), 12)))


if __name__ == "__main__":
    main()
