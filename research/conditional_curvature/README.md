# Conditional tests of a shared curvature restriction

Original design analysis · 5 November 2026 · AI-assisted, internal computational review only

This bounded standard-library implementation tests whether conditional W/A/M outcome distributions share a curvature parameter across contexts. It addresses a different question from superiority of frozen prediction algorithms. Neither rejection nor nonrejection identifies a mutation mechanism; nonrejection does not establish equality, equivalence or a biologically adequate model. All examples and operating checks here are synthetic. No registry, forecast, comparator, error allocation, stopping rule or released method is changed.

Two observation contracts are supported. The reference version treats positive offsets as exactly known. The second uses independent baseline counts and conditions away an unknown offset shared by the two observed assay laws within each context. It does not substitute estimated recovery controls for known offsets or establish biological transfer.

The companion [conditional design analysis](../conditional_design/README.md) now computes support geometry, retained information and complete small-budget rejection probabilities. It separates those planning quantities from biological power and leaves these test definitions unchanged.

## Relationship to prior project methods

The prospective design already states the positive-triad restriction and notes that conditioning on each context's total and W–M difference removes its tilt. Published methods 0.5.0/0.6.0 already test a common recovery-corrected contrast by intersection of simultaneous confidence intervals, propagating baseline/control uncertainty and optional recovery-transfer bounds. The certified score engine instead compares realized expected log scores of frozen forecasts. Existing paired-aliquot exact calculations address allocation quality under their own count laws.

This implementation adds an explicitly computable conditional probability-ordering test and matched-baseline nuisance elimination. It is a narrower observation-model option, not the first common-curvature test in the project or a replacement for existing forecast and uncertainty procedures. The mathematics is standard exponential-family conditioning and exact finite probability ordering; no new theorem or priority claim is made.

Relevant existing documentation: `research/prospective_design/README.md`, its `review/REVIEW_NOTES.md`, `research/transport_robustness/sources/methods/BOUNDARY_CONFIDENCE_PROJECTION.md`, `research/certified_score/README.md`, and `research/operating_characteristics/README.md`.

## Known positive offsets

Assume a joint product of context-specific multinomial laws, conditional on prespecified totals. In context c, selected counts X_c=(W_c,A_c,M_c) have total N_c. For positive known q_c and finite parameters, the null is

```text
p_ci = q_ci exp(theta 1[i=A] + eta_c s_i) / Z_c,
s = (1,0,-1),     theta common across contexts.
```

Define D_c=W_c−M_c and A_total=sum_c A_c. Conditional on every N_c,D_c and A_total, all eta_c factors and the common theta factor are constant. The support consists of allocations satisfying

```text
w_c=(N_c−a_c+D_c)/2,     m_c=(N_c−a_c−D_c)/2,
0 <= a_c <= N_c−|D_c|,
a_c congruent to N_c−D_c modulo 2,     sum_c a_c=A_total.
```

An allocation's unnormalized conditional probability is

```text
B(a) = product_c q_cW^w_c q_cA^a_c q_cM^m_c / (w_c! a_c! m_c!).
```

The context-specific N_c! constants cancel. The code enumerates exactly this support, retaining parity, observed zeros and exact probability ties. It uses integers and Fraction arithmetic without pseudocounts. Structural zeros in q are outside the finite positive-parameter contract.

Writing a_c=epsilon_c+2k_c shows that the law depends on q only through relative curvature offsets kappa_c=q_cA²/(q_cW q_cM): B is proportional to product kappa_c^k_c/(w_c!a_c!m_c!). A common multiplicative factor applied to all kappa_c cancels because sum k_c is fixed. This algebra does not authenticate equality of unknown offsets or turn separately estimated offsets into known ones. The reference API deliberately requires complete positive rational q vectors summing exactly to one. Rational approximations to unknown or irrational q define different numerical nulls and do not inherit exactness for the original q.

## Unknown offsets with independent baseline counts

Independently observe K_c~Mult(B_c,q_c) and X_c~Mult(N_c,p_c), with p_c following the same model above and unknown positive q_c. Require the joint product law across arms and contexts. Baseline q_c can differ between contexts, but the same q_c must enter both arms within a context.

Condition additionally on each pooled route vector T_ci=K_ci+X_ci. Up to fixed multinomial factorials, the joint likelihood contains

```text
product_ci q_ci^T_ci / (K_ci! X_ci!)
    * exp(theta A_total) * product_c [exp(eta_c D_c) / Z_c^N_c].
```

All q, eta and common theta terms are then constant. The admissible allocations have the same selected N,D,parity,total-A conditions, together with 0<=X_ci<=T_ci and K_ci=T_ci−X_ci. Their unnormalized weights are

```text
B_baseline(a) = product_ci binom(T_ci, X_ci(a)).
```

The fixed baseline total follows from the pooled total and fixed selected total. This engine uses integer weights and never estimates q. Sample pooled zeros restrict the support; they are not declared population structural zeros.

This tests equal observed-frame contrast relative to a genuinely shared within-context baseline offset. Unknown route-dependent differential recovery can alter that contrast. The code does not include recovery controls, estimate a recovery map, or justify the shared-offset contract. A smoothed qstar assembled from baseline and recovery-control estimates cannot automatically replace this joint assay model. Correlated paired arms or descendant clusters do not satisfy the stipulated independent product law merely by having valid marginal counts.

For example, if route-specific inclusion probabilities are r0 in baseline and r1 in selected observations, the observed curvature is

```text
theta_observed,c = theta_biological,c
    + log[(r1_A/r0_A) / sqrt((r1_W/r0_W)(r1_M/r0_M))].
```

Interpreting observed common curvature as biological common curvature requires that differential-recovery contrast to be constant across contexts, or a justified known correction. Complete equality of the recovery maps is sufficient but stronger than necessary; independently estimated recovery contrasts still carry uncertainty.

## Probability ordering, degeneracy and interpretation

For either finite conditional law, the inclusive probability-ordering tail is

```text
p_exact(a_observed) = sum_{a:B(a)<=B(a_observed)} B(a) / sum_a B(a).
```

All equal-probability allocations are included. There is no floating tie tolerance, mid-P correction or Monte Carlo approximation. Ordered probability masses and their inclusive cumulative sums give Pr(p_exact<=alpha | conditioning statistics)<=alpha. Averaging over the conditioning statistics preserves that bound under the stipulated joint null. This finite nonrandomized guarantee does not mean rejection probability equals alpha. Other conditional statistics may yield different valid tests and different power; no optimality claim is made.

One context, extreme selected W–M differences, or extreme total A can produce a singleton fiber. The code returns p=1 and `uninformative_singleton_fiber`. It also reports the minimum attainable p and whether any allocation on the current fiber can reject at the supplied alpha. A nontrivial fiber can remain too discrete to reject. Without baseline observations the second mode is uninformative. Indeed baseline total below two permits no change in selected A while preserving selected N,D, so it allows no within-context movement under this conditioning.

The test conditions away common theta and all tilts; it does not estimate them, test theta=0 or the numerical theta learned in training, test the frozen tilt regression, forecast a full new triad or measure incremental predictive gain. Rejection concerns the combined shared-curvature and observation/sampling model. An observation-contract failure can mimic heterogeneity. Other, no-qualified-outcome, unresolved and missing categories still require their full ledgers; this conditional-triad calculation cannot establish an all-category result.

Contexts, eligibility, count laws, analysis rule, alpha and stopping must be fixed before the relevant outcomes for confirmatory use. The joint independence requirement is stronger than the marginal-law assumptions of the existing Bonferroni confidence procedure. These tools do not authorize adaptive context selection, repeated unadjusted looks or post-outcome replacement of the frozen score criterion.

The supplied alpha is a standalone allocation for this test. Adding it to a study's existing score comparisons is not covered by their simultaneous confidence-region guarantee; a prespecified study-level error allocation is required. The examples' alpha=1/20 is illustrative and changes no frozen study criterion.

## Independent point calibration is insufficient

Take two contexts with true q=(1/3,1/3,1/3), theta=eta=0, and five independent selected observations each. Estimate each q from one independent baseline draw using the existing Jeffreys prediction convention. Each estimate is a permutation of (3,1,1)/5. If it is incorrectly supplied as exactly known q, the nominal alpha=1/20 conditional test rejects with exact unconditional probability

```text
30620/531441 = approximately 0.0576169321 > 0.05.
```

This sums all nine calibration outcomes and all 441 selected count-table pairs; it is not a Monte Carlo estimate. Equal estimated curvature occurs with probability 5/9 and differing estimated curvature with probability 4/9. Their respective conditional-on-calibration rejection probabilities are 20/19683 and 7580/59049. Independent calibration does not remove nuisance uncertainty. The known-offset contract rejects an `independently_estimated` declaration; the counterexample intentionally misdeclares estimates to show why a declaration cannot authenticate the assumption.

The properly conditioned baseline mode has no information in that one-baseline-observation example: all 3,969 joint tables have singleton fibers and p=1. Avoiding the plug-in error can cost substantial information. Larger complete synthetic null enumerations illustrate discreteness, not recommended sample sizes or biological power:

| Baseline total per context | Selected total per context | Complete joint tables | Informative fibers | Exact null rejection probability at 1/20 |
| --- | --- | ---: | ---: | --- |
| 1 | 5 | 3,969 | 0 of 3,969 | 0 |
| 3 | 3 | 10,000 | 81 of 9,919 | 8/59049 |
| 4 | 4 | 50,625 | 1,295 of 49,329 | 16888/14348907 |

These rows use two contexts, uniform baseline laws and theta=eta=0. Their low null rejection probabilities do not quantify alternative power. Separate heterogeneous-q/nonzero-tilt null enumerations verify nuisance cancellation. A synthetic extreme table gives known-offset p=1/298552 and matched-baseline p=875/755849; these are results for their declared finite examples only.

## Bounded implementation and reproduction

Each mode accepts at most eight contexts, 200 observations per arm, 800 observations across included arms, and 100,000 Cartesian candidate allocations. Known-offset rationals are limited to 256-bit numerators/denominators. A combined candidate-count/weight-bit guard declines excessive exact arithmetic before constructing local weights. Its 64 Mi-bit limit includes a conservative bookkeeping allowance, but is not a comprehensive runtime or memory guarantee. These are implementation limits, not scientific design choices. An exhausted bound raises an error and leaves the result uncomputed; it never returns p=1 or substitutes an approximation.

Inputs reject booleans as counts or rationals, floats, decimal strings, nonpositive or nonnormalized known q, duplicate context IDs, unknown contract values, duplicate JSON keys and nonstandard JSON NaN/Infinity. Contracts are declarations, not evidence that the laws hold.

```sh
python -B conditional_homogeneity.py example_known.json --include-fiber
python -B baseline_conditional_homogeneity.py example_baseline.json --include-fiber
python -B verify_conditional.py
python -B independent_oracle.py
```

`VERIFICATION.json` records complete producer finite-law checks, malformed-input checks, the exact plug-in counterexample, examples and source hashes. The independent oracle uses raw joint multinomial masses, compares full conditional distributions and P values, and checks every attainable conditional threshold in its enumerated nulls. Its receipt and hash file record its own executed checks and final sources. This is internal AI-assisted computational review, not external peer review, biological replication or study registration.

The verification scripts regenerate receipts and example results beside themselves. Copy this directory to a scratch location before running them if preserving an untouched checkout.

New code is MIT and original documentation CC BY 4.0 under the repository terms. No third-party code is copied. The released methods 0.6.0 archive and unresolved actual-study fields remain unchanged.
