"""Regression checks on constructed frames for the directional scoring contract."""
from fractions import Fraction
from io import StringIO

from score_replication import score

HEADER = "plant_id tissue_id site_id a_ref a_alt b_ref b_alt".replace(" ", "\t")


def example(rows):
    return score(StringIO(HEADER + "\n" + "\n".join("\t".join(r) for r in rows) + "\n"))


def run():
    # Depths 2 and 2, two pooled alternates: 2 of 6 equally likely subsets are one-sided.
    split = ["1", "1", "1", "1"]
    one_side = ["0", "2", "2", "0"]
    forced = ["0", "2", "0", "1"]
    rows = [
        ["p", "t", "1", *one_side],
        ["p", "t", "2", *split],
        ["q", "t", "1", *split],
        ["p", "s", "1", *forced],
        ["p", "s", "2", "", "0", "1", "0"],
        ["p", "s", "3", "1", "0", "", ""],
        ["p", "s", "4", "", "", "0", ""],
        ["p", "s", "5", "0", "0", "1", "0"],
        ["p", "s", "6", "1", "0", "1", "0"],
        ["p", "s", "7", "0", "1", "1", "0"],
    ]
    result = example(rows)
    assert result["frame"] == {"tissue_site_pairs": 10, "distinct_plants": 2, "distinct_tissues": 3}
    assert result["eligible"] == {"tissue_site_pairs": 4, "distinct_plants": 2, "distinct_tissues": 3}
    assert result["exclusive_exclusions"] == dict(missing_counts=3, zero_depth=1, zero_alternates=1, one_alternate=1)
    assert result["missing_counts_by_incomplete_half"] == dict(a_only=1, b_only=1, both=1)
    assert result["forced_comparisons"] == 1 and result["informative_comparisons"] == 3
    assert result["observed_one_sided"] == 1 and result["expected_one_sided"] == "1"
    assert result["observed_minus_expected"] == result["difference_per_eligible_comparison"] == "0"
    assert result["directional_outcome"] == "direction_failed"
    pos = example([rows[0], rows[3]])
    assert pos["directional_outcome"] == "positive_direction"
    assert Fraction(pos["observed_minus_expected"]) == Fraction(2, 3)
    assert Fraction(pos["difference_per_eligible_comparison"]) == Fraction(1, 3)
    neg = example([rows[1]])
    assert neg["directional_outcome"] == "direction_failed"
    assert Fraction(neg["observed_minus_expected"]) == Fraction(-1, 3)
    assert example([rows[3]])["directional_outcome"] == "uninformative"
    nothing = example(rows[4:])
    assert nothing["directional_outcome"] == "uninformative" and nothing["difference_per_eligible_comparison"] is None
    for malformed in [[rows[0], rows[0]], [["p", "t", "", *split]],
                      [["p", "t", "1", "", "0", "-2", "0"]], [["p", "t", "1", "1", "1", "x"]],
                      [["p", "t", "1", "1.5", "1", "0", "0"]]]:
        try:
            example(malformed)
        except ValueError:
            continue
        raise AssertionError("Malformed frame accepted")
    return "Passed positive, negative, exact tie, forced-only, excluded-only, inventory and invalid-frame checks."


if __name__ == "__main__":
    print(run())
