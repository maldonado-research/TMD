"""Independent exhaustive oracle for the paired bounds, using original loss definitions."""

import unittest
from fractions import Fraction as F
from itertools import product
from math import prod

from score_bounds import score_unit, summarize_units


def loss(p, y):
    return sum((w - int(k == y)) ** 2 for k, w in p.items())


def top_hit(p, y, random_ties):
    ranks = [k for k in p if all(p[k] >= w for w in p.values())]
    if not random_ties and len(ranks) != 1:
        return F(0)
    return F(int(y in ranks), len(ranks))


class PairedBoundsTest(unittest.TestCase):
    def test_original_losses_over_all_completions(self):
        u = dict.fromkeys("ABCDEF", F(1, 6))
        p = dict(zip("ABCDEF", [F(v, 20) for v in (7, 4, 4, 3, 1, 1)]))
        q = dict(zip("ABCDEF", [F(v, 20) for v in (3, 6, 6, 2, 1, 2)]))
        rows = [("AAB", p, u), ("ABCE", q, p), ("E", u, q)]
        bounds = summarize_units(score_unit(*row) for row in rows)
        observed = {m: [] for m in ("unique_top_hit", "unique_top_gain", "randomized_top_gain",
                                    "brier_gain", "log_gain")}
        for ys in product(*(sorted(set(s)) for s, _, _ in rows)):
            cases = [(y, pp, qq) for y, (_, pp, qq) in zip(ys, rows)]
            observed["unique_top_hit"].append(sum(top_hit(pp, y, False) for y, pp, _ in cases) / len(rows))
            for rnd, metric in [(False, "unique_top_gain"), (True, "randomized_top_gain")]:
                observed[metric].append(sum(top_hit(pp, y, rnd) - top_hit(qq, y, rnd)
                                            for y, pp, qq in cases) / len(rows))
            observed["brier_gain"].append(sum(loss(qq, y) - loss(pp, y) for y, pp, qq in cases) / len(rows))
            observed["log_gain"].append(prod(pp[y] / qq[y] for y, pp, qq in cases))
        self.assertEqual(bounds["class_completions"], 8)
        for metric, values in observed.items():
            for key, extreme in (("lower", min), ("upper", max)):
                found = bounds["mean_" + metric][key]
                if metric == "log_gain":
                    found = found["product_ratio"]
                self.assertEqual(F(found), extreme(values))

    def test_identical_forecasts_share_hidden_outcome(self):
        p = {"a": F(3, 4), "b": F(1, 4)}
        bounds = summarize_units([score_unit("ab", p, p)])
        self.assertEqual(bounds["mean_brier_gain"], {"lower": "0", "upper": "0"})
        self.assertEqual(bounds["mean_log_gain"]["lower"]["product_ratio"], "1")
        self.assertEqual(bounds["mean_log_gain"]["upper"]["product_ratio"], "1")

    def test_degenerate_and_invalid_inputs(self):
        u = {"a": F(1, 2), "b": F(1, 2)}
        self.assertEqual(score_unit("aa", u, u)["a"].randomized_top_gain, 0)
        for candidates, p, q in [([], u, u), ("ac", u, u), ("a", {"a": 1}, u),
                                  ("a", {"a": F(1, 3), "b": F(1, 3)}, u),
                                  ("a", {"a": 0, "b": 1}, u)]:
            with self.assertRaises(ValueError):
                score_unit(candidates, p, q)
        with self.assertRaises(ValueError):
            summarize_units([])


if __name__ == "__main__":
    unittest.main()
