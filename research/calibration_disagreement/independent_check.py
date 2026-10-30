#!/usr/bin/env python3
"""Independent Decimal check of a hypothetical six-cell CP calibration box.

Standard library only; no repository imports or writes. Numbers are synthetic.
The result concerns product-law oracle distributions, not statistical power,
actual biology, or the performance of the already frozen point forecasts.
"""

from decimal import Decimal, localcontext
from math import comb
import json


def binomial_sum(n, p, first, last):
    one = Decimal(1)
    return sum((Decimal(comb(n, j)) * p ** j * (one - p) ** (n-j)
                for j in range(first, last+1)), Decimal(0))


def cp_bound(k, n, tail, lower):
    if lower and k == 0:
        return Decimal(0)
    if not lower and k == n:
        return Decimal(1)
    lo, hi = Decimal(0), Decimal(1)
    for _ in range(240):
        mid = (lo + hi) / 2
        if lower:
            # P_p(K >= k) increases with p.
            probability = binomial_sum(n, mid, k, n)
            if probability < tail:
                lo = mid
            else:
                hi = mid
        else:
            # P_p(K <= k) decreases with p.
            probability = binomial_sum(n, mid, 0, k)
            if probability > tail:
                lo = mid
            else:
                hi = mid
    answer = (lo + hi) / 2
    residual = abs(binomial_sum(n, answer, k, n) - tail) if lower else abs(
        binomial_sum(n, answer, 0, k) - tail)
    assert residual < Decimal('1e-69')
    return answer


def normalize(values):
    total = sum(values)
    return tuple(x / total for x in values)


def kl(p, q):
    return sum((a * (a / b).ln() for a, b in zip(p, q)), Decimal(0))


def js(p, q):
    m = tuple((a + b) / 2 for a, b in zip(p, q))
    return (kl(p, m) + kl(q, m)) / 2


def main():
    with localcontext() as ctx:
        ctx.prec = 80
        one = Decimal(1)
        alpha = one / 20
        tail = alpha / 12
        intervals = {k: (cp_bound(k, 100, tail, True),
                         cp_bound(k, 100, tail, False)) for k in (10, 20, 80)}
        low10, high10 = intervals[10]
        low20, high20 = intervals[20]
        low80, high80 = intervals[80]
        # Six distinct nuisance probabilities. Equal observed k does not pool them.
        corner = ((low20, high10, low20), (high20, low80, high20))
        p1, p2 = tuple(normalize(x) for x in corner)
        a, b = p1[1], p2[1]
        assert a < b
        sharp_min = js(p1, p2)
        binary_min = js((a, one-a), (b, one-b))
        assert abs(sharp_min-binary_min) < Decimal('1e-76')
        point1 = normalize(tuple(Decimal(x) for x in (41,21,41)))
        point2 = normalize(tuple(Decimal(x) for x in (41,161,41)))
        point_js = js(point1, point2)
        mean = tuple((a+b)/2 for a,b in zip(p1,p2))
        fixed_forecast_misspecification = (kl(p1, point1) + kl(p2, point2)) / 2
        fixed_forecast_gain_over_best_common = sharp_min - fixed_forecast_misspecification
        # This decomposition applies at these possible oracle truths only.
        lhs = sum(sum(t * (r / m).ln() for t,r,m in zip(p,f,mean))
                  for p,f in ((p1,point1),(p2,point2))) / 2
        assert abs(lhs-fixed_forecast_gain_over_best_common) < Decimal('1e-76')
        output = {
            'scope': 'Synthetic calibration sensitivity; no data or power result',
            'alpha': alpha,
            'tail_probability': tail,
            'n_per_cell': 100,
            'count_law': 'Each of six marginal counts is Binomial(100, p_ci)',
            'CP_intervals': intervals,
            'sharp_minimizing_latent_controls': corner,
            'sharp_minimizing_product_law_vectors': (p1,p2),
            'context1_A_max': a,
            'context2_A_min': b,
            'minimum_JS_nats': sharp_min,
            'point_JS_nats': point_js,
            'minimum_to_point_ratio': sharp_min/point_js,
            'x_range_each_context': ((low20/high20).ln()/2,
                                     (high20/low20).ln()/2),
            'z_range_context1': ((low10/high20).ln(), (high10/low20).ln()),
            'z_range_context2': ((low80/high20).ln(), (high80/low20).ln()),
            'minimum_z2_minus_z1': (low80/high20).ln() - (high10/low20).ln(),
            'least_favorable_mean': mean,
            'fixed_point_forecast_misspecification_at_corner': fixed_forecast_misspecification,
            'fixed_point_forecast_gain_over_best_common_at_corner': fixed_forecast_gain_over_best_common,
            'verification': 'PASS: 80-digit arithmetic, tail-root residuals < 1e-69; identities < 1e-76',
        }
        print(json.dumps(output, default=str, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
