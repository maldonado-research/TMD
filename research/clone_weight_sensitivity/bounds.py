"""Exact, conditional row-to-clone CDF bounds for bounded multiplicities.

Original R41 bookkeeping implementation; no biological data or author code.
Each eligible clone has one common value repeated between 1 and K times.
Bounds use a single threshold's row count, optionally the total clone count.
They do not recover identities, multiplicities, fitness, or sampling error.

All probabilities returned by this module are fractions.Fraction objects.
Count arguments accept Python integers except bool; probabilities accept only
int or Fraction, except bool. Floating-point inputs are deliberately rejected.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class CDFBounds:
    """Inclusive lower and upper bounds for the clone CDF at one threshold."""

    lower: Fraction
    upper: Fraction


@dataclass(frozen=True)
class ThresholdRealization:
    """Hypothetical endpoint witness; entries are distinct clone multiplicities.

    Assign all left clones a common value below or at the threshold and all
    right clones a value above it. Entries do not denote observed clone IDs.
    """

    left: tuple[int, ...]
    right: tuple[int, ...]

    @property
    def row_count(self) -> int:
        return sum(self.left) + sum(self.right)

    @property
    def clone_count(self) -> int:
        return len(self.left) + len(self.right)

    @property
    def row_cdf(self) -> Fraction:
        return Fraction(sum(self.left), self.row_count)

    @property
    def clone_cdf(self) -> Fraction:
        return Fraction(len(self.left), self.clone_count)


def _integer(name: str, value: int, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer, excluding bool")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _probability(value: Fraction | int) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError("row_cdf must be an int or Fraction, excluding bool")
    value = Fraction(value)
    if not 0 <= value <= 1:
        raise ValueError("row_cdf must be between zero and one")
    return value


def clone_cdf_envelope(
    row_cdf: Fraction | int, max_multiplicity: int = 3
) -> CDFBounds:
    """Sharp pointwise envelope when row totals and clone count are unspecified.

    For p = row_cdf and K = max_multiplicity, return
    [p / (K - (K-1)*p), K*p / (1 + (K-1)*p)].
    Rational endpoints are attainable over some finite populations. If the
    actual row total is fixed, finite_clone_cdf_bounds can be tighter.
    """
    p = _probability(row_cdf)
    cap = _integer("max_multiplicity", max_multiplicity, 1)
    return CDFBounds(
        p / (cap - (cap - 1) * p),
        cap * p / (1 + (cap - 1) * p),
    )


def _count_limits(
    row_count: int,
    rows_at_or_below: int,
    max_multiplicity: int,
    unique_clone_count: int | None,
) -> tuple[int, int, int, int]:
    total = _integer("row_count", row_count, 1)
    left_rows = _integer("rows_at_or_below", rows_at_or_below, 0)
    cap = _integer("max_multiplicity", max_multiplicity, 1)
    if left_rows > total:
        raise ValueError("rows_at_or_below must not exceed row_count")
    right_rows = total - left_rows
    left_min = (left_rows + cap - 1) // cap
    right_min = (right_rows + cap - 1) // cap
    if unique_clone_count is None:
        # Lower endpoint minimizes left clones and maximizes right clones.
        # Upper endpoint maximizes left clones and minimizes right clones.
        return left_min, right_rows, left_rows, right_min
    clones = _integer("unique_clone_count", unique_clone_count, 1)
    if not clones <= total <= cap * clones:
        raise ValueError("row_count must lie between J and K*J")
    low = max(left_min, clones - right_rows)
    high = min(left_rows, clones - right_min)
    if low > high:
        raise ValueError("threshold counts are incompatible with this clone count")
    return low, clones - low, high, clones - high


def finite_clone_cdf_bounds(
    row_count: int,
    rows_at_or_below: int,
    max_multiplicity: int = 3,
    unique_clone_count: int | None = None,
) -> CDFBounds:
    """Exact endpoint bounds given N rows, k threshold rows and optionally J.

    Empty frames and impossible counts raise ValueError. Sharpness refers to
    information N, k, K and optional J only; observed value ties or known
    identities can constrain the problem further. Intermediate fractions need
    not be attainable, and endpoints at multiple thresholds need not share a
    single realization. The function uses a constant number of integer
    operations and does not iterate over N or J; bit complexity still depends
    on the sizes of the integer inputs.
    """
    low_left, low_right, high_left, high_right = _count_limits(
        row_count, rows_at_or_below, max_multiplicity, unique_clone_count
    )
    return CDFBounds(
        Fraction(low_left, low_left + low_right),
        Fraction(high_left, high_left + high_right),
    )


def _partition_rows(rows: int, clones: int, cap: int) -> tuple[int, ...]:
    """Construct any permitted partition; callers already checked feasibility."""
    excess = rows - clones
    result = []
    for _ in range(clones):
        add = min(excess, cap - 1)
        result.append(1 + add)
        excess -= add
    if excess != 0:
        raise AssertionError("internal partition feasibility error")
    return tuple(result)


def endpoint_realizations(
    row_count: int,
    rows_at_or_below: int,
    max_multiplicity: int = 3,
    unique_clone_count: int | None = None,
) -> tuple[ThresholdRealization, ThresholdRealization]:
    """Construct HYPOTHETICAL lower/upper endpoint witnesses, in that order.

    This allocates one tuple entry per hypothetical clone: O(N) worst-case
    time and memory. Use finite_clone_cdf_bounds alone for very large totals.
    No witness is an estimate of an actual clone's multiplicity or identity.
    """
    low_left, low_right, high_left, high_right = _count_limits(
        row_count, rows_at_or_below, max_multiplicity, unique_clone_count
    )
    right_rows = row_count - rows_at_or_below
    return tuple(
        ThresholdRealization(
            _partition_rows(rows_at_or_below, left, max_multiplicity),
            _partition_rows(right_rows, right, max_multiplicity),
        )
        for left, right in ((low_left, low_right), (high_left, high_right))
    )
