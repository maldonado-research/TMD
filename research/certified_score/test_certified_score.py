"""Synthetic behavioral and finite-enumeration checks; no biological evidence."""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as F
import itertools
import math
import unittest

import certified_score as cs


def fixture():
    plan = {"alpha": "1/20", "cp_bisection_bits": 36, "log_terms": 32,
            "log_fraction_bits": 64, "report_fraction_bits": 64,
            "comparator_names": ["supply", "establishment", "flexible"],
            "contexts": [
                {"id": "synthetic_c1", "weight": "2/3", "fixed_total_units": 60,
                 "tmd": ["1/4", "1/2", "1/4"],
                 "comparators": {"supply": ["1/3", "1/3", "1/3"],
                                 "establishment": ["1/5", "1/2", "3/10"],
                                 "flexible": ["3/10", "2/5", "3/10"]}},
                {"id": "synthetic_c2", "weight": "1/3", "fixed_total_units": 45,
                 "tmd": ["1/2", "3/10", "1/5"],
                 "comparators": {"supply": ["1/3", "1/3", "1/3"],
                                 "establishment": ["2/5", "2/5", "1/5"],
                                 "flexible": ["1/2", "1/4", "1/4"]}}],
            "gates": {"success_threshold": "0", "failure_mode": "any_upper_lt_threshold",
                      "failure_threshold": "-1/100"}}
    assertions = {k: True for k in (
        "independent_founder_units", "iid_conditional_multinomial_marginals_justified",
        "independent_training_and_calibration", "forecasts_weights_gates_precision_frozen",
        "fixed_stopping_no_interim_looks", "other_exclusion_and_missingness_rule_frozen",
        "complete_endpoint_ledger", "clusters_not_counted_as_independent_descendants")}
    assertions.update({
        "count_law_justification": "Synthetic independent IID categorical units; conditional W/A/M counts are multinomial given their total.",
        "founder_unit_definition": "One synthetic independently generated categorical outcome per founder; no descendants counted.",
        "sampling_and_conditioning_rule": "Fixed complete frame, condition on W/A/M. All excluded categories remain in the ledger.",
        "freeze_reference": "Synthetic verification fixture only; no real registration or collected outcome.",
        "fixed_stopping_rule": "Exactly 60 and 45 full-frame synthetic units; no interim decisions."})
    return {"schema_version": 1, "scope": cs.SCOPE, "provenance": "synthetic",
        "route_order": list(cs.ROUTES), "assumptions": assertions, "plan": plan,
        "expected_plan_sha256": cs.plan_sha256(plan), "outcomes": {
            "synthetic_c1": {"counts": [11, 29, 10], "excluded_ledger": {
                "Other": 5, "no_qualified_outcome": 3, "unresolved_classification": 1, "missing": 1}},
            "synthetic_c2": {"counts": [20, 10, 8], "excluded_ledger": {
                "Other": 3, "no_qualified_outcome": 2, "unresolved_classification": 1, "missing": 1}}}}


def rehash(doc):
    doc["expected_plan_sha256"] = cs.plan_sha256(doc["plan"])
    return doc


def counts_and_mass(n, probabilities):
    for w in range(n + 1):
        for a in range(n - w + 1):
            k = (w, a, n - w - a)
            coefficient = math.factorial(n)
            for count in k:
                coefficient //= math.factorial(count)
            mass = F(coefficient)
            for count, p in zip(k, probabilities):
                mass *= p**count
            yield k, mass


def vertices(box):
    found = set()
    for free in range(3):
        fixed = [i for i in range(3) if i != free]
        for ends in itertools.product((0, 1), repeat=2):
            p = [F(0)] * 3
            for i, end in zip(fixed, ends):
                p[i] = box[i][end]
            p[free] = 1 - sum(p)
            if all(lo <= v <= hi for v, (lo, hi) in zip(p, box)):
                found.add(tuple(p))
    return found


class CertifiedScoreTests(unittest.TestCase):
    def test_duplicate_and_nonstandard_json_are_rejected(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}'):
            with self.assertRaises(ValueError):
                cs.strict_json(raw)

    def test_type_guards_cannot_be_bypassed_by_warm_cache(self):
        cs.cp_interval(1, 0, F(1, 20), 8)
        cs.log_enclosure(F(1), 1, 8)
        for call in (lambda: cs.cp_interval(True, 0, F(1, 20), 8),
                     lambda: cs.cp_interval(1, False, F(1, 20), 8),
                     lambda: cs.log_enclosure(True, 1, 8),
                     lambda: cs.log_enclosure(F(1), True, 8)):
            with self.assertRaises(ValueError):
                call()

    def test_exact_tails_against_direct_binomial_polynomials(self):
        for n in range(1, 13):
            for p in (F(0), F(1), F(1, 10), F(1, 3), F(2, 3), F(9, 10)):
                masses = [math.comb(n, j) * p**j * (1-p)**(n-j) for j in range(n + 1)]
                self.assertEqual(sum(masses), 1)
                for k in range(n + 1):
                    self.assertEqual(cs.exact_binomial_tail(n, k, p, True), sum(masses[k:]))
                    self.assertEqual(cs.exact_binomial_tail(n, k, p, False), sum(masses[:k+1]))

    def test_cp_root_brackets_and_support_boundaries(self):
        for n in range(1, 17):
            for k in range(n + 1):
                for tail in (F(1, 600), F(1, 20)):
                    lo, hi, lower_root, upper_root = cs.cp_interval(n, k, tail, 20)
                    self.assertTrue(0 <= lo <= hi <= 1)
                    for a, b in (lower_root, upper_root):
                        self.assertLessEqual(b - a, F(1, 2**20))
                    if k == 0:
                        self.assertEqual(lo, 0)
                    else:
                        self.assertLessEqual(cs.exact_binomial_tail(n, k, lower_root[0], True), tail)
                        self.assertGreaterEqual(cs.exact_binomial_tail(n, k, lower_root[1], True), tail)
                    if k == n:
                        self.assertEqual(hi, 1)
                    else:
                        self.assertGreaterEqual(cs.exact_binomial_tail(n, k, upper_root[0], False), tail)
                        self.assertLessEqual(cs.exact_binomial_tail(n, k, upper_root[1], False), tail)

    def test_exact_small_n_binomial_coverage(self):
        alpha = F(1, 5)
        for n in range(1, 13):
            intervals = [cs.cp_interval(n, k, alpha / 2, 24)[:2] for k in range(n + 1)]
            for p in (F(0), F(1, 20), F(1, 3), F(3, 4), F(1)):
                coverage = sum(math.comb(n, k) * p**k * (1-p)**(n-k)
                               for k, (lo, hi) in enumerate(intervals) if lo <= p <= hi)
                self.assertGreaterEqual(coverage, 1 - alpha)

    def test_log_series_independent_decimal_enclosures(self):
        arguments = {F(1), F(2), F(1, 2), F(1, 2**63), F(2**63), F(2**62+1, 2**63-1)}
        arguments.update(F(a, b) for a in range(1, 20) for b in (3, 7, 19, 31))
        with localcontext() as ctx:
            ctx.prec = 110
            for x in arguments:
                lo, hi = cs.log_enclosure(x, 40, 80)
                # Certified Decimal input conversion plus correctly rounded ln:
                # bracket the input by adjacent decimals before monotone ln.
                nearest_x = Decimal(x.numerator) / Decimal(x.denominator)
                x_lo, x_hi = nearest_x.next_minus(), nearest_x.next_plus()
                independent_lo = F(x_lo.ln().next_minus())
                independent_hi = F(x_hi.ln().next_plus())
                if x == 1:
                    self.assertEqual((lo, hi), (0, 0))
                else:
                    self.assertLessEqual(lo, independent_lo)
                    self.assertGreaterEqual(hi, independent_hi)
                reciprocal_lo, reciprocal_hi = cs.log_enclosure(1/x, 40, 80)
                self.assertLessEqual(lo + reciprocal_lo, 0)
                self.assertGreaterEqual(hi + reciprocal_hi, 0)

    def test_series_remainder_shrinks_and_encloses_longer_series(self):
        for r in (F(1), F(17, 16), F(3, 2), F(2)):
            fine_lo, fine_hi = cs.positive_series_log(r, 64)
            previous_width = F(100)
            for terms in (1, 2, 4, 8, 16, 32):
                lo, hi = cs.positive_series_log(r, terms)
                self.assertLessEqual(lo, fine_lo)
                self.assertGreaterEqual(hi, fine_hi)
                self.assertLessEqual(hi - lo, previous_width)
                previous_width = hi - lo

    def test_signed_outward_dyadic_rounding(self):
        for value in (F(-100, 7), F(-1, 3), F(0), F(1, 3), F(100, 7)):
            for bits in (1, 7, 32, 64, 96):
                lo = cs.dyadic_outer(value, bits, True)
                hi = cs.dyadic_outer(value, bits, False)
                self.assertLessEqual(lo, value)
                self.assertGreaterEqual(hi, value)
                self.assertLess(hi - value, F(1, 2**bits))
                self.assertLess(value - lo, F(1, 2**bits))

    def test_exact_projection_against_enumerated_vertices(self):
        for a in range(1, 9):
            for b in range(1, 9):
                p = (F(a, 20), F(b, 20), 1-F(a+b, 20))
                box = tuple((max(F(0), v-F(1, 10)), min(F(1), v+F(1, 5))) for v in p)
                for coefficients in ((F(-2), F(0), F(3)), (F(1, 7), F(-5, 2), F(1)),
                                     (F(3), F(3), F(3))):
                    v = vertices(box)
                    expected = [sum(x*y for x, y in zip(point, coefficients)) for point in v]
                    lo, low_point = cs.exact_extreme(box, coefficients)
                    hi, high_point = cs.exact_extreme(box, coefficients, True)
                    self.assertEqual(lo, min(expected))
                    self.assertEqual(hi, max(expected))
                    self.assertIn(low_point, v)
                    self.assertIn(high_point, v)

    def test_signed_interval_coefficients_conservative(self):
        box = ((F(0), F(3, 5)), (F(1, 10), F(4, 5)), (F(0), F(4, 5)))
        intervals = ((F(-2), F(-1)), (F(-1, 4), F(1, 4)), (F(2), F(3)))
        lo, hi, _, _ = cs.score_projection(box, intervals)
        for p in vertices(box):
            for ends in itertools.product((0, 1), repeat=3):
                value = sum(p[i]*intervals[i][ends[i]] for i in range(3))
                self.assertLessEqual(lo, value)
                self.assertGreaterEqual(hi, value)

    def test_threshold_rounding_guard_and_explicit_failure(self):
        gate, tiny = F(1, 8), F(1, 2**100)
        # This strict difference vanishes at binary float precision; exact comparison retains it.
        self.assertEqual(float(gate + tiny), float(gate))
        self.assertEqual(cs.decide([(gate+tiny, gate+2*tiny)], gate, None),
                         "certified_success_at_declared_score_gate")
        rounded = (cs.dyadic_outer(gate+tiny, 64, True), cs.dyadic_outer(gate+2*tiny, 64, False))
        self.assertEqual(cs.decide([rounded], gate, None), "inconclusive_at_declared_score_gate")
        self.assertEqual(cs.decide([(gate-tiny, gate+tiny)], gate, gate),
                         "inconclusive_at_declared_score_gate")
        self.assertEqual(cs.decide([(gate-tiny, gate)], gate, gate),
                         "inconclusive_at_declared_score_gate")
        self.assertEqual(cs.decide([(gate-2*tiny, gate-tiny)], gate, gate),
                         "certified_failure_at_declared_score_gate")
        self.assertEqual(cs.decide([(gate+tiny, gate+2*tiny), (gate, gate+tiny)], gate, None),
                         "inconclusive_at_declared_score_gate")

    def test_fixture_weighted_bounds_and_ledger(self):
        result = cs.analyze(fixture())
        self.assertEqual(result["count_coordinates"], 6)
        self.assertEqual(result["per_tail_error_exact"], "1/240")
        self.assertEqual(result["decision"], "inconclusive_at_declared_score_gate")
        for name in fixture()["plan"]["comparator_names"]:
            lo = sum(F(c["weight_exact"])*F(c["comparisons"][name]["score_interval_exact"][0])
                     for c in result["contexts"])
            hi = sum(F(c["weight_exact"])*F(c["comparisons"][name]["score_interval_exact"][1])
                     for c in result["contexts"])
            self.assertEqual(result["weighted_score_intervals_exact"][name],
                             [str(cs.dyadic_outer(lo, 64, True)), str(cs.dyadic_outer(hi, 64, False))])
        self.assertEqual(result["contexts"][0]["qualifying_endpoints"], 50)
        self.assertEqual(sum(result["contexts"][0]["excluded_ledger"].values()), 10)

    def test_complete_engine_success_and_frozen_failure_gate(self):
        doc = fixture()
        row = deepcopy(doc["plan"]["contexts"][0])
        row.update(weight="1", fixed_total_units=100, tmd=["1/10", "4/5", "1/10"],
                   comparators={"supply": ["1/3", "1/3", "1/3"],
                                "establishment": ["1/5", "3/5", "1/5"],
                                "flexible": ["1/4", "1/2", "1/4"]})
        doc["plan"]["contexts"] = [row]
        doc["outcomes"] = {row["id"]: {"counts": [0, 100, 0],
                           "excluded_ledger": {k: 0 for k in cs.EXCLUDED}}}
        self.assertEqual(cs.analyze(rehash(doc))["decision"],
                         "certified_success_at_declared_score_gate")
        doc["outcomes"][row["id"]]["counts"] = [100, 0, 0]
        self.assertEqual(cs.analyze(doc)["decision"],
                         "certified_failure_at_declared_score_gate")

    def test_comparators_share_region_and_error_budget(self):
        original = fixture()
        extra = deepcopy(original)
        extra["plan"]["comparator_names"].append("additional_frozen")
        for row in extra["plan"]["contexts"]:
            row["comparators"]["additional_frozen"] = ["1/6", "2/3", "1/6"]
        result, more = cs.analyze(original), cs.analyze(rehash(extra))
        for key in ("alpha_exact", "count_coordinates", "per_tail_error_exact"):
            self.assertEqual(result[key], more[key])
        for c, more_c in zip(result["contexts"], more["contexts"]):
            self.assertEqual(c["probability_box_exact"], more_c["probability_box_exact"])
        for name in original["plan"]["comparator_names"]:
            self.assertEqual(result["weighted_score_intervals_exact"][name],
                             more["weighted_score_intervals_exact"][name])

    def test_exact_two_context_multinomial_coverage_for_all_frozen_comparators(self):
        alpha, n = F(1, 5), 6
        tail = alpha / 12
        truths = ((F(1, 10), F(3, 10), F(3, 5)), (F(1, 2), F(1, 3), F(1, 6)))
        forecasts = ((F(1, 4), F(1, 2), F(1, 4)), (F(1, 2), F(3, 10), F(1, 5)))
        comparators = ((F(1, 3),)*3, (F(1, 5), F(1, 2), F(3, 10)), (F(2, 5), F(2, 5), F(1, 5)))
        weights = (F(2, 3), F(1, 3))
        stored, truth_scores = [], [[F(0), F(0)] for _ in comparators]
        for c in range(2):
            coeff = [tuple(cs.log_enclosure(forecasts[c][i]/m[i], 32, 64) for i in range(3)) for m in comparators]
            true_coeff = [tuple(cs.log_enclosure(forecasts[c][i]/m[i], 48, 96) for i in range(3)) for m in comparators]
            for m in range(3):
                for endpoint in range(2):
                    truth_scores[m][endpoint] += weights[c] * sum(truths[c][i]*true_coeff[m][i][endpoint] for i in range(3))
            rows = []
            for counts, mass in counts_and_mass(n, truths[c]):
                box = tuple(cs.cp_interval(n, k, tail, 24)[:2] for k in counts)
                covers = all(a <= p <= b for p, (a, b) in zip(truths[c], box))
                intervals = [cs.score_projection(box, a)[:2] for a in coeff]
                rows.append((mass, covers, intervals))
            self.assertEqual(sum(r[0] for r in rows), 1)
            stored.append(rows)
        region_coverage, score_coverage = F(0), F(0)
        for row1, row2 in itertools.product(*stored):
            mass = row1[0]*row2[0]
            covered = row1[1] and row2[1]
            if covered:
                region_coverage += mass
            score_covers = True
            for m in range(3):
                lo = sum(weights[c]*row[2][m][0] for c, row in enumerate((row1, row2)))
                hi = sum(weights[c]*row[2][m][1] for c, row in enumerate((row1, row2)))
                score_covers &= lo <= truth_scores[m][0] <= truth_scores[m][1] <= hi
            if covered:
                self.assertTrue(score_covers)
            if score_covers:
                score_coverage += mass
        self.assertGreaterEqual(region_coverage, 1-alpha)
        self.assertGreaterEqual(score_coverage, region_coverage)

    def test_zero_weight_context_and_boundary_counts(self):
        doc = fixture()
        doc["plan"]["contexts"][0]["weight"] = "1"
        doc["plan"]["contexts"][1]["weight"] = "0"
        doc["outcomes"]["synthetic_c1"]["counts"] = [0, 50, 0]
        result = cs.analyze(rehash(doc))
        box = result["contexts"][0]["probability_box_exact"]
        self.assertEqual(box[0][0], "0")
        self.assertEqual(box[1][1], "1")
        self.assertEqual(box[2][0], "0")

    def test_precision_planning_is_outcome_independent(self):
        doc = fixture()
        guide = cs.precision_plan(doc["plan"], "1/2", {"synthetic_c1": "2/3", "synthetic_c2": "1/3"})
        changed = deepcopy(doc)
        changed["outcomes"]["synthetic_c1"]["counts"] = [50, 0, 0]
        self.assertEqual(guide, cs.precision_plan(changed["plan"], "1/2",
                                                {"synthetic_c1": "2/3", "synthetic_c2": "1/3"}))
        self.assertTrue(all(v["minimum_qualifying_endpoints"] >= 1
                            for v in guide["qualifying_sample_requirements"].values()))
        with self.assertRaises(ValueError):
            cs.precision_plan(doc["plan"], "1/10000000000000000000000000",
                              {"synthetic_c1": "2/3", "synthetic_c2": "1/3"})

    def test_pre_outcome_worst_case_width_for_all_small_count_vectors(self):
        plan = fixture()["plan"]
        plan["contexts"] = [deepcopy(plan["contexts"][0])]
        plan["contexts"][0]["weight"] = "1"
        guide = cs.precision_plan(plan, "1/2", {"synthetic_c1": "1"})
        n = guide["qualifying_sample_requirements"]["synthetic_c1"]["minimum_qualifying_endpoints"]
        self.assertLessEqual(n, 20)
        parsed = cs.validate_plan(plan)
        table = cs.coefficient_table(parsed)["synthetic_c1"]
        tail = F(plan["alpha"])/6
        for counts, _ in counts_and_mass(n, (F(1, 3),)*3):
            box = tuple(cs.cp_interval(n, k, tail, parsed["cp_bits"])[:2] for k in counts)
            for coeff in table.values():
                lo, hi, _, _ = cs.score_projection(box, coeff)
                lo = cs.dyadic_outer(lo, parsed["report_bits"], True)
                hi = cs.dyadic_outer(hi, parsed["report_bits"], False)
                self.assertLessEqual((hi-lo)/2, F(1, 2))

    def test_invalid_counts_probabilities_hashes_and_design_contracts(self):
        modifications = [
            lambda d: d["outcomes"]["synthetic_c1"]["counts"].__setitem__(0, True),
            lambda d: d["outcomes"]["synthetic_c1"]["counts"].__setitem__(0, 11.0),
            lambda d: d["outcomes"]["synthetic_c1"]["counts"].__setitem__(0, -1),
            lambda d: d["outcomes"]["synthetic_c1"]["counts"].__setitem__(0, 501),
            lambda d: d["outcomes"]["synthetic_c1"].__setitem__("counts", [0, 0, 0]),
            lambda d: d["outcomes"]["synthetic_c1"]["excluded_ledger"].pop("Other"),
            lambda d: d["assumptions"].__setitem__("fixed_stopping_no_interim_looks", False),
            lambda d: d.__setitem__("expected_plan_sha256", "0"*64),
        ]
        plan_modifications = [
            lambda p: p["contexts"][0]["tmd"].__setitem__(0, "0"),
            lambda p: p["contexts"][0]["tmd"].__setitem__(0, float("nan")),
            lambda p: p["contexts"][0]["tmd"].__setitem__(0, "NaN"),
            lambda p: p["contexts"][0]["tmd"].__setitem__(0, True),
            lambda p: p["contexts"][0].__setitem__("weight", "-1/3"),
            lambda p: p["contexts"][0].__setitem__("weight", "1/2"),
            lambda p: p.__setitem__("alpha", "0"),
            lambda p: p.__setitem__("alpha", "1"),
            lambda p: p.__setitem__("cp_bisection_bits", 65),
            lambda p: p.__setitem__("log_terms", 0),
            lambda p: p["gates"].__setitem__("failure_threshold", "1"),
            lambda p: p["contexts"][0]["comparators"].pop("flexible"),
        ]
        for change in modifications:
            doc = fixture()
            change(doc)
            with self.assertRaises(ValueError):
                cs.analyze(doc)
        for change in plan_modifications:
            doc = fixture()
            change(doc["plan"])
            # A nonstandard NaN cannot even form a canonical frozen manifest.
            with self.assertRaises(ValueError):
                cs.analyze(rehash(doc))

    def test_empty_regions_and_unsupported_resource_caps(self):
        for box in (((F(2, 5), F(1)),)*3, ((F(0), F(1, 5)),)*3,
                    ((F(1, 3)+F(1, 2**100), F(1)),)*3):
            with self.assertRaises(ValueError):
                cs.score_projection(box, ((F(0), F(0)),)*3)
        plan = fixture()["plan"]
        plan["contexts"] = [deepcopy(plan["contexts"][0]) for _ in range(16)]
        for i, row in enumerate(plan["contexts"]):
            row.update(id=f"c{i}", weight="1/16", fixed_total_units=500)
        with self.assertRaises(ValueError):
            cs.validate_plan(plan)
        for x in (F(0), F(-1), float("nan"), True):
            with self.assertRaises(ValueError):
                cs.log_enclosure(x)


if __name__ == "__main__":
    unittest.main()
