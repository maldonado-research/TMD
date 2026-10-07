"""Classical clone/thinning benchmarks, with no biological likelihood fitting.

Exact rational calculations below concern finite synthetic clone models.
Infinite equal-growth LD zero probabilities use 80-digit Decimal arithmetic;
they are numerical evaluations of stated analytic identities, not outward
certified confidence bounds or a claim that this model describes the source.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from math import comb, factorial

PRECISION = 80


def rational(x, name):
    if type(x) not in (int, Fraction):
        raise TypeError(name + " must be an int or Fraction")
    x = Fraction(x)
    if x.denominator.bit_length() > 128 or abs(x.numerator).bit_length() > 128:
        raise ValueError(name + " exceeds the benchmark rational-size cap")
    return x


def probability(p):
    p = rational(p, "p")
    if not 0 <= p <= 1:
        raise ValueError("p outside[0,1]")
    return p


def birth_intensity(m):
    m = rational(m, "m")
    if not 0 <= m <= 100:
        raise ValueError("synthetic m outside[0,100]")
    return m


def decimal(x):
    x = Fraction(x)
    return Decimal(x.numerator) / Decimal(x.denominator)


def ld_zero_factor(p):
    """E[1-(1-p)^K] for P(K=k)=1/[k(k+1)]."""
    p = probability(p)
    with localcontext() as ctx:
        ctx.prec = PRECISION
        if p == 0:
            return Decimal(0)
        if p == 1:
            return Decimal(1)
        d = decimal(p)
        return +(-d * d.ln() / (1 - d))


def ld_clone_pgf(t):
    t = probability(t)
    with localcontext() as ctx:
        ctx.prec = PRECISION
        if t == 0:
            return Decimal(0)
        if t == 1:
            return Decimal(1)
        d = decimal(t)
        return +(1 + (1 - d) / d * (1 - d).ln())


def ld_pgf(m, p, z):
    m, p, z = birth_intensity(m), probability(p), probability(z)
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return +(decimal(m) * (ld_clone_pgf(1 - p + p * z) - 1)).exp()


def ld_zero_probability(m, p):
    m, p = birth_intensity(m), probability(p)
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return +(-decimal(m) * ld_zero_factor(p)).exp()


def clone_zero_bounds(p, cutoff):
    """Exact rational lower/upper bounds for g(1-p), not G's numerical exp."""
    p = probability(p)
    if type(cutoff) is not int or not 1 <= cutoff <= 512:
        raise ValueError("cutoff outside[1,512]")
    t = 1 - p
    lower = sum((t ** k / (k * (k + 1)) for k in range(1, cutoff + 1)), Fraction())
    upper = lower + t ** (cutoff + 1) / (cutoff + 1)
    return lower, upper


def capped_clone_law(cutoff):
    """A distinct finite synthetic model: K=min(K_infinite,cutoff)."""
    if type(cutoff) is not int or not 1 <= cutoff <= 16:
        raise ValueError("finite synthetic cutoff outside[1,16]")
    return {k: Fraction(1, k * (k + 1)) if k < cutoff else Fraction(1, cutoff)
            for k in range(1, cutoff + 1)}


def validate_law(law, minimum):
    """Validate a bounded exact PMF; no float/bool or malformed laws admitted."""
    if type(law) is not dict or not law or len(law) > 17 - minimum:
        raise ValueError("finite law must be a nonempty bounded dictionary")
    if any(type(k) is not int or not minimum <= k <= 16 for k in law):
        raise ValueError("finite law has invalid integer support")
    checked = {k: rational(w, "law weight") for k, w in law.items()}
    if any(w < 0 for w in checked.values()) or sum(checked.values()) != 1:
        raise ValueError("finite law must be normalized and nonnegative")
    return checked


def thin_clone_law(law, p):
    p = probability(p)
    law = validate_law(law, 1)
    out = {j: sum((Fraction(w) * comb(k, j) * p ** j * (1 - p) ** (k - j)
                   for k, w in law.items() if k >= j), Fraction())
           for j in range(max(law) + 1)}
    assert sum(out.values()) == 1
    return out


def evaluate(law, z):
    z = probability(z)
    return sum((w * z ** k for k, w in law.items()), Fraction())


def cp_relative_coefficients_recurrence(m, observed_law, count_cap):
    """Return P_n/P_0 exactly; P0=exp[-m(1-a0)]."""
    m = birth_intensity(m)
    observed_law = validate_law(observed_law, 0)
    if type(count_cap) is not int or not 0 <= count_cap <= 32:
        raise ValueError("count_cap outside[0,32]")
    q = [Fraction(1)]
    for n in range(1, count_cap + 1):
        q.append(m / n * sum((j * observed_law.get(j, 0) * q[n - j]
                              for j in range(1, n + 1)), Fraction()))
    return q


def cp_relative_coefficients_direct(m, observed_law, count_cap):
    """Separate exp-series/polynomial-convolution oracle for the same ratios."""
    m = birth_intensity(m)
    observed_law = validate_law(observed_law, 0)
    if type(count_cap) is not int or not 0 <= count_cap <= 32:
        raise ValueError("count_cap outside[0,32]")
    positive = {j: w for j, w in observed_law.items() if j > 0}
    total, power = [Fraction(0)] * (count_cap + 1), [Fraction(1)] + [Fraction(0)] * count_cap
    for events in range(count_cap + 1):
        weight = m ** events / factorial(events)
        for n in range(count_cap + 1):
            total[n] += weight * power[n]
        nxt = [Fraction(0)] * (count_cap + 1)
        for n in range(count_cap + 1):
            for j, w in positive.items():
                if n + j <= count_cap:
                    nxt[n + j] += power[n] * w
        power = nxt
    return total


def benchmarks():
    with localcontext() as ctx:
        ctx.prec = PRECISION
        tolerance = Decimal("1e-60")
        factors = []
        bound_checks = 0
        ps = [Fraction(0), Fraction(3, 40000), Fraction(1, 6000), Fraction(3, 4000),
              Fraction(3, 40), Fraction(1, 2), Fraction(1)]
        for p in ps:
            factor = ld_zero_factor(p)
            assert abs(factor - (1 - ld_clone_pgf(1 - p))) < tolerance
            row = {"p": str(p), "A_p_decimal": str(factor),
                   "p_origin": "source_nominal_geometry" if p in ps[1:5] else "synthetic_boundary_or_example"}
            bounds = []
            for cutoff in (8, 32, 128):
                lower, upper = clone_zero_bounds(p, cutoff)
                target = 1 - factor
                assert decimal(lower) - tolerance <= target <= decimal(upper) + tolerance
                bound_checks += 1
                bounds.append({"cutoff": cutoff, "g_lower_decimal_rounded": str(decimal(lower)),
                               "g_upper_decimal_rounded": str(decimal(upper)),
                               "rational_bound_width": str(upper - lower)})
            row["finite_clone_sum_checks"] = bounds
            factors.append(row)
        thinning_checks, coefficient_checks = 0, 0
        for cutoff in (1, 3, 8):
            law = capped_clone_law(cutoff)
            assert sum(law.values()) == 1
            for p in (Fraction(0), Fraction(1, 10), Fraction(1, 2), Fraction(1)):
                obs = thin_clone_law(law, p)
                for z in (Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(1)):
                    assert evaluate(obs, z) == evaluate(law, 1 - p + p * z)
                    thinning_checks += 1
                for m in (Fraction(1, 10), Fraction(1), Fraction(2)):
                    q = cp_relative_coefficients_recurrence(m, obs, 8)
                    direct = cp_relative_coefficients_direct(m, obs, 8)
                    assert q == direct
                    coefficient_checks += len(q)
        a = Decimal("0.7")
        zero = (-a).exp()
        confounded = []
        for p in (Fraction(1, 10), Fraction(1, 2), Fraction(1)):
            phi = ld_zero_factor(p)
            m_decimal = a / phi
            ghalf = (m_decimal * (ld_clone_pgf(1 - p + p / 2) - 1)).exp()
            confounded.append({"p": str(p), "synthetic_m_decimal": str(m_decimal),
                               "P0_decimal": str((-m_decimal * phi).exp()),
                               "Gobs_at_z_half_decimal": str(ghalf)})
            assert abs((-m_decimal * phi).exp() - zero) < tolerance
        assert len({x["Gobs_at_z_half_decimal"] for x in confounded}) == 3
        guards = 0
        malformed = [{}, {1: Fraction(1, 2)}, {1: 2, 2: -1}, {1: 0.5, 2: 0.5},
                     {1: True}, {True: 1}, {Fraction(3, 2): 1}, {17: 1},
                     {1: Fraction(1, 2 ** 130), 2: 1 - Fraction(1, 2 ** 130)}]
        for law in malformed:
            for operation in (lambda: thin_clone_law(law, Fraction(1, 2)),
                              lambda: cp_relative_coefficients_recurrence(1, law, 8),
                              lambda: cp_relative_coefficients_direct(1, law, 8)):
                try:
                    operation()
                except (ValueError, TypeError):
                    guards += 1
                else:
                    raise AssertionError("malformed law was admitted")
        assert guards == 27
        # Different synthetic event times/clone sizes, identical zero intensity.
        histories = []
        p = Fraction(1, 10)
        for clone_size in (1, 2, 8):
            phi = 1 - (1 - p) ** clone_size
            m_decimal = a / decimal(phi)
            histories.append({"clone_size": clone_size, "capture_p": str(p),
                              "event_visibility_fraction": str(phi),
                              "synthetic_m_decimal": str(m_decimal),
                              "P0_decimal": str((-m_decimal * decimal(phi)).exp())})
        return {"schema_version": 1, "status": "synthetic_model_benchmarks_passed",
                "model": "classical ideal equal-growth asymptotic LD clone law with independent descendant thinning",
                "decimal_precision": PRECISION, "decimal_comparison_tolerance": str(tolerance),
                "numerical_exp_log_bounds_outward_certified": False,
                "exact_finite_clone_thinning_identities": thinning_checks,
                "exact_compound_Poisson_relative_coefficient_identities": coefficient_checks,
                "infinite_clone_rational_tail_checks": bound_checks,
                "malformed_exact_PMF_guard_checks": guards,
                "zero_factor_rows": factors,
                "equal_zero_probability_different_full_PGF_examples": confounded,
                "equal_zero_probability_different_clone_history_examples": histories,
                "biological_likelihood_fits": 0, "biological_rate_estimates": 0,
                "new_theorem_or_priority_claim": False, "matched_WAM_panels_admitted": 0}
