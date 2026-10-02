"""Independent exact-arithmetic tests for public transport robustness results.

Run with ``python -m unittest discover -s transport_robustness -v`` from the
research-progress directory.  These fixtures are synthetic and require no
private observations, network access, or third-party packages.
"""

from copy import deepcopy
from decimal import Decimal
from fractions import Fraction as F
from itertools import product
import unittest

import transport_robustness as tr


def row(lower, upper, infinity=None):
    return {
        "J_lower_exact": lower,
        "J_upper_exact": upper,
        "J_upper_infinity": infinity,
    }


def identity_routes():
    return {route: {"lower": "1", "upper": "1"} for route in "WAM"}


def synthetic_document():
    """A fully specified two-context fixture with independently obvious J=1."""
    groups = ("baseline", "selected", "baseline_controls", "selected_controls")
    contexts = []
    for name in ["public-alpha", "public-beta"]:
        context = row("1", "1")
        context["context"] = name
        context["marginal_intervals"] = {
            group: [{"lower": 1, "upper": 1, "status": "certified"}
                    for _ in range(3)] for group in groups
        }
        contexts.append(context)
    return {
        "schema_version": "transport-robustness-1",
        "assumptions": {name: True for name in tr.ASSUMPTIONS},
        "source_projection": {
            "schema_version": "0.5.0", "nominal_alpha": "1/20",
            "coordinates": 24, "per_tail_error_exact": "1/960",
            "simultaneous_coverage_lower_bound_exact": "19/20",
            "contexts": contexts,
        },
        "residual_bounds_by_context": {
            context["context"]: identity_routes() for context in contexts
        },
    }


class RationalInputTests(unittest.TestCase):
    def test_exact_integer_and_fraction_inputs(self):
        for value, expected in [(0, F(0)), (7, F(7)), (F(2, 3), F(2, 3)),
                                ("-11/7", F(-11, 7)), ("2/4", F(1, 2)),
                                ("123456789012345678901234567890/7",
                                 F(123456789012345678901234567890, 7))]:
            with self.subTest(value=value):
                self.assertEqual(tr.rational(value), expected)
                self.assertIsInstance(tr.rational(value), F)

    def test_rejects_non_exact_or_non_rational_input(self):
        for value in [True, False, 0.5, Decimal("0.5"), None, [], {},
                      "", "1.0", "1e2", "1/0", "1/-2", "+1", " 1",
                      "1 ", "1 /2", "NaN", "Infinity", "1/2/3"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    tr.rational(value)

    def test_rational_parser_does_not_impose_positive_domain(self):
        self.assertEqual(tr.rational("-3/2", label="diagnostic"), F(-3, 2))


class IntervalInputTests(unittest.TestCase):
    def test_finite_interval_with_zero_lower(self):
        self.assertEqual(tr.parse_interval(row("0", "7/3")), (F(0), F(7, 3)))

    def test_touching_point_interval_is_valid(self):
        self.assertEqual(tr.parse_interval(row("5/7", "5/7")),
                         (F(5, 7), F(5, 7)))

    def test_positive_infinity_is_explicit(self):
        self.assertEqual(tr.parse_interval(row("9/2", None, "positive")),
                         (F(9, 2), None))

    def test_metadata_does_not_change_endpoints(self):
        sample = row("2/7", "3/5")
        sample["context_id"] = "public-synthetic-example"
        self.assertEqual(tr.parse_interval(sample), (F(2, 7), F(3, 5)))

    def test_rejects_invalid_endpoint_and_infinity_encodings(self):
        malformed = [
            row("-1", "2"), row("1", "0"), row("0", "0"),
            row("0", "-2"), row(None, "2"), row("infinity", "2"),
            row("0", None), row("0", "2", "positive"),
            row("0", None, "negative"), row("0", None, True),
            row("0.5", "1"), row("0", 0.5), row(False, "1"), {},
        ]
        for sample in malformed:
            with self.subTest(sample=sample):
                with self.assertRaises(ValueError):
                    tr.parse_interval(sample)


class MultiplierTests(unittest.TestCase):
    def test_general_envelope_equals_extrema_of_all_eight_corners(self):
        routes = {
            "W": {"lower": "1/3", "upper": "7/4"},
            "A": {"lower": "2/5", "upper": "9/7"},
            "M": {"lower": "3/8", "upper": "11/6"},
        }
        corners = []
        for w, a, m in product((F(1, 3), F(7, 4)),
                               (F(2, 5), F(9, 7)),
                               (F(3, 8), F(11, 6))):
            corners.append(a * a / (w * m))
        self.assertEqual(len(corners), 8)
        self.assertEqual(tr.multiplier_bounds(routes), (min(corners), max(corners)))

    def test_fixed_route_correction_can_shift_without_containing_identity(self):
        routes = identity_routes()
        routes["A"] = {"lower": "2", "upper": "2"}
        self.assertEqual(tr.multiplier_bounds(routes), (F(4), F(4)))
        self.assertEqual(tr.widen_interval((F(4), F(8)), routes), (F(1), F(2)))

    def test_identity_routes_leave_interval_unchanged(self):
        interval = (F(2, 7), F(11, 3))
        self.assertEqual(tr.multiplier_bounds(identity_routes()), (F(1), F(1)))
        self.assertEqual(tr.widen_interval(interval, identity_routes()), interval)

    def test_aperture_is_squared_and_width_and_mass_are_reciprocal(self):
        for route, expected in [("A", (F(1, 4), F(4))),
                                ("W", (F(1, 2), F(2))),
                                ("M", (F(1, 2), F(2)))]:
            routes = identity_routes()
            routes[route] = {"lower": "1/2", "upper": "2"}
            with self.subTest(route=route):
                self.assertEqual(tr.multiplier_bounds(routes), expected)

    def test_symmetric_bounds_have_reciprocal_route_and_multiplier_endpoints(self):
        for radius in [F(1), F(3, 2), F(7, 3), F(19)]:
            routes = tr.symmetric_bounds(radius)
            with self.subTest(radius=radius):
                for route in "WAM":
                    self.assertEqual(F(routes[route]["lower"]), 1 / radius)
                    self.assertEqual(F(routes[route]["upper"]), radius)
                low, high = tr.multiplier_bounds(routes)
                self.assertEqual(low * high, 1)
                self.assertEqual((low, high), (radius ** -4, radius ** 4))

    def test_larger_symmetric_radius_can_only_expand_interval(self):
        interval = (F(3, 7), F(29, 11))
        intervals = [tr.widen_interval(interval, tr.symmetric_bounds(radius))
                     for radius in [F(1), F(5, 4), F(2), F(9)]]
        for earlier, later in zip(intervals, intervals[1:]):
            self.assertLessEqual(later[0], earlier[0])
            self.assertGreaterEqual(later[1], earlier[1])

    def test_zero_and_infinity_are_preserved_under_positive_transport(self):
        routes = tr.symmetric_bounds(F(7, 3))
        self.assertEqual(tr.widen_interval((F(0), None), routes), (F(0), None))
        lower, upper = tr.widen_interval((F(3), None), routes)
        self.assertEqual(lower, F(3) * F(3, 7) ** 4)
        self.assertIsNone(upper)

    def test_rejects_invalid_route_bounds(self):
        for lower, upper in [("0", "1"), ("-1", "1"), ("1", "0"),
                             ("2", "1"), (None, "1"), ("1/2", None),
                             ("0.5", "2"), (True, "2")]:
            routes = identity_routes()
            routes["A"] = {"lower": lower, "upper": upper}
            with self.subTest(lower=lower, upper=upper):
                with self.assertRaises(ValueError):
                    tr.multiplier_bounds(routes)

    def test_symmetric_radius_must_be_exact_and_at_least_one(self):
        for radius in [F(1, 2), 0, -1, True, "1.5", 1.5]:
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    tr.symmetric_bounds(radius)


class IntersectionTests(unittest.TestCase):
    def assert_interval(self, result, lower, upper, status):
        self.assertFalse(result["empty"])
        self.assertEqual(result["status"], status)
        self.assertEqual(F(result["J_lower_exact"]), lower)
        if upper is None:
            self.assertIsNone(result["J_upper_exact"])
            self.assertEqual(result["J_upper_infinity"], "positive")
        else:
            self.assertEqual(F(result["J_upper_exact"]), upper)
            self.assertIsNone(result["J_upper_infinity"])

    def test_finite_intersection_uses_distinct_active_contexts(self):
        result = tr.intersection([(F(1), F(10)), (F(3), F(9)),
                                  (F(2), F(4)), (F(0), None)])
        self.assert_interval(result, F(3), F(4), "compatible_finite")

    def test_closed_endpoints_can_touch(self):
        result = tr.intersection([(F(1), F(2)), (F(2), F(3))])
        self.assert_interval(result, F(2), F(2), "compatible_finite")

    def test_disjoint_intervals_reject(self):
        result = tr.intersection([(F(1), F(2)), (F(3), None)])
        self.assertTrue(result["empty"])
        self.assertEqual(result["status"], "reject")

    def test_all_infinite_upper_bounds_produce_unbounded_intersection(self):
        self.assert_interval(tr.intersection([(F(0), None), (F(7), None)]),
                             F(7), None, "compatible_unbounded")

    def test_zero_lower_is_unbounded_on_the_log_scale(self):
        self.assert_interval(tr.intersection([(F(0), F(3)), (F(0), F(2))]),
                             F(0), F(2), "compatible_unbounded")

    def test_empty_input_and_invalid_direct_intervals_are_rejected(self):
        for intervals in [[], [(F(-1), F(2))], [(F(0), F(0))],
                          [(F(3), F(2))], [(0.5, F(2))], [(F(0),)]]:
            with self.subTest(intervals=intervals):
                with self.assertRaises(ValueError):
                    tr.intersection(intervals)

    def test_single_context_remains_descriptive(self):
        for interval in [(F(1), F(3)), (F(0), None)]:
            with self.subTest(interval=interval):
                self.assert_interval(tr.intersection([interval]),
                                     interval[0], interval[1], "descriptive_only")

    def test_different_context_transports_can_restore_compatibility(self):
        intervals = [(F(1), F(2)), (F(8), F(16))]
        self.assertTrue(tr.intersection(intervals)["empty"])
        first_routes = identity_routes()
        first_routes["A"] = {"lower": "1/2", "upper": "1"}
        second_routes = identity_routes()
        second_routes["A"] = {"lower": "1", "upper": "2"}
        widened = [tr.widen_interval(intervals[0], first_routes),
                   tr.widen_interval(intervals[1], second_routes)]
        self.assertEqual(widened, [(F(1), F(8)), (F(2), F(16))])
        self.assert_interval(tr.intersection(widened), F(2), F(8),
                             "compatible_finite")


class ThresholdTests(unittest.TestCase):
    @staticmethod
    def transported(intervals, radius):
        routes = tr.symmetric_bounds(radius)
        return [tr.widen_interval(interval, routes) for interval in intervals]

    def test_exact_threshold_restores_compatibility_at_equality(self):
        intervals = [(F(1), F(2)), (F(512), F(1024))]
        result = tr.threshold_bracket(intervals)
        self.assertEqual(F(result["power_ratio_exact"]), F(256))
        self.assertEqual(F(result["R_upper_exact"]), F(2))
        self.assertIn(result["status"], ("exact", "certified_bracket"))
        at_threshold = tr.intersection(self.transported(intervals, F(2)))
        self.assertFalse(at_threshold["empty"])
        self.assertEqual(F(at_threshold["J_lower_exact"]), F(32))
        self.assertEqual(F(at_threshold["J_upper_exact"]), F(32))
        for radius in [F(1), F(3, 2), F(199, 100)]:
            with self.subTest(radius=radius):
                self.assertTrue(tr.intersection(self.transported(intervals, radius))["empty"])

    def test_nonroot_threshold_has_exact_rejection_and_compatibility_witnesses(self):
        intervals = [(F(0), F(1)), (F(2), None)]
        result = tr.threshold_bracket(intervals, bits=48)
        self.assertEqual(result["status"], "certified_bracket")
        low, high = F(result["R_lower_exact"]), F(result["R_upper_exact"])
        self.assertEqual(F(result["power_ratio_exact"]), F(2))
        self.assertGreaterEqual(low, 1)
        self.assertLess(low, high)
        self.assertLess(low ** 8, F(2))
        self.assertGreater(high ** 8, F(2))
        self.assertLess(high - low, F(1, 10 ** 12))
        self.assertTrue(tr.intersection(self.transported(intervals, low))["empty"])
        self.assertFalse(tr.intersection(self.transported(intervals, high))["empty"])

    def test_rational_noninteger_threshold(self):
        ratio = F(6561, 256)
        result = tr.threshold_bracket([(F(0), F(1)), (ratio, None)])
        low, high = F(result["R_lower_exact"]), F(result["R_upper_exact"])
        self.assertEqual(F(result["power_ratio_exact"]), ratio)
        self.assertLessEqual(low, F(3, 2))
        self.assertGreaterEqual(high, F(3, 2))
        if result["status"] == "exact":
            self.assertEqual((low, high), (F(3, 2), F(3, 2)))
        else:
            self.assertLess(low ** 8, ratio)
            self.assertGreaterEqual(high ** 8, ratio)

    def test_already_compatible_including_zero_and_infinity(self):
        for intervals in [[(F(1), F(2)), (F(2), F(3))],
                          [(F(0), None), (F(7), None)],
                          [(F(0), F(1)), (F(0), F(2))]]:
            with self.subTest(intervals=intervals):
                self.assertEqual(tr.threshold_bracket(intervals)["status"],
                                 "already_compatible")

    def test_single_context_is_descriptive_not_cross_context_evidence(self):
        for interval in [(F(1), F(3)), (F(0), None)]:
            with self.subTest(interval=interval):
                self.assertEqual(tr.threshold_bracket([interval])["status"],
                                 "descriptive_only")

    def test_threshold_is_invariant_to_units_order_duplication_and_loose_context(self):
        base = [(F(1, 3), F(7, 5)), (F(13, 3), F(20))]
        scale = F(11, 7)
        variants = [list(reversed(base)), base + base,
                    base + [(F(0), None)],
                    [(low * scale, high * scale) for low, high in base]]
        expected_ratio = F(65, 21)
        for intervals in [base] + variants:
            result = tr.threshold_bracket(intervals, bits=48)
            with self.subTest(intervals=intervals):
                self.assertEqual(F(result["power_ratio_exact"]), expected_ratio)
                low = F(result["R_lower_exact"])
                high = F(result["R_upper_exact"])
                self.assertLess(low ** 8, expected_ratio)
                self.assertGreaterEqual(high ** 8, expected_ratio)

    def test_finer_precision_keeps_certificate_and_tightens_bracket(self):
        intervals = [(F(0), F(1)), (F(3), None)]
        coarse = tr.threshold_bracket(intervals, bits=16)
        fine = tr.threshold_bracket(intervals, bits=64)
        coarse_low, coarse_high = F(coarse["R_lower_exact"]), F(coarse["R_upper_exact"])
        fine_low, fine_high = F(fine["R_lower_exact"]), F(fine["R_upper_exact"])
        self.assertLess(fine_high - fine_low, coarse_high - coarse_low)
        self.assertLess(fine_low ** 8, F(3))
        self.assertGreater(fine_high ** 8, F(3))

    def test_precision_requires_bounded_positive_integer(self):
        intervals = [(F(0), F(1)), (F(3), None)]
        for bits in [0, -1, 513, True, "48", 1.5]:
            with self.subTest(bits=bits):
                with self.assertRaises(ValueError):
                    tr.threshold_bracket(intervals, bits=bits)


class StoredProjectionContractTests(unittest.TestCase):
    def test_valid_synthetic_document_rechecks_arithmetic_and_records_conditional_scope(self):
        result = tr.evaluate(synthetic_document())
        self.assertEqual(result["status"], "compatible_finite")
        self.assertEqual(result["decision"], "no_shared_finite_theta_departure_established")
        self.assertEqual(F(result["conditional_simultaneous_coverage_lower_bound_exact"]),
                         F(19, 20))
        self.assertTrue(result["source_probability_projection_arithmetic_rechecked"])
        self.assertFalse(result["source_exact_transport_assertion_adopted"])
        for context in result["contexts"]:
            self.assertEqual(context["observable_J_interval"], row("1", "1"))
            self.assertEqual(context["biological_J_interval"], row("1", "1"))

    def test_each_bounded_transport_assumption_must_be_explicitly_true(self):
        for assumption in tr.ASSUMPTIONS:
            for replacement in [False, 1, "true", None]:
                document = synthetic_document()
                document["assumptions"][assumption] = replacement
                with self.subTest(assumption=assumption, value=replacement):
                    with self.assertRaises(ValueError):
                        tr.evaluate(document)
            document = synthetic_document()
            del document["assumptions"][assumption]
            with self.subTest(missing=assumption):
                with self.assertRaises(ValueError):
                    tr.evaluate(document)

    def test_whole_assumption_declaration_is_required(self):
        document = synthetic_document()
        del document["assumptions"]
        with self.assertRaises(ValueError):
            tr.evaluate(document)

    def test_residual_context_labels_must_match_source_exactly(self):
        for labels in [("public-alpha",), ("public-alpha", "wrong-label"),
                       ("public-alpha", "public-beta", "extra-label")]:
            document = synthetic_document()
            document["residual_bounds_by_context"] = {
                label: identity_routes() for label in labels
            }
            with self.subTest(labels=labels):
                with self.assertRaises(ValueError):
                    tr.evaluate(document)

    def test_source_coordinate_tail_and_coverage_metadata_must_agree(self):
        for key, value in [("coordinates", 12), ("coordinates", 25),
                           ("per_tail_error_exact", "1/480"),
                           ("simultaneous_coverage_lower_bound_exact", "99/100"),
                           ("nominal_alpha", "0"), ("nominal_alpha", "1"),
                           ("nominal_alpha", "0.05")]:
            source = synthetic_document()["source_projection"]
            source[key] = value
            with self.subTest(key=key, value=value):
                with self.assertRaises(ValueError):
                    tr.parse_projection(source)

    def test_source_context_names_must_be_unique_and_nonempty(self):
        for name in ["public-alpha", "", " public-beta", None]:
            source = synthetic_document()["source_projection"]
            source["contexts"][1]["context"] = name
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    tr.parse_projection(source)

    def test_stored_exact_interval_cannot_disagree_with_marginal_arithmetic(self):
        document = synthetic_document()
        document["source_projection"]["contexts"][0]["J_upper_exact"] = "2"
        with self.assertRaises(ValueError):
            tr.evaluate(document)

    def test_saved_marginal_status_does_not_replace_endpoint_validation(self):
        for lower, upper in [(-1, 1), (0, 0), (1, 2), (True, 1)]:
            document = synthetic_document()
            marginal = document["source_projection"]["contexts"][0]["marginal_intervals"]["baseline"][0]
            marginal.update(lower=lower, upper=upper)
            with self.subTest(lower=lower, upper=upper):
                with self.assertRaises(ValueError):
                    tr.evaluate(document)

    def test_no_observations_preserves_vacuous_probability_information(self):
        for selected_groups in [("baseline",),
                                ("baseline", "selected", "baseline_controls", "selected_controls")]:
            for include_certificates in [False, True]:
                document = synthetic_document()
                for context in document["source_projection"]["contexts"]:
                    context.update(row("0", None, "positive"))
                    for group in selected_groups:
                        for marginal in context["marginal_intervals"][group]:
                            marginal.update(lower=0, upper=1, status="no_observations")
                            if include_certificates:
                                marginal["certificates"] = []
                with self.subTest(groups=selected_groups, certificates=include_certificates):
                    result = tr.evaluate(document)
                    self.assertEqual(result["status"], "compatible_unbounded")
                    self.assertFalse(result["shared_biological_J_intersection"]["empty"])
                    for context in result["contexts"]:
                        self.assertEqual(context["biological_J_interval"], row("0", None, "positive"))

    def test_no_observations_cannot_claim_a_narrower_probability_interval(self):
        document = synthetic_document()
        for context in document["source_projection"]["contexts"]:
            context.update(row("0", None, "positive"))
            for group in context["marginal_intervals"].values():
                for marginal in group:
                    marginal.update(lower=0, upper=1, status="no_observations", certificates=[])
        # Other [0,1] factors keep the stored J=[0,infinity] arithmetic valid;
        # rejection must come from the false information claimed by this row.
        marginal = document["source_projection"]["contexts"][0]["marginal_intervals"]["baseline"][0]
        marginal.update(lower=1, upper=1)
        with self.assertRaises(ValueError):
            tr.evaluate(document)

    def test_evaluation_preserves_input_document(self):
        document = synthetic_document()
        original = deepcopy(document)
        tr.evaluate(document)
        self.assertEqual(document, original)


if __name__ == "__main__":
    unittest.main()
