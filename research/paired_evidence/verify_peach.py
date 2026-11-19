"""Check the published peach overlap calculations without the source workbooks."""
from fractions import Fraction
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def verify(data):
    sites = data["across_sites"]
    hist = sites["site_overlap_histogram"]
    # Expand anonymous sites only. No named tissue or locus is needed for these checks.
    roster = [(row["both_positive_pairs"], row["either_positive_pairs"])
              for row in hist for _ in range(row["number_of_sites"])]
    n_pairs = data["frame"]["split_tissue_pairs"]
    n_sites = data["frame"]["published_flower_sites"]
    assert n_pairs == 20 and len(roster) == n_sites == 37
    assert all(0 <= both <= either <= n_pairs for both, either in roster)
    cells = data["pair_by_site_calls"]
    assert cells == {"both_positive": 50, "a_only_positive": 9, "b_only_positive": 12,
                     "neither_positive": 669, "total": 740}
    both = sum(i for i, u in roster)
    union = sum(u for i, u in roster)
    assert both == cells["both_positive"] and union - both == cells["a_only_positive"] + cells["b_only_positive"]
    assert cells["total"] == n_pairs * n_sites and cells["total"] - union == cells["neither_positive"]
    ratios = [Fraction(i, u) for i, u in roster if u]
    wide = [(i, u) for i, u in roster if u == n_pairs]
    assert n_sites - len(ratios) == sites["no_positive_in_split_tissues"] == 15
    assert len(ratios) == sites["at_least_one_positive_in_split_tissues"] == 22
    assert sum(r > 0 for r in ratios) == sites["at_least_one_pair_with_both_positive"] == 11
    equal_site = sum(ratios) / len(ratios)
    assert equal_site == Fraction(sites["mean_intersection_over_union_weighting_each_nonempty_site_equally"])
    for group, key in [(wide, "observed_in_either_subsample_in_all_pairs"),
                       ([(i, u) for i, u in roster if u < n_pairs], "remaining_sites")]:
        assert sites[key] == {"sites": len(group), "intersection": sum(i for i, u in group),
                              "union": sum(u for i, u in group)}
    agreement = {k: Fraction(v) for k, v in data["agreement"].items()}
    assert agreement == {
        "matching_calls_over_all": Fraction(both + cells["neither_positive"], n_pairs * n_sites),
        "both_positive_over_either_positive": Fraction(both, union),
        "b_positive_given_a_positive": Fraction(both, both + cells["a_only_positive"]),
        "a_positive_given_b_positive": Fraction(both, both + cells["b_only_positive"]),
    }
    adjudicated = data["source_adjudication_of_discordances"]
    assert adjudicated["source_false_negative"] + adjudicated["source_false_positive"] == union - both
    return {"site_bins": len(hist), "site_tissue_pairs": n_pairs * n_sites,
            "double_positive_over_either_positive": str(Fraction(both, union)),
            "mean_site_overlap": str(equal_site)}


if __name__ == "__main__":
    print(json.dumps(verify(json.loads((HERE / "peach_receipt.json").read_bytes())), indent=2))
