"""Independently enumerate every admissible hidden-positive count on the saved rosters."""
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def attainable(grouped, lower=0, upper=None):
    totals = {0}
    for both, a, b, zero, copies in grouped:
        counts = [h for h in range(zero + 1)
                  if lower * a * b <= both * h and (upper is None or both * h <= upper * a * b)]
        for _ in range(copies):
            totals = {i + j for i in totals for j in counts}
    return totals


def verify(receipt, reported):
    s = receipt["site_tables"]
    t = receipt["tissue_tables"]
    pooled = [50, 9, 12, 669]
    for bins, units, width in [(s, 37, 20), (t, 20, 37)]:
        assert sum(r[-1] for r in bins) == units and all(sum(r[:4]) == width for r in bins)
        assert [sum(r[i] * r[-1] for r in bins) for i in range(4)] == pooled
    groups = {"pooled": [[*pooled, 1]], "within_sites": s, "within_tissues": t}
    checked = 0
    for key, band in [("hidden_counts_by_one_sided_cap", False), ("hidden_counts_by_two_sided_band", True)]:
        for cap, results in reported[key].items():
            high = Fraction(cap)
            low = 1 / high if band else 0
            for name, rows in groups.items():
                support = attainable(rows, low, high)
                endpoints = results[name]
                assert (not support and endpoints is None) or support == set(range(endpoints[0], endpoints[1] + 1))
                checked += 1
    for name, rows in groups.items():
        hs = attainable(rows, 0, 1)
        stats = reported["cap_one"][name]
        measures = {
            "missed_by_a_fraction": [Fraction(12 + h, 71 + h) for h in hs],
            "missed_by_b_fraction": [Fraction(9 + h, 71 + h) for h in hs],
            "missed_by_exactly_one_fraction": [Fraction(21, 71 + h) for h in hs],
            "missed_by_both_fraction": [Fraction(h, 71 + h) for h in hs],
            "detected_by_either_fraction": [Fraction(71, 71 + h) for h in hs],
        }
        for k, values in measures.items():
            assert [str(min(values)), str(max(values))] == stats[k]
        assert stats["true_site_tissue_count"] == [71 + min(hs), 71 + max(hs)]
        assert stats["missed_by_both_count"] == [min(hs), max(hs)]
        # A cap larger than any realizable finite cross-product ratio saturates the finite limit.
        assert max(attainable(rows, 0, 740 ** 2)) == reported["largest_hidden_count_for_arbitrarily_large_finite_upper_cap"][name]
        assert attainable(rows) == set(range(670))
    witness = reported["cap_one_maximum_sitewise_witness_nonzero_terms"]
    expected = {(tuple(r[:4]), r[4]): max(h for h in range(r[3] + 1) if r[0] * h <= r[1] * r[2]) for r in s}
    got = {(tuple(row["table"]), row["sites"]): row["h_per_site"] for row in witness}
    assert got == {key: value for key, value in expected.items() if value}
    return {"attainable_integer_sets_checked": checked, "stratifications_checked": len(groups),
            "rate_endpoint_pairs_at_cap_one_checked": len(groups) * len(measures),
            "largest_within_site_cap_one_total": sum(n * h for (table, n), h in got.items())}


if __name__ == "__main__":
    report = verify(json.loads((HERE / "site_calls.json").read_bytes()),
                    json.loads((HERE / "shared_miss_result.json").read_bytes()))
    print(json.dumps(report, indent=2))
