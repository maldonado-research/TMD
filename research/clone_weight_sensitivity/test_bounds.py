"""Independent finite enumeration and constructive tests for original R41 code.

Enumeration generates actual bounded compositions of integer row totals. It
does not calculate the ceil-count formulas used by the implementation.
"""

from fractions import Fraction
from functools import lru_cache
from itertools import product
import unittest

from bounds import clone_cdf_envelope, endpoint_realizations, finite_clone_cdf_bounds


@lru_cache(maxsize=None)
def ordered_partitions(total, cap):
    """Every ordered positive bounded composition of total; zero has ()."""
    if total == 0:
        return ((),)
    return tuple(
        (part,) + tail
        for part in range(1, min(total, cap) + 1)
        for tail in ordered_partitions(total - part, cap)
    )


def enumerated_cdfs(total, left_rows, cap):
    by_clones = {}
    for left, right in product(
        ordered_partitions(left_rows, cap),
        ordered_partitions(total - left_rows, cap),
    ):
        count = len(left) + len(right)
        by_clones.setdefault(count, set()).add(Fraction(len(left), count))
    return by_clones


class ExactBoundsTests(unittest.TestCase):
    def test_against_all_ordered_partitions(self):
        # Includes edge thresholds, K=1, feasible and infeasible J.
        for cap in (1, 2, 3, 4):
            for total in range(1, 11):
                for left_rows in range(total + 1):
                    oracle = enumerated_cdfs(total, left_rows, cap)
                    all_values = set().union(*oracle.values())
                    actual = finite_clone_cdf_bounds(total, left_rows, cap)
                    self.assertEqual((actual.lower, actual.upper),
                                     (min(all_values), max(all_values)))
                    for count in range(1, total + 2):
                        with self.subTest(K=cap, N=total, k=left_rows, J=count):
                            if count not in oracle:
                                with self.assertRaises(ValueError):
                                    finite_clone_cdf_bounds(total, left_rows, cap, count)
                                continue
                            actual = finite_clone_cdf_bounds(total, left_rows, cap, count)
                            self.assertEqual((actual.lower, actual.upper),
                                             (min(oracle[count]), max(oracle[count])))

    def test_constructed_endpoints_are_valid_and_attain_bounds(self):
        for cap in (1, 2, 3, 5):
            for total in range(1, 31):
                for left_rows in range(total + 1):
                    counts = [None, 1, max(1, total // 2), total]
                    for count in counts:
                        try:
                            expected = finite_clone_cdf_bounds(total, left_rows, cap, count)
                        except ValueError:
                            with self.assertRaises(ValueError):
                                endpoint_realizations(total, left_rows, cap, count)
                            continue
                        low, high = endpoint_realizations(total, left_rows, cap, count)
                        for witness in (low, high):
                            self.assertEqual(witness.row_count, total)
                            self.assertEqual(sum(witness.left), left_rows)
                            self.assertEqual(witness.row_cdf, Fraction(left_rows, total))
                            self.assertTrue(all(1 <= r <= cap for r in witness.left + witness.right))
                            if count is not None:
                                self.assertEqual(witness.clone_count, count)
                        self.assertEqual(low.clone_cdf, expected.lower)
                        self.assertEqual(high.clone_cdf, expected.upper)

    def test_envelope_contains_enumerated_populations(self):
        for cap in (1, 2, 3, 4):
            for total in range(1, 11):
                for left_rows in range(total + 1):
                    envelope = clone_cdf_envelope(Fraction(left_rows, total), cap)
                    for values in enumerated_cdfs(total, left_rows, cap).values():
                        for value in values:
                            self.assertLessEqual(envelope.lower, value)
                            self.assertLessEqual(value, envelope.upper)

    def test_envelope_endpoint_attainment_for_rational_row_cdfs(self):
        # Explicit populations with all multiplicities at endpoints 1 or K.
        for cap in (1, 2, 3, 4, 7):
            for denominator in range(1, 16):
                for numerator in range(denominator + 1):
                    p = Fraction(numerator, denominator)
                    result = clone_cdf_envelope(p, cap)
                    low_left = (cap,) * numerator
                    low_right = (1,) * (cap * (denominator - numerator))
                    high_left = (1,) * (cap * numerator)
                    high_right = (cap,) * (denominator - numerator)
                    for left, right, target in (
                        (low_left, low_right, result.lower),
                        (high_left, high_right, result.upper),
                    ):
                        self.assertEqual(Fraction(sum(left), sum(left) + sum(right)), p)
                        self.assertEqual(Fraction(len(left), len(left) + len(right)), target)

    def test_equal_weights_leave_the_cdf_unchanged(self):
        for count in range(1, 21):
            for left_count in range(count + 1):
                for weight in (1, 2, 3):
                    self.assertEqual(Fraction(weight * left_count, weight * count),
                                     Fraction(left_count, count))

    def test_threshold_infeasibility_despite_feasible_global_total(self):
        # J=2,N=6,K=3 globally forces both multiplicities to 3, so k=1
        # cannot be a whole-clone threshold count.
        with self.assertRaises(ValueError):
            finite_clone_cdf_bounds(6, 1, 3, 2)

    def test_hypothetical_nontrivial_finite_example(self):
        envelope = clone_cdf_envelope(Fraction(3, 7), 3)
        finite = finite_clone_cdf_bounds(7, 3, 3)
        known = finite_clone_cdf_bounds(7, 3, 3, 4)
        self.assertEqual((envelope.lower, envelope.upper), (Fraction(1, 5), Fraction(9, 13)))
        self.assertEqual((finite.lower, finite.upper), (Fraction(1, 5), Fraction(3, 5)))
        self.assertEqual((known.lower, known.upper), (Fraction(1, 4), Fraction(1, 2)))

    def test_large_exact_integers_do_not_round(self):
        n = 10**100 + 7
        k = n // 2
        result = finite_clone_cdf_bounds(n, k, 3)
        self.assertIsInstance(result.lower, Fraction)
        self.assertIsInstance(result.upper, Fraction)
        self.assertLessEqual(result.lower, Fraction(k, n))
        self.assertGreaterEqual(result.upper, Fraction(k, n))

    def test_invalid_inputs_are_rejected(self):
        for fn in (finite_clone_cdf_bounds, endpoint_realizations):
            for args in ((0, 0), (-1, 0), (2, -1), (2, 3), (2, 1, 0),
                         (2, 1, -1), (2, 1, 3, 0), (2, 1, 3, 3), (9, 3, 3, 2)):
                with self.subTest(fn=fn.__name__, args=args):
                    with self.assertRaises(ValueError):
                        fn(*args)
            for args in ((True, 0), (2, False), (2, 1, True), (2, 1, 3, True),
                         (2.0, 1), (2, 1.0), (2, 1, 3.0), (2, 1, 3, 1.0),
                         ("2", 1), (2, Fraction(1)), (2, 1, 3, Fraction(1))):
                with self.assertRaises(TypeError):
                    fn(*args)
        for p in (True, False, 0.5, float("nan"), float("inf"), "1/2", None):
            with self.assertRaises(TypeError):
                clone_cdf_envelope(p)
        for p in (-1, 2, Fraction(-1, 3), Fraction(4, 3)):
            with self.assertRaises(ValueError):
                clone_cdf_envelope(p)
        for cap in (True, 3.0, "3", Fraction(3)):
            with self.assertRaises(TypeError):
                clone_cdf_envelope(Fraction(1, 2), cap)
        for cap in (0, -3):
            with self.assertRaises(ValueError):
                clone_cdf_envelope(Fraction(1, 2), cap)


if __name__ == "__main__":
    unittest.main()
