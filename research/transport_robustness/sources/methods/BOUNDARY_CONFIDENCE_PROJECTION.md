# Boundary-safe simultaneous confidence projection (TMD 0.5.0)

This update supplies a conservative finite-sample confidence procedure for fixed-route binomial recovery controls, including observed zero and all-success cells. It does not solve the boundary joint likelihood, return a likelihood-ratio statistic or P value, provide a profile confidence interval, or establish a biological mechanism. It uses established binomial confidence inversion and Bonferroni coverage. Its advance relative to the local 0.4.0 software is a computable, boundary-compatible procedure with explicit mathematical and numerical guarantees.

## Count laws and scientific target

In context c, let b_c and t_c be the positive route probability vectors for observed baseline and selected samples, with routes W,A,M. The observed categorical count vectors have multinomial laws conditional on prespecified totals. Each route count is therefore marginally Binomial(total, corresponding probability), although counts within a sample are dependent.

For branch h=0,1 and route i, known positive introduced totals L_hci and recovered counts k_hci have marginal Binomial(L_hci,d_hci) laws. Units must support one binary recovery outcome, with the design and sampling assumptions needed for these binomial laws. Observations k=0 and k=L are permitted. Missing introduced totals, missing route keys, arbitrary fluctuation/colony summaries, and randomized-mixture recovery counts are not interchangeable with this design.

The model interpretation is b_ci proportional to q_ci times biological baseline recovery, and t_ci proportional to q_ci exp(theta_c I_A + eta_c s_i) times biological selected recovery, s=(1,0,-1). Positive control efficiencies d_hci transport to biological recovery up to a branch/context-wide unknown positive multiplier. Such multipliers cancel in route contrasts; fixed denominators identify absolute CONTROL recovery probabilities, not all absolute biological recovery probabilities or establishment rates. Route-dependent transport failure does not cancel and invalidates this interpretation. Population b,t and d must be strictly positive for a finite target; d=1 is permitted. An observed zero is not evidence that a population component is structurally zero.

With v=(-1/2,1,-1/2), v·1=v·s=0 and v·I_A=1, so

    theta_c = v·(log t_c − log b_c − log d_1c + log d_0c).

This is a recovery-corrected phenomenological route contrast. Its interpretation as the proposed selection parameter requires the model and relative transport assumptions. It does not identify a mutation mechanism.

## Marginal intervals and simultaneous coverage

For x successes in n trials and one-sided error tau, the ideal equal-tailed Clopper–Pearson interval is [l,u]. For x>0, l solves P_l(X>=x)=tau; for x<n, u solves P_u(X<=x)=tau. Set l=0 at x=0 and u=1 at x=n. When n=0, [0,1] is explicitly a no-observations interval. Each tail's noncoverage probability is at most tau; discreteness usually makes coverage greater than its nominal lower bound.

There are 12C components: three baseline route probabilities, three selected route probabilities, and six recovery probabilities per context. For a prespecified alpha, assign tau=alpha/(24C) exactly. The union bound gives simultaneous component coverage at least 1−alpha. Independence across these confidence events, across arms, or across contexts is not required for this bound. The individual binomial/multinomial marginal laws still must hold. A positive contract declaration is an input requirement and does not verify those laws.

The guarantee is for a fixed collection of contexts and prespecified sample sizes/analysis. It does not by itself justify repeated looks, selection of reported contexts after examining data, adaptively stopping when a rejection appears, clustered-unit binomial approximations, or invalid denominator definitions.

## Exact rational projection and shared-contrast rule

Let J_c=exp(2theta_c)>0. Then

    J_c = (t_A² b_W b_M d_1W d_1M d_0A²)
          / (t_W t_M b_A² d_1A² d_0W d_0M).

Because this expression increases in each numerator component and decreases in each denominator component, a valid outer interval follows from lower numerator/upper denominator endpoints for J_lower and upper numerator/lower denominator endpoints for J_upper. Any zero numerator lower bound yields J_lower=0, equivalent to theta_lower=−infinity. Any zero denominator lower bound yields J_upper=+infinity. The enclosing rectangular set intentionally ignores additional simplex restrictions and dependence, making the projection conservative. This is not a likelihood confidence region.

Under simultaneous component coverage, every true J_c lies within its projected interval. If all contexts have a common theta, they have a common J, so their intervals must intersect on that coverage event. Reject the shared-contrast null only when

    max_c J_lower,c > min_c J_upper,c.

Consequently, under the valid marginal models, relative transport, and a common finite contrast, rejection probability is at most alpha. A touching intersection is nonempty and is not rejected. Failure to reject does not demonstrate equality or equivalence, especially when intervals are unbounded. One context supplies only a descriptive interval and no between-context test. The API returns `not_evaluable_one_context` for C=1. No P value is produced.

## Numerical guarantee and supported domain

Floating-point log-sum binomial tails and safeguarded bisection propose each nontrivial endpoint. A small deliberate outward displacement is attempted, starting with max(16 ulps, 1e−10 p(1−p)), expanding when needed. These returned dyadic endpoints are certified conservative OUTER APPROXIMATIONS to the nominal Clopper–Pearson roots; they need not equal those roots. Failed proposals may be widened to the support boundary, sacrificing information rather than claiming an uncertified bound.

For a binary floating endpoint p=U/D, its binomial tail is represented exactly by an integer numerator and denominator D^n. Positive terms recur with exact integer division, and complementing a shorter tail is also exact. Integer cross multiplication compares the tail with the exact rational tau. A lower endpoint is accepted only if its increasing upper tail is at most tau; an upper endpoint only if its decreasing lower tail is at most tau. Thus numerical proposal error cannot narrow an accepted interval past its nominal root. Python arbitrary-precision integers make the endpoint certificate exact, within the supported domain.

Projected J endpoints and their intersection comparisons use exact Fraction arithmetic on these certified dyadic bounds. Therefore logarithm rounding cannot create a rejection. Displayed theta bounds enclose log(J)/2 using a directed rational-to-Decimal enclosure, correctly rounded Decimal logarithm followed by an adjacent Decimal outward step, directed division, and a final outward float step. These display values are not the decision basis. Raw NaN/Infinity are forbidden in JSON: infinite endpoints have `value:null` and `infinity:"negative"` or `"positive"`. Exact J endpoints are rational strings; an unbounded upper endpoint is null with an explicit positive-infinity field.

The prototype explicitly limits each categorical total and control denominator to 5,000, contexts to 64, and alpha to [1e−12,1). Unsupported domains are declined rather than approximated silently. Very small samples, zero counts, and the stricter Bonferroni allocation can yield broad intervals. Numerical certification does not authenticate biological transport, sampling laws or data provenance.

## Input contract, reproducibility, and tests

The strict JSON contract requires explicit W,A,M route dictionaries, baseline/selected branch order, unique context names, known positive introduced totals, observed recovered values, provenance, an exposed-unit definition, a locked winner-observation rule, validated common-background triad calibration, positive population log components, and justified categorical and fixed-route binomial marginal laws. Previously imposed joint-fit independence is not needed by this union-bound procedure; valid unit-level count laws are required. Measured zeros are retained. Missing values never become zeros. A zero categorical total is supported as no observations, yielding [0,1] component bounds and an uninformative contrast.

`inference/boundary_confidence.py` is a Python standard-library implementation with no numerical optimizer. Its source and count topology lineage are documented in `inference/VERSION_LINEAGE.md` and MIT LICENSE. `inference/test_boundary_confidence.py` checks independently enumerated exact tails, all x for n=1..10 at three allocations and 21 rational population probabilities (630 exact coverage checks), endpoint identities, all-success controls, observed failures and no-data behavior, malformed input, exact projection signs, display enclosures, and a shared-null experiment with maximally dependent components but valid marginal laws. A deliberately incorrect root proposal must still return certified outer intervals.

Six deterministic synthetic fixtures and their hashed results illustrate all-success controls, a strong contrast departure that remains distinguishable, observed failures, zero categorical cells, no categorical observations, and a single descriptive context. The all-success fixtures use finite positive observed categorical proportions and k=L=100 controls; their intervals remain finite. They are arithmetic examples, not biological evidence, mechanism validation, or a repeated-sample power estimate. The separate calibration directory reports a limited repeated-sample synthetic study.

At alpha=0.05 with two contexts, the deterministic all-success/null fixture yields theta intervals approximately [−0.858894,0.858894] in both contexts. The strong-departure fixture yields that interval in context 1 and [2.717251,5.180998] in context 2, so the exact J intervals are disjoint and the shared contrast is rejected. All-failure controls and explicit zero baseline sample totals yield [−infinity,+infinity] and no established departure. A selected sample with observed counts (0,600,0) can yield a one-sided unbounded interval [3.966368,+infinity] that is still disjoint from the other context; unbounded does not automatically mean that a comparison has no information. No pseudocount is introduced in any case.
