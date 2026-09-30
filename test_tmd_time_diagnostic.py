"""Analytical oracles and failure cases for TMD time diagnostic. MIT License."""
import math
import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch
from tmd_time_diagnostic import analyze, aalen_johansen, contingency_deviance, main, make_tables, validate_rows


def row(rid, time, route="A", context="c", event=1):
    return dict(replicate_id=str(rid), context=context, time=str(time),
                event=str(event), route=route, provenance="synthetic")


class TimeDiagnosticTests(unittest.TestCase):
    def test_analytical_balanced_null(self):
        self.assertAlmostEqual(contingency_deviance([[8, 8], [8, 8]]), 0)

    def test_analytical_separation(self):
        self.assertAlmostEqual(contingency_deviance([[20, 0], [0, 20]]), 80 * math.log(2))

    def test_unequal_margins_independence(self):
        self.assertAlmostEqual(contingency_deviance([[2, 6], [5, 15]]), 0)

    def test_exposure_censoring_and_cut_boundary(self):
        rows = validate_rows([row(1, 1), row(2, 2, "B"), row(3, 3, "", event=0)], ["A", "B"])
        tables, exposures, _, _ = make_tables(rows, ["A", "B"], [1, 2])
        self.assertEqual(tables["c"], [[1, 0], [0, 1], [0, 0]])
        self.assertEqual(exposures["c"], [3, 2, 1])

    def test_cumulative_incidence_censoring(self):
        rows = validate_rows([row(1, 1), row(2, 2, "B"), row(3, 1, "", event=0)], ["A", "B"])
        out = aalen_johansen(rows, ["A", "B"])
        self.assertAlmostEqual(out[-1]["cumulative_incidence"]["A"], 1 / 3)
        self.assertAlmostEqual(out[-1]["cumulative_incidence"]["B"], 2 / 3)
        self.assertAlmostEqual(out[-1]["survival"], 0)

    def test_single_route_and_empty_events_uninformative(self):
        r = analyze([row(1, 1), row(2, 3)], ["A", "B"], [2], 19)
        self.assertIsNone(r["conditional_permutation_p"])
        r = analyze([row(1, 1, "", event=0)], ["A", "B"], [2], 19)
        self.assertIsNone(r["conditional_permutation_p"])
        self.assertIsNone(r["contexts"]["c"]["observed_event_proportions"]["A"])
        self.assertIsNone(r["contexts"]["c"]["common_clock_route_estimates"]["A"])

    def test_separated_routes_rejected_and_deterministic_seed(self):
        rows = [row(i, 1, "A") for i in range(20)] + [row(i + 20, 3, "B") for i in range(20)]
        r = analyze(rows, ["A", "B"], [2], 199, 14)
        self.assertLess(r["conditional_permutation_p"], .02)
        self.assertEqual(r, analyze(rows, ["A", "B"], [2], 199, 14))

    def test_context_stratification_avoids_spurious_pooled_signal(self):
        rows = []
        for c, probs in [("early", (18, 2)), ("late", (2, 18))]:
            for t in (1, 3):
                for route, n in zip(("A", "B"), probs):
                    rows += [row(len(rows) + j, t, route, c) for j in range(n)]
        r = analyze(rows, ["A", "B"], [2], 99)
        self.assertAlmostEqual(r["statistic_deviance"], 0)
        self.assertEqual(r["conditional_permutation_p"], 1)

    def test_invalid_records_and_cuts(self):
        invalid = [[row(1, 0)], [row(1, float("nan"))], [row(1, float("inf"))],
                   [row(1, -1)], [row(1, 1, "X")], [row(1, 1, "A", event=0)],
                   [row(1, 1), row(1, 2)]]
        for rows in invalid:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                analyze(rows, ["A", "B"], [2], 9)
        for cuts in [[2, 1], [1, 1], [float("inf")], [-1]]:
            with self.subTest(cuts=cuts), self.assertRaises(ValueError):
                analyze([row(1, 1)], ["A", "B"], cuts, 9)

    def test_time_rescaling_preserves_test_and_scales_hazards(self):
        rows = [row(1, 1, "A"), row(2, 3, "B"), row(3, 4, "", event=0)]
        scaled = [dict(r, time=str(float(r["time"]) * 10)) for r in rows]
        a = analyze(rows, ["A", "B"], [2], 19)
        b = analyze(scaled, ["A", "B"], [20], 19)
        self.assertEqual(a["conditional_permutation_p"], b["conditional_permutation_p"])
        self.assertAlmostEqual(a["contexts"]["c"]["hazards"][0]["free_hazards"]["A"] / 10,
                               b["contexts"]["c"]["hazards"][0]["free_hazards"]["A"])

    def test_global_identifiers_reject_same_replicate_in_different_contexts(self):
        with self.assertRaisesRegex(ValueError, "global replicate identifier"):
            analyze([row(1, 1, context="one"), row(1, 3, context="two")], ["A", "B"], [2], 9)

    def test_unsupported_design_fields_are_not_silently_dropped(self):
        invalid = [dict(entry_time=1), dict(entry_time="nan"), dict(entry_time=""),
                   dict(observation_type="detection_time"), dict(observation_type="endpoint_dominance"),
                   dict(observation_type="interval_censored"), dict(observation_type=""),
                   dict(cluster_id="shared-culture"), dict(cluster_id=17)]
        for extra in invalid:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                analyze([dict(row(1, 3), **extra)], ["A", "B"], [2], 9)
        bare = [row(1, 1, "A"), row(2, 3, "B"), row(3, 4, "", event=0)]
        explicit = [dict(r, entry_time="0", observation_type="first_successful_arrival", cluster_id=" ")
                    for r in bare]
        self.assertEqual(analyze(bare, ["A", "B"], [2], 19, 3),
                         analyze(explicit, ["A", "B"], [2], 19, 3))

    def test_missing_or_malformed_cells_raise_value_errors(self):
        for key in ("replicate_id", "context", "time", "event", "route", "provenance"):
            missing = row(1, 1)
            del missing[key]
            for bad in (missing, dict(row(1, 1), **{key: None})):
                with self.subTest(key=key, bad=bad), self.assertRaises(ValueError):
                    analyze([bad], ["A", "B"], [2], 9)
        malformed = [None, {None: ["surplus"], **row(1, 1)},
                     dict(row(1, 1), time="not-a-number"), dict(row(1, 1), route=17)]
        for bad in malformed:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                analyze([bad], ["A", "B"], [2], 9)
        csv_cases = ["replicate_id,context,time,event,route,provenance\n1,c,1,1,A\n",
                     "replicate_id,context,time,event,route,provenance\n1,c,1,1,A,synthetic,extra\n"]
        for text in csv_cases:
            with self.subTest(csv=text), self.assertRaises(ValueError):
                analyze(list(csv.DictReader(io.StringIO(text))), ["A", "B"], [2], 9)

    def test_cli_malformed_csv_is_a_clean_input_error(self):
        cases = ["replicate_id,context,time,time,event,route,provenance\n1,c,1,1,1,A,synthetic\n",
                 "replicate_id,context,time,event,route,provenance\n1,c,1,1,A\n",
                 "replicate_id,context,time,event,route,provenance\n1,c,1,1,A,synthetic,extra\n",
                 'replicate_id,context,time,event,route,provenance\n1,c,1,1,A,"unterminated\n']
        with tempfile.TemporaryDirectory() as tmp:
            path, out = Path(tmp) / "input.csv", Path(tmp) / "result.json"
            args = ["tmd_time_diagnostic.py", "--csv", str(path), "--routes", "A,B", "--cuts", "2",
                    "--time-unit", "hours", "--cuts-plan", "fixed test cuts", "--event-definition",
                    "first_successful_arrival", "--independent-replicates", "--independent-censoring",
                    "--permutations", "9", "--output", str(out)]
            for text in cases:
                path.write_text(text)
                stderr = io.StringIO()
                with self.subTest(csv=text), patch.object(sys, "argv", args), redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as exit_error:
                        main()
                    self.assertEqual(exit_error.exception.code, 2)
                    self.assertIn("error:", stderr.getvalue())
                    self.assertNotIn("Traceback", stderr.getvalue())
                    self.assertFalse(out.exists())

    def test_mixed_provenance_is_flagged_without_changing_the_calculation(self):
        rows = [row(1, 1, "A"), row(2, 3, "B"), row(3, 4, "", event=0)]
        pure = analyze(rows, ["A", "B"], [2], 19, 4)
        mixed = analyze([rows[0], dict(rows[1], provenance="observed"), rows[2]], ["A", "B"], [2], 19, 4)
        self.assertFalse(pure["mixed_provenance"])
        self.assertIsNone(pure["provenance_warning"])
        self.assertTrue(mixed["mixed_provenance"])
        self.assertEqual(mixed["evidence_kind"], "mixed_provenance_requires_separate_evidence_review")
        self.assertIn("not a homogeneous empirical evidence sample", mixed["provenance_warning"])
        self.assertEqual(pure["statistic_deviance"], mixed["statistic_deviance"])
        self.assertEqual(pure["conditional_permutation_p"], mixed["conditional_permutation_p"])

    def test_censored_full_likelihood_matches_route_time_deviance(self):
        rows = []
        for t, counts in ((.5, (8, 2)), (1.5, (2, 8))):
            for route, count in zip(("A", "B"), counts):
                rows.extend([row(len(rows) + j, t, route) for j in range(count)])
        rows.extend([row("cens1", 1.25, "", event=0), row("cens2", 3, "", event=0)])
        result = analyze(rows, ["A", "B"], [1], 9)
        # Independent survival likelihood oracle for E=(17,7.25), p=(.5,.5).
        log_free = log_common = 0.0
        for exposure, counts in ((17, (8, 2)), (7.25, (2, 8))):
            for count in counts:
                free_rate, common_rate = count / exposure, 5 / exposure
                log_free += count * math.log(free_rate) - exposure * free_rate
                log_common += count * math.log(common_rate) - exposure * common_rate
        self.assertAlmostEqual(2 * (log_free - log_common), 7.7097902808703)
        self.assertAlmostEqual(result["statistic_deviance"], 2 * (log_free - log_common))
        self.assertEqual(result["contexts"]["c"]["observed_event_proportions"], {"A": .5, "B": .5})
        self.assertEqual(result["contexts"]["c"]["common_clock_route_estimates"], {"A": .5, "B": .5})


if __name__ == "__main__":
    unittest.main()
