"""Sharp finite-sample bounds for paired categorical forecasts on set-valued labels."""

from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from math import log, log1p, prod


@dataclass(frozen=True)
class OutcomeScores:
    unique_top_hit: int
    unique_top_gain: int
    randomized_top_gain: Fraction
    brier_gain: Fraction
    likelihood_ratio: Fraction


def probabilities(values):
    if not isinstance(values, Mapping) or not values:
        raise ValueError("Supply a nonempty mapping from class to probability")
    if any(type(x) not in (int, Fraction) or x <= 0 for x in values.values()):
        raise ValueError("Supply positive exact probabilities as integers or Fractions")
    if sum(values.values()) != 1:
        raise ValueError("Probabilities must sum to one")
    return {key: Fraction(x) for key, x in values.items()}


def score_unit(candidates, p, q):
    """Complete the same hidden outcome for both forecasts, once per distinct class."""
    p, q = probabilities(p), probabilities(q)
    if p.keys() != q.keys():
        raise ValueError("Forecast class rosters differ")
    labels = sorted(set(candidates))
    if not labels or not set(labels) <= p.keys():
        raise ValueError("Supply a nonempty subset of the forecast class roster")
    max_p, max_q = max(p.values()), max(q.values())
    p_top = {k for k, v in p.items() if v == max_p}
    q_top = {k for k, v in q.items() if v == max_q}
    norm_change = sum(q[k] ** 2 - p[k] ** 2 for k in p)
    results = {}
    for y in labels:
        p_hit = int(p_top == {y})
        q_hit = int(q_top == {y})
        results[y] = OutcomeScores(
            p_hit,
            p_hit - q_hit,
            Fraction(int(y in p_top), len(p_top)) - Fraction(int(y in q_top), len(q_top)),
            norm_change + 2 * (p[y] - q[y]),
            p[y] / q[y],
        )
    return results


def log_ratio(value):
    if Fraction(1, 2) <= value <= 2:
        return log1p(float(value - 1))
    return log(value.numerator) - log(value.denominator)


def summarize_units(units):
    """Give each supplied unit equal weight. Each unit has one latent winning class."""
    units = list(units)
    if not units or any(not u for u in units):
        raise ValueError("At least one unit and at least one candidate per unit are required")
    n = len(units)
    summary = {"units": n, "class_completions": prod(len(u) for u in units)}
    for field in ("unique_top_hit", "unique_top_gain", "randomized_top_gain", "brier_gain"):
        bounds = {}
        for key, extreme in (("lower", min), ("upper", max)):
            total = sum(extreme(getattr(s, field) for s in u.values()) for u in units)
            bounds[key] = str(Fraction(total, n))
        summary["mean_" + field] = bounds
    log_bounds = {}
    for key, extreme in (("lower", min), ("upper", max)):
        ratio = prod(extreme(s.likelihood_ratio for s in u.values()) for u in units)
        log_bounds[key] = {"product_ratio": str(ratio), "nats_per_unit": log_ratio(ratio) / n}
    summary["mean_log_gain"] = log_bounds
    return summary
