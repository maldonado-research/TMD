# Conditional curvature sensitivity to differential recovery

Original design analysis · 5 November 2026 · AI-assisted internal computational review

This bounded two-context wrapper asks whether the baseline-conditioned curvature test still rejects when differential recovery can differ between contexts. It evaluates a **fixed reference statistic** over an externally justified interval of recovery contrasts, using exact rational arithmetic. It adds a declared interval-noncoverage allocation when those bounds are statistical. All supplied examples are synthetic; no measured recovery bounds, native biological result, new theorem or external peer review is claimed.

Methods 0.6.0 and [transport robustness](../transport_robustness/METHODS.md) already propagate recovery uncertainty through confidence intervals and test a common contrast by intersection. Their residual-bias identity and bound algebra are reused here. The addition is a sensitivity wrapper for the separate [baseline-conditioned exact test](../conditional_curvature/README.md). It leaves that engine, frozen forecasts, score criteria, registry, error allocations and released packages unchanged. The existing [conditional design diagnostics](../conditional_design/README.md) describe the support and information costs of this conditioning; they do not authenticate recovery bounds.

## Observation model and the one-dimensional nuisance

Let the positive biological baseline and selected route probabilities in context c be q and p, with

```text
p_ci proportional to q_ci exp(theta_bio,c 1[i=A] + eta_c s_i),
s=(1,0,-1).
```

Route-specific positive inclusion probabilities are r0 in the baseline arm and r1 in the selected arm. The observed multinomial probabilities are b proportional to q*r0 and v proportional to p*r1. Let

```text
rho_ci = r1_ci/r0_ci,
delta_c = log(rho_cA) - (log(rho_cW)+log(rho_cM))/2,
m_c = exp(2 delta_c) = rho_cA^2/(rho_cW rho_cM).
```

Every positive three-route recovery vector has a constant, W−M tilt and A-curvature decomposition. Thus the observed selected law relative to b has curvature theta_bio,c+delta_c; its remaining recovery tilt joins the context nuisance tilt. Assume the independent product multinomial law across both arms and both contexts, conditional on prespecified arm totals. As in the existing engine, condition on the pooled route vectors T=K+X, each selected total N and W−M difference D, and total selected A.

Under shared biological theta, let `a2_min` be the minimum selected A in the second context on this fiber and set

```text
j = (A_2-a2_min)/2,
h_j = product_ci binom(T_ci, X_ci(j)),
t = exp(2(delta_2-delta_1)) = m_2/m_1.
```

The conditional law is `P_t(j)=h_j t^j / sum_k h_k t^k`. Terms involving the common biological curvature, baseline nuisance, and both observed tilts are constant on the fiber. Context order matters: reversing contexts reflects the weights and replaces `[l,u]` by `[1/u,1/l]`, preserving the result.

The likelihood derivation requires the stated full observation and independence model. A count table or affirmative input declaration does not verify it. Correlated descendants, nonmultinomial route counts, misclassification or a mismatched baseline may invalidate the calculation. This does not identify mutation supply, establishment, selection, drift or causal mechanism.

The [measurement bridge](MEASUREMENT_BRIDGE.md) specifies which controls could justify a bound and gives an exact counterexample in which a shared classifier creates unequal observed curvature. The [SLST-Seq assessment](SLST_MEASUREMENT_NOTE.md) illustrates assignment, mixture and calibration-stage limits from a newly inspected primary source; no source number is used as a native recovery bound.

## Fixed reference ordering and an exact endpoint certificate

Freeze the inclusive probability ordering at zero differential recovery, t=1:

```text
E_observed = {j: h_j <= h_observed},
p_ref(t) = sum_{j in E_observed} h_j t^j / sum_j h_j t^j,
p_sup = sup_{t in [l,u]} p_ref(t).
```

For each fixed t, this is the inclusive lower tail of the single statistic h_J under its true tilted distribution. Its possible event sets are nested, so `Pr_t(p_ref(t)<=alpha | fiber)<=alpha`. Maximizing over an interval containing the true t preserves that bound. **The ordering stays fixed.** This is not a Fisher probability ordering recalculated from h_j*t^j for each t. At `[l,u]=[1,1]` and zero bound noncoverage it agrees exactly with the unchanged baseline-conditioned engine, including ties and observed zeros.

Generic ratios of positive-coefficient polynomials can have interior maxima. In this particular model the endpoint maximum is exact, with a checkable structural reason:

1. The support is every integer j from zero through its maximum. Each h_j is a product of six binomial-coefficient sequences evaluated at affine integer arguments with increments ±1 or ±2. Binomial sequences are log-concave, as are their fixed-step subsequences and products. Therefore h is positive and log-concave, and the strict complement `C={j:h_j>h_observed}` is a contiguous interval `[a,b]`, or is empty.
2. Let Q(t)=P_t(C). After cancellation of terms internal to C, the numerator of Q'(t) is `sum_{i in C,j outside C}(i-j) h_i h_j t^(i+j-1)`. Positive terms have j<a and degrees at most a+b−2. Negative terms have j>b and degrees at least a+b. If both tails exist, division by `t^(a+b-1)` gives a strictly decreasing function, so the derivative can change sign only from positive to negative. One missing tail gives a monotone function; an empty complement gives p_ref=1.
3. Thus Q rises then falls at most once, and p_ref falls then rises at most once. Its maximum on any finite positive interval is **exactly** `max(p_ref(l),p_ref(u))`.

The implementation checks integer support, positive weights, log-concavity, and complement contiguity before using this certificate. The reusable scalar helper requires the positive support and contiguous complement directly; log-concavity is sufficient but is not necessary there. This is a specialization of standard finite exponential-family algebra and polynomial sign arguments, not a new-theorem claim.

Outside that structure, endpoint evaluation can fail. For arbitrary h=(2,1,2) observed at the middle index, `p_ref(t)=t/(2+t+2t²)`. Over [1/2,2], each endpoint gives 1/6 but the interior t=1 gives 1/5. The helper explicitly refuses its disconnected complement `{0,2}`. It never silently substitutes endpoint evaluation for an uncertified optimization.

## External coverage and its error allocation

The input requires a positive finite rational interval and a fixed rational `bound_noncoverage_probability=gamma` in [0,1). Coverage must be justified outside this utility:

```text
Pr(true t is outside the supplied interval) <= gamma,
p_adjusted = min(1, p_sup + gamma).
```

The reported rejection uses `p_adjusted<=alpha`. Set gamma=0 only for a deterministically covering interval. Such bounds give the conditional guarantee above. For a random estimated interval with valid marginal coverage, on its coverage event p_sup is at least the true-parameter reference tail. A union bound gives `Pr(p_adjusted<=alpha)<=alpha`. Statistical independence between the interval and the tested counts is not needed for this marginal argument. A marginal coverage claim alone does **not** establish conditional validity within every fiber; that stronger claim needs conditional coverage given the fiber, for example a valid independent calibration construction. Gamma itself must be fixed rather than chosen after favorable outcomes.

No confidence interval for recovery controls is constructed here. An estimated point correction, nominal coverage without a justified sampling law, or a sensitivity radius chosen after seeing the result cannot establish the required bound. The input declaration records the assumption; `bound_validity_established_by_counts` is always false. Unbounded or missing intervals are refused. With no restriction on t>0 the supremum is 1: log-concavity puts a minimum reference weight at an endpoint, and exponential tilting can concentrate there.

Alpha remains a standalone allocation for this test. Adding it to a study's existing score comparisons, selecting contexts, changing the reference statistic, or taking repeated looks requires the corresponding prespecified study-level allocation. Nonrejection is compatibility under the declared model, not equality, equivalence or verification of recovery transfer.

## Mapping existing recovery bounds into t

For per-context rectangular bounds `L_ci<=rho_ci<=U_ci`, the same algebra used in methods 0.6.0 gives

```text
m_lo,c = L_cA²/(U_cW U_cM),
m_hi,c = U_cA²/(L_cW L_cM),
t in [m_lo,2/m_hi,1, m_hi,2/m_lo,1].
```

Separate context boxes can be conservative when a joint recovery mechanism couples them. If every phase ratio rho is bounded by [1/R,R], then t lies in `[R^-8,R^8]`. If each branch-specific recovery ratio to its reference is separately bounded by [1/R,R], its phase ratio is bounded by `[R^-2,R²]` and the corresponding exponent is 16. An identical recovery-curvature bias in both contexts cancels exactly, giving t=1 even when the full recovery maps differ.

The older transport package's e denotes **residual** recovery after fixed-route controls; it is not automatically the raw rho used here. If `rho=(d1/d0)*e`, the control curvature ratio must also enter t, with its uncertainty. Using only the residual box is justified only when the omitted control contrast ratio is exactly known to be one, or its full contribution has otherwise been validly included. The mapping algebra provides no empirical recovery measurements.

An interval excluding 1 is permitted: it can shift the sensitivity result below the zero-recovery reference p. Inclusion of 1 guarantees p_sup is at least that reference p; arbitrary intervals do not. Nested intervals give nondecreasing suprema, and increasing gamma gives nondecreasing adjusted p.

## Synthetic examples and reproduction

The small two-point example has context 1 baseline (0,4,0), selected (2,0,2), and context 2 baseline (2,0,2), selected (1,2,1). Its primitive weights are (24,1), the observed index is 1 and `p_ref(t)=t/(24+t)`. At alpha=1/20 and gamma=0, `[1,24/19]` gives exactly p=1/20 and rejects under the inclusive rule; `[1,4/3]` gives 1/19 and does not reject. Setting gamma=1/100 at point t=1 changes 1/25 to 1/20. This exact inclusive boundary differs from the older confidence-intersection rule, where touching intervals remain compatible.

The symmetric example has baseline/selected counts (0,4,0)/(2,0,2) in context 1 and (2,0,2)/(0,4,0) in context 2. Its weights are (1,576,1) and observed E={0,2}. Reference p=1/289; on [1/4,4] the exact supremum is 17/2321, attained at both endpoints. These hypothetical intervals are sensitivity scenarios, not calibrated empirical bounds.

The earlier synthetic baseline example is retained as `example_previous_baseline.json`: both baselines are (4,4,4), and selected counts are (6,0,6) and (0,12,0). Its reference p=875/755849 becomes 9625/189283, approximately 0.05085, on the hypothetical interval [1/33,33] with gamma=0. It therefore loses rejection at alpha=1/20. This is sensitivity to a declared interval, not a measured robustness radius.

```sh
python -B research/conditional_recovery/recovery_sensitivity.py research/conditional_recovery/example_two_point.json --include-fiber
python -B research/conditional_recovery/verify_recovery.py
```

The wrapper imports the existing conditional-curvature combinatorial helper and strict rational/JSON parsers. It does not feed a recovery-mismatched model to the original shared-offset validator. The current implementation admits exactly two contexts, at most 200 observations per arm and 800 total observations, at most 101 contiguous fiber weights, 256-bit rational input numerators/denominators, and at most 801-bit integer weights. Before evaluation, a conservative polynomial integer-size bound must be at most 12,000 bits; this leaves room for the 256-bit gamma adjustment under Python's default decimal-output limit. Consequently not every combination of the individual limits is accepted. The inherited Cartesian and storage guards also apply. These are arithmetic refusal limits, not recommended scientific sample sizes or full runtime guarantees. Invalid contracts, booleans/floats, malformed rational strings, duplicate JSON keys, nonstandard NaN/Infinity, or a failed structural certificate raise an error and leave the result uncomputed. There is no numerical optimizer, approximate tail, pseudocount, or automatic fallback to p=1.

Verification regenerates local receipts and example outputs; copy this directory to scratch when preserving an untouched checkout. The [independent review](INDEPENDENT_REVIEW.md) records the separate raw-multinomial enumeration and producer comparisons, with source and receipt hashes in `INDEPENDENT_HASHES.json`. The measurement bridge's offline verifier separately checks the exact classification counterexample and, when the external JATS file is supplied, its pinned identity and eight source anchors.

New code is MIT and original documentation CC BY 4.0 under the repository terms. Internal AI-assisted computational checks do not constitute external peer review or biological replication.
