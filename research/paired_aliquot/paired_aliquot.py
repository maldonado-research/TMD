"""Exact finite synthetic paired-sampling laws; no biological fitting.

The compound-Poisson probability ratios below concern explicitly stated
finite clone laws. Absolute probabilities are left as exp(-exact intensity).
No floating certificate, statistical interval or mechanistic inference is made.
"""
from fractions import Fraction
from math import comb, factorial

MAX_CLONE = 8
MAX_TOTAL_COUNT = 8
INPUT_BITS = 32


def exact(x, name):
    if type(x) not in (int, Fraction):
        raise TypeError(name + " must be int or Fraction, excluding bool")
    x = Fraction(x)
    if max(abs(x.numerator).bit_length(), x.denominator.bit_length()) > INPUT_BITS:
        raise ValueError(name + " exceeds the input rational cap")
    return x


def probability(x, name):
    x = exact(x, name)
    if not 0 <= x <= 1:
        raise ValueError(name + " outside [0,1]")
    return x


def clone_law(law):
    if type(law) is not dict or not law or len(law) > MAX_CLONE + 1:
        raise ValueError("clone law must be a nonempty finite dictionary")
    if any(type(k) is not int or not 0 <= k <= MAX_CLONE for k in law):
        raise ValueError("clone support must be integer 0 through 8")
    weights = {k: exact(w, "clone weight") for k, w in law.items()}
    if any(w < 0 for w in weights.values()) or sum(weights.values()) != 1:
        raise ValueError("clone weights must be nonnegative and normalized")
    return weights


def count_cap(cap):
    if type(cap) is not int or not 0 <= cap <= MAX_TOTAL_COUNT:
        raise ValueError("total count cap must be integer 0 through 8")
    return cap


def pgf(law, z):
    law, z = clone_law(law), probability(z, "z")
    return sum((w * z ** k for k, w in law.items()), Fraction())


def _thin(law, p):
    return {j: sum((w * comb(k, j) * p ** j * (1-p) ** (k-j)
                    for k, w in law.items() if j <= k), Fraction())
            for j in range(max(law) + 1)}


def joint_clone_law(law, p1, p2, frame="disjoint"):
    """One clone's marked counts, before compound-Poisson aggregation."""
    law = clone_law(law)
    p1, p2 = probability(p1, "p1"), probability(p2, "p2")
    if frame not in ("disjoint", "overlapping"):
        raise ValueError("frame must be disjoint or overlapping")
    if frame == "disjoint" and p1 + p2 > 1:
        raise ValueError("disjoint capture probabilities sum above 1")
    out = {}
    for k, w in law.items():
        for a in range(k+1):
            for b in range(k+1):
                if frame == "disjoint":
                    if a+b > k:
                        continue
                    term = (w * comb(k,a) * comb(k-a,b) * p1 ** a * p2 ** b
                            * (1-p1-p2) ** (k-a-b))
                else:
                    term = (w * comb(k,a) * p1 ** a * (1-p1) ** (k-a)
                            * comb(k,b) * p2 ** b * (1-p2) ** (k-b))
                out[a,b] = out.get((a,b), Fraction()) + term
    assert sum(out.values()) == 1
    return out


def _cp_1d(m, marked, cap):
    q = [Fraction(1)]
    for n in range(1, cap+1):
        q.append(m/n * sum((j*marked.get(j,0)*q[n-j]
                             for j in range(1,n+1)), Fraction()))
    return q


def _cp_2d(m, marked, cap):
    """Euler-derivative recurrence for exact P(a,b)/P(0,0)."""
    q = {(0,0): Fraction(1)}
    for total in range(1, cap+1):
        for a in range(total+1):
            b = total-a
            q[a,b] = m/total * sum(((u+v)*w*q.get((a-u,b-v),0)
                                   for (u,v),w in marked.items()
                                   if 0 < u+v <= total and u <= a and v <= b), Fraction())
    return q


def _cp_2d_exp_series(m, marked, cap):
    """Independent finite exponential-series/convolution calculation."""
    positive = {(a,b): w for (a,b),w in marked.items() if a+b and w}
    total = {(a,n-a): Fraction() for n in range(cap+1) for a in range(n+1)}
    power = {(0,0): Fraction(1)}
    for events in range(cap+1):
        multiplier = m ** events / factorial(events)
        for key,w in power.items():
            total[key] += multiplier*w
        nxt = {}
        for (a,b),w in power.items():
            for (u,v),h in positive.items():
                if a+b+u+v <= cap:
                    key = a+u,b+v
                    nxt[key] = nxt.get(key,Fraction()) + w*h
        power = nxt
    return total


def paired_model(law, m, p1, p2, frame="disjoint", cap=8):
    law = clone_law(law)
    m = exact(m,"m")
    if not 0 <= m <= 20:
        raise ValueError("m outside [0,20]")
    p1, p2 = probability(p1,"p1"), probability(p2,"p2")
    cap = count_cap(cap)
    if frame not in ("disjoint","overlapping","independent_cultures"):
        raise ValueError("unknown sampling frame")
    ek = sum((k*w for k,w in law.items()), Fraction())
    ekk = sum((k*(k-1)*w for k,w in law.items()), Fraction())
    a1 = m*(1-pgf(law,1-p1))
    a2 = m*(1-pgf(law,1-p2))
    if frame == "independent_cultures":
        first,second = _cp_1d(m,_thin(law,p1),cap),_cp_1d(m,_thin(law,p2),cap)
        q = {(a,n-a):first[a]*second[n-a] for n in range(cap+1) for a in range(n+1)}
        a00,covariance = a1+a2,Fraction()
    else:
        marked = joint_clone_law(law,p1,p2,frame)
        q = _cp_2d(m,marked,cap)
        a00 = m*(1-marked.get((0,0),0))
        covariance = m*p1*p2*(ekk if frame == "disjoint" else ekk+ek)
    return {"frame":frame,"negative_log_P00":a00,"negative_log_P0_marginals":[a1,a2],
            "means":[m*p1*ek,m*p2*ek],
            "variances":[m*(p1*ek+p1*p1*ekk),m*(p2*ek+p2*p2*ekk)],
            "covariance":covariance,"relative_coefficients":q}


def _json_model(model):
    out = {key:([str(x) for x in value] if isinstance(value,list) else str(value))
           for key,value in model.items() if key != "relative_coefficients"}
    out["relative_coefficients"] = {str(a)+","+str(b):str(w)
                                    for (a,b),w in model["relative_coefficients"].items()}
    return out


def benchmarks():
    if not __debug__:
        raise RuntimeError("Benchmark verification requires Python assertions enabled.")
    laws = [{0:Fraction(1)}, {1:Fraction(1)}, {2:Fraction(1)},
            {1:Fraction(3,4),3:Fraction(1,4)}, {0:Fraction(1,3),8:Fraction(2,3)}]
    pairs = [(Fraction(0),Fraction(0)),(Fraction(0),Fraction(1)),
             (Fraction(1),Fraction(0)),(Fraction(1,4),Fraction(1,4)),
             (Fraction(1,10),Fraction(2,5)),(Fraction(1,3),Fraction(2,3))]
    counts = {"joint_PMF_normalization":0,"exact_clone_PGF_identities":0,
              "recurrence_vs_exp_series_coefficients":0,"union_thinning_coefficients":0,
              "conditional_binomial_split_coefficients":0,"invalid_input_guards":0}
    for law in laws:
        for p1,p2 in pairs:
            for frame in ("disjoint","overlapping"):
                marked = joint_clone_law(law,p1,p2,frame)
                assert sum(marked.values()) == 1
                counts["joint_PMF_normalization"] += 1
                for z1,z2 in pairs:
                    lhs = sum((w*z1**a*z2**b for (a,b),w in marked.items()),Fraction())
                    z = 1-p1-p2+p1*z1+p2*z2 if frame == "disjoint" else (1-p1+p1*z1)*(1-p2+p2*z2)
                    assert lhs == pgf(law,z)
                    counts["exact_clone_PGF_identities"] += 1
                for m in (Fraction(0),Fraction(1,3),Fraction(2)):
                    q = paired_model(law,m,p1,p2,frame,6)["relative_coefficients"]
                    assert q == _cp_2d_exp_series(m,marked,6)
                    counts["recurrence_vs_exp_series_coefficients"] += len(q)
                    if frame == "disjoint":
                        P = p1+p2
                        univariate = _cp_1d(m,_thin(law,P),6)
                        for n in range(7):
                            assert sum(q[a,n-a] for a in range(n+1)) == univariate[n]
                            counts["union_thinning_coefficients"] += 1
                            if P:
                                for a in range(n+1):
                                    assert q[a,n-a] == univariate[n]*comb(n,a)*(p1/P)**a*(p2/P)**(n-a)
                                    counts["conditional_binomial_split_coefficients"] += 1
    invalid = [lambda:paired_model({},1,Fraction(1,4),Fraction(1,4)),
               lambda:paired_model({1:Fraction(1,2)},1,0,0),
               lambda:paired_model({1:2,2:-1},1,0,0),
               lambda:paired_model({True:1},1,0,0),
               lambda:paired_model({9:1},1,0,0),
               lambda:paired_model({1:1.0},1,0,0),
               lambda:paired_model({1:True},1,0,0),
               lambda:paired_model({1:1},True,0,0),
               lambda:paired_model({1:1},-1,0,0),
               lambda:paired_model({1:1},21,0,0),
               lambda:paired_model({1:1},1,0.5,0),
               lambda:paired_model({1:1},1,-1,0),
               lambda:paired_model({1:1},1,0,2),
               lambda:paired_model({1:1},1,1,1),
               lambda:paired_model({1:1},1,0,0,"unknown"),
               lambda:paired_model({1:1},1,0,0,cap=9),
               lambda:paired_model({1:1},1,0,0,cap=True),
               lambda:paired_model({1:1},1,Fraction(1,2**40),0)]
    for operation in invalid:
        try:
            operation()
        except (TypeError,ValueError):
            counts["invalid_input_guards"] += 1
        else:
            raise AssertionError("invalid benchmark input admitted")
    contrast = {frame:_json_model(paired_model({2:1},1,Fraction(1,4),Fraction(1,4),frame,4))
                for frame in ("disjoint","overlapping","independent_cultures")}
    assert [contrast[f]["negative_log_P00"] for f in contrast] == ["3/4","175/256","7/8"]
    assert [contrast[f]["covariance"] for f in contrast] == ["1/8","1/4","0"]
    a = paired_model({2:1},1,Fraction(1,4),Fraction(1,4),cap=4)
    b = paired_model({0:Fraction(1,2),2:Fraction(1,2)},2,Fraction(1,4),Fraction(1,4),cap=4)
    assert a == b
    positive_intensities_a = {2:Fraction(1)}
    positive_intensities_b = {k:2*w for k,w in {0:Fraction(1,2),2:Fraction(1,2)}.items() if k}
    assert positive_intensities_a == positive_intensities_b
    c = paired_model({1:Fraction(3,4),3:Fraction(1,4)},Fraction(4,3),Fraction(1,4),Fraction(1,4),cap=4)
    for field in ("means","variances","covariance"):
        assert a[field] == c[field]
    assert a["negative_log_P00"] != c["negative_log_P00"]
    assert c["negative_log_P00"] == Fraction(19,24)
    negative_control = {}
    for frame in ("disjoint","overlapping"):
        q = paired_model({1:1},1,Fraction(1,4),Fraction(1,4),frame,2)["relative_coefficients"]
        diagonal = sum(q[i,2-i] for i in range(3))
        ratio = q[1,1]/diagonal
        assert ratio == (Fraction(1,2) if frame == "disjoint" else Fraction(25,34))
        negative_control[frame] = {"q20":str(q[2,0]),"q11":str(q[1,1]),
                                   "q02":str(q[0,2]),"qS2":str(diagonal),
                                   "P_X1_equals_1_given_S2":str(ratio)}
    lambdas = {0:Fraction(1,3),3:Fraction(2,3)}
    mean_lambda = sum(v*w for v,w in lambdas.items())
    variance_lambda = sum(v*v*w for v,w in lambdas.items()) - mean_lambda**2
    assert mean_lambda == 2 and variance_lambda == 2
    assert mean_lambda + variance_lambda == 4
    assert Fraction(1,4)**2*variance_lambda == a["covariance"]
    return {"schema_version":1,"status":"passed","scope":"exact finite synthetic observation laws",
            "checks":counts,"same_marginals_different_paired_frames":contrast,
            "same_moments_different_finite_clone_histories":[_json_model(a),_json_model(c)],
            "conditional_split_negative_control":negative_control,
            "zero_clone_full_law_ambiguity":{"first_m":"1","first_law":{"2":"1"},
                "second_m":"2","second_law":{"0":"1/2","2":"1/2"},
                "all_PGF_terms_identical":True,"reason":"equal positive jump intensities; extra zero marks are unobserved"},
            "fixed_terminal_N2_disjoint_covariance":"-1/8",
            "mixed_Poisson_counterexample":{"Lambda_values":["0","3"],"weights":["1/3","2/3"],
                "E_R":"2","Var_R":"4","paired_covariance_at_p1_p2_quarter":"1/8",
                "same_as_fixed_intensity_K2_first_two_moments":True,"molecular_clone_mechanism_identified":False},
            "biological_data_fitted":False,"new_rate_or_confidence_interval":False,
            "new_theorem_or_priority_claim":False,"actual_study_fields_resolved":0}
